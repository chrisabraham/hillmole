"""Generate the Jekyll source for hillmole.com from the extracted MT data.

Reads ~/hillmole-source/work/entries.json (from extract.py) and the old
webroot, and writes into the repo:

  _posts/            one .html file per published entry, body byte-for-byte
  _drafts/           unpublished entries (gitignored)
  _mtarchives/       stub pages for MT's monthly/weekly/daily/category URLs
  archives/N.xml     per-entry TrackBack feeds, spam items removed
  images/ podcast/ and other static files, paths preserved
  archives/YYYY/...  deleted entries' old pages, kept verbatim at Chris' request
  attic/             MT templates, mt.cgi and config, secrets stripped

Safe to re-run; generated directories are rebuilt from scratch.
Usage: python3 _migration/build_site.py
"""
import datetime as dt
import glob
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
import mysqldump as md  # noqa: E402
from extract import convert_breaks, repair  # noqa: E402

HOME = os.path.expanduser("~")
SRC = glob.glob(f"{HOME}/hillmole-source/backup-*/")[0]
WEB = SRC + "homedir/public_html"
WORK = f"{HOME}/hillmole-source/work"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def q(s):
    """YAML-safe double-quoted scalar."""
    return json.dumps(s, ensure_ascii=False)


def entry_path(e):
    return f"/archives/{e['created_on'][:4]}/{e['created_on'][5:7]}/{e['basename']}.html"


def reset(d):
    shutil.rmtree(f"{REPO}/{d}", ignore_errors=True)
    os.makedirs(f"{REPO}/{d}")


def recover_categories():
    """mt_category is empty in the dump; recover membership from the HTML."""
    cats = {}
    for p in sorted(glob.glob(f"{WEB}/archives/*/index.html")):
        slug = p.split("/")[-2]
        if slug.isdigit():
            continue
        h = open(p, encoding="utf-8").read()
        label = re.search(r"<title>Hill Mole: (.*?) Archives</title>", h).group(1)
        ids = [int(x) for x in re.findall(r'<h3 id="a0*(\d+)"', h)]
        cats[slug] = {"label": repair(label), "ids": ids}
    return cats


def write_post(e, cats, dest):
    labels = [c["label"] for c in cats.values() if e["mt_id"] in c["ids"]]
    fm = [
        "---",
        f"title: {q(e['title'])}",
        f"date: {e['created_on']} -0500",
        f"permalink: {entry_path(e)}",
        f"categories: {q(labels)}",
        f"mt_basename: {e['basename']}",
        f"mt_id: {e['mt_id']}",
    ]
    if e["excerpt"]:
        fm.append(f"description: {q(e['excerpt'])}")
    if e["keywords"]:
        fm.append(f"keywords: {q(e['keywords'])}")
    fm.append("---")
    body = convert_breaks(e["text"])
    if e["text_more"]:
        body += "\n\n" + convert_breaks(e["text_more"])
    name = f"{e['created_on'][:10]}-{e['basename']}.html"
    with open(f"{REPO}/{dest}/{name}", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(fm) + "\n" + body + "\n")


def fmt_day(d):
    return f"{d:%B} {d.day}, {d.year}"


def archive_pages(pub, cats):
    """Every MT archive URL: monthly, weekly (Sunday start), daily, category."""
    days = sorted({dt.date.fromisoformat(e["created_on"][:10]) for e in pub})
    groups = {"monthly": {}, "weekly": {}, "daily": {}}
    for d in days:
        m0 = d.replace(day=1)
        m1 = (m0 + dt.timedelta(days=32)).replace(day=1) - dt.timedelta(days=1)
        groups["monthly"][m0] = (f"/archives/{d:%Y/%m}/", f"{d:%B %Y}", m0, m1)
        w0 = d - dt.timedelta(days=(d.weekday() + 1) % 7)
        w1 = w0 + dt.timedelta(days=6)
        groups["weekly"][w0] = (f"/archives/{w0:%Y/%m/%d}-week/",
                                f"{fmt_day(w0)} - {fmt_day(w1)}", w0, w1)
        groups["daily"][d] = (f"/archives/{d:%Y/%m/%d}/", fmt_day(d), d, d)
    pages = []
    for kind, g in groups.items():
        items = [g[k] for k in sorted(g)]
        for i, (url, label, a, b) in enumerate(items):
            p = {"layout": "archive", "archive_type": kind, "title": label,
                 "permalink": url, "from": a.isoformat(), "to": b.isoformat()}
            if kind in ("daily", "weekly"):
                # Same entries as the monthly page; keep the URL, keep it out of search.
                p["robots"], p["sitemap"] = "noindex, follow", False
            if i > 0:
                p["prev_url"], p["prev_title"] = items[i - 1][:2]
            if i + 1 < len(items):
                p["next_url"], p["next_title"] = items[i + 1][:2]
            pages.append(p)
    pub_ids = {e["mt_id"] for e in pub}
    for slug, c in cats.items():
        if not pub_ids & set(c["ids"]):
            continue  # lists only deleted entries; old page is kept verbatim instead
        pages.append({"layout": "archive", "archive_type": "category",
                      "title": c["label"], "permalink": f"/archives/{slug}/",
                      "category": c["label"]})
    return pages


def write_archives(pages):
    reset("_mtarchives")
    for p in pages:
        name = p["permalink"].strip("/").replace("/", "-") + ".html"
        lines = ["---"] + [f"{k}: {q(v)}" for k, v in p.items()] + ["---", ""]
        open(f"{REPO}/_mtarchives/{name}", "w", encoding="utf-8").write("\n".join(lines))


# Orphaned entry pages MT left on disk after an entry was renamed, emptied,
# or deleted. Renamed ones point at the current entry; empty shells go home.
# Deleted entries with real text are not listed here: that's Chris' call.
ORPHAN_REDIRECTS = {
    "/archives/2021/01/post.html": "/archives/2021/01/metanoia.html",
    "/archives/2021/07/the_only_reason.html":
        "/archives/2021/07/the_only_reason_to_go_offworld_is_for_sick_remittance_money.html",
    "/archives/2021/07/the_only_reason_1.html":
        "/archives/2021/07/the_only_reason_to_go_offworld_is_for_sick_remittance_money.html",
    "/archives/2005/05/i_suspect_every.html": "/",
    "/archives/2008/02/test.html": "/",
    "/archives/2019/08/all_the_old_men.html": "/",
}

# Entries deleted from MT whose pages still had text. Chris wants them kept,
# so they're served exactly as MT last wrote them, old styling and all.
KEEP_ORPHANS = [
    "archives/2008/05/princey_lovey_b.html",
    "archives/2008/05/upon_meeting_my.html",
    "archives/2022/10/theres_no_busin.html",
    "archives/2023/02/chatgpt_rewrite.html",
    "archives/2023/05/a_hill_mole_sho.html",
    "archives/2023/05/a_hill_mole_sho_1.html",
    "archives/2023/05/a_short_story_f.html",
    "archives/2023/05/bard_turns_hill.html",
    "archives/2023/05/excerpt_of_the.html",
    "archives/2023/05/hill_mole_accor.html",
    "archives/2023/05/the_mole_a_nove.html",
]


def keep_orphan_page(rel):
    """True if an old date page lists only kept orphans; it's then served verbatim."""
    h = open(f"{WEB}/{rel}", encoding="utf-8", errors="replace").read()
    links = set(re.findall(r'<h3 id="a\d+"><a href="https?://[^/]+/([^"]+)"', h))
    is_category = not re.match(r"archives/\d{4}/", rel)  # categories may be empty on the old site
    return (bool(links) or is_category) and links <= set(KEEP_ORPHANS)


def copy_kept_orphans():
    """Copy kept orphan entries, and date pages listing only them, byte-for-byte."""
    pages = [os.path.relpath(p, WEB) for p in
             glob.glob(f"{WEB}/archives/[0-9]*/[0-9]*/**/index.html", recursive=True)
             + glob.glob(f"{WEB}/archives/[0-9]*/[0-9]*/index.html")]
    pages += [os.path.relpath(p, WEB) for p in glob.glob(f"{WEB}/archives/*/index.html")]
    kept = list(KEEP_ORPHANS) + [p for p in sorted(set(pages)) if keep_orphan_page(p)]
    for rel in kept:
        os.makedirs(os.path.dirname(f"{REPO}/{rel}"), exist_ok=True)
        shutil.copyfile(f"{WEB}/{rel}", f"{REPO}/{rel}")
        os.chmod(f"{REPO}/{rel}", 0o644)
    return kept


def redirect_pages(pages):
    """Old date-archive pages for entries that moved or were deleted."""
    have = {p["permalink"] for p in pages}
    out = [{"permalink": old, "redirect_to": new, "sitemap": False}
           for old, new in ORPHAN_REDIRECTS.items()]
    for p in sorted(glob.glob(f"{WEB}/archives/[0-9]*/[0-9]*/**/index.html", recursive=True)
                    + glob.glob(f"{WEB}/archives/[0-9]*/[0-9]*/index.html")):
        url = "/" + os.path.relpath(os.path.dirname(p), WEB) + "/"
        if url in have or keep_orphan_page(os.path.relpath(p, WEB)):
            continue
        month = "/".join(url.split("/")[:4]) + "/"
        out.append({"permalink": url, "redirect_to": month if month in have else "/archives.html",
                    "sitemap": False})
        have.add(url)
    return out


def write_trackback_feeds():
    """archives/N.xml held only spam pings; keep the URL, drop the <item>s."""
    os.makedirs(f"{REPO}/archives", exist_ok=True)
    for p in glob.glob(f"{WEB}/archives/*.xml"):
        x = open(p, "rb").read()  # spam pings are in mixed encodings; work in bytes
        x = re.sub(rb"<item>.*?</item>\s*", b"", x, flags=re.S)
        open(f"{REPO}/archives/{os.path.basename(p)}", "wb").write(x)


# Served verbatim. default.html, postinfo.html and styles.css are host/install
# leftovers, kept only so their old URLs still answer.
STATIC = ["images", "podcast", "hillMoleiTunes.gif", "nav-commenters.gif", "favicon.ico",
          "styles-site.css", "styles.css", "GOOGLEe028701e4dbb21d7.html",
          "googlee028701e4dbb21d7.html", "test.htm", "default.html", "postinfo.html"]


def copy_static():
    for s in STATIC:
        src, dst = f"{WEB}/{s}", f"{REPO}/{s}"
        if os.path.isdir(src):
            shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(src, dst)
            for root, dirs, files in os.walk(dst):
                os.chmod(root, 0o755)
                for f in files:
                    os.chmod(os.path.join(root, f), 0o644)
        else:
            shutil.copyfile(src, dst)
            os.chmod(dst, 0o644)


SECRET = re.compile(r"^(\s*(?:DBPassword|DBUser|DBHost|Database)\s+).*$", re.M | re.I)


def write_attic():
    reset("attic")
    os.makedirs(f"{REPO}/attic/templates")
    dump = open(glob.glob(f"{SRC}mysql/*_hillmole.sql")[0], "rb").read()
    for t in md.rows(dump, "mt_template"):
        name = re.sub(r"[^A-Za-z0-9]+", "-", t["template_name"]).strip("-").lower()
        open(f"{REPO}/attic/templates/{name}.tmpl", "w", encoding="utf-8").write(
            repair(t["template_text"] or ""))
    for f in ("mt.cgi", "mt-config.cgi", "mt.cfg"):
        text = open(f"{WEB}/{f}", encoding="latin-1").read()
        text = SECRET.sub(lambda m: m.group(1) + "REMOVED", text)
        open(f"{REPO}/attic/{f}", "w", encoding="latin-1").write(text)


def main():
    entries = json.load(open(f"{WORK}/entries.json"))
    cats = recover_categories()
    pub = [e for e in entries if e["status"] == "published"]
    drafts = [e for e in entries if e["status"] == "draft"]
    reset("_posts")
    reset("_drafts")
    for e in pub:
        write_post(e, cats, "_posts")
    for e in drafts:
        write_post(e, cats, "_drafts")
    pages = archive_pages(pub, cats)
    write_archives(pages + redirect_pages(pages))
    write_trackback_feeds()
    kept = copy_kept_orphans()
    copy_static()
    write_attic()
    print(f"{len(pub)} posts, {len(drafts)} drafts, {len(cats)} categories, "
          f"{len(kept)} old pages kept verbatim")


if __name__ == "__main__":
    main()
