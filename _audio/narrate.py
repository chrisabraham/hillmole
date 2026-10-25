#!/usr/bin/env python3
"""Narrate every Hill Mole chapter with the built-in tts (free only).

    python3 _audio/narrate.py [--limit N] [--only basename,...] [--workers N]

The audio edition of Hill Mole (Chris' ruling, Oct 25 2026): every chapter
read aloud in the male voice "Weighty Bell" (avocado_v2:qvd_02406, the same
voice that reads Chris on thechrisabrahamshow.com), from the built-in tts
only — no paid API, ever. One voice constant: change CHAPTER_VOICE and every
narration whose hash covers it is re-rendered on the next run.

What a run does:
  * Reads _posts/*.html, orders chapters by their timestamps (the order the
    site itself numbers them by; verified against the live bylines), and
    writes each chapter's clean spoken text to _audio/text/<basename>.txt,
    keyed to its MP3 for re-rendering.
  * Synthesizes the missing or changed chapters to assets/audio/<basename>.mp3
    (sha256 of voice + title + text in _audio/manifest.json decides "changed").
    Chapters are narrated in chapter order within each worker batch; the
    manifest is the queue — a chapter with no entry and no MP3 is still owed,
    and re-running picks it up. Failures are reported, never hidden.
  * Regenerates _data/audio.yml (what the layouts read to place a player)
    and audio.xml (the chapters as a podcast feed: full text in
    content:encoded, MP3 enclosures, itunes:episode = chapter number).

The MP3s are binaries: they cannot ride the UTF-8 push-files route. They are
staged under assets/audio/ and reach the repo by the browser-upload route;
everything else this tool writes is text and pushes normally. On machines
without the tts tool this script still regenerates the data file and the
feed from whatever MP3s are present, and reports what is owed.
"""

import argparse
import concurrent.futures
import datetime
import email.utils
import hashlib
import html
import json
import os
import re
import subprocess
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, "_posts")
AUDIO_DIR = os.path.join(ROOT, "assets", "audio")
WORK = os.path.join(ROOT, "_audio")
TEXT_DIR = os.path.join(WORK, "text")
MANIFEST = os.path.join(WORK, "manifest.json")
DATA_YML = os.path.join(ROOT, "_data", "audio.yml")
FEED_PATH = os.path.join(ROOT, "audio.xml")
SITE = "https://hillmole.com"
AUTHOR = "Chris Abraham"
OWNER_EMAIL = "cja@well.com"  # the owner email already published on Chris' feeds
CHAPTER_VOICE = "avocado_v2:qvd_02406"  # "Weighty Bell"
TTS_BIN = os.environ.get("HILLMOLE_TTS", "/opt/hatch/bin/tts")
FEED_GUID = "b7e2c41a-58d3-4f6e-9a21-0c5d8e7f3b19"  # audio.xml's own Podcast Index GUID; never changes
FEED_TITLE = "Hill Mole — The Audio Edition"


def load_posts():
    posts = []
    for name in sorted(os.listdir(POSTS)):
        if not name.endswith(".html"):
            continue
        raw = open(os.path.join(POSTS, name), encoding="utf-8").read()
        _, fm, body = raw.split("---", 2)
        meta = yaml.safe_load(fm)
        date = meta["date"]
        if isinstance(date, str):  # some front matter quotes the date
            date = datetime.datetime.strptime(date.strip(), "%Y-%m-%d %H:%M:%S %z")
        elif isinstance(date, datetime.date) and not isinstance(date, datetime.datetime):
            date = datetime.datetime(date.year, date.month, date.day,
                                     tzinfo=datetime.timezone(datetime.timedelta(hours=-5)))
        posts.append({
            "file": name,
            "title": str(meta["title"]),
            "date": date,
            "permalink": str(meta["permalink"]),
            "basename": str(meta["mt_basename"]),
            "description": str(meta.get("description") or ""),
            "body": body.strip(),
        })
    posts.sort(key=lambda p: p["date"])
    for i, p in enumerate(posts, 1):
        p["chapter"] = i
    assert len({p["basename"] for p in posts}) == len(posts), "mt_basename not unique"
    return posts


# Spoken-text substitutions: words the English voice cannot say as printed.
# The printed text never changes; only the narration's clean text does.
SPOKEN = [
    ("μετάνοια", "metanoia"),  # ch 196 is about the word; it gives this transliteration itself
]


def chapter_text(body_html):
    """The chapter as clean spoken text, mirroring the Show site's article
    extractor, plus one Hill Mole rule: the 2006 [Listen] links are apparatus,
    not prose, so anchors that say 'Listen...' are dropped whole."""
    h = re.sub(r'\s*\[?\s*<a\b[^>]*>\s*\[?Listen[^<]*</a>\s*\]?', "", body_html)
    h = re.sub(r"<br\s*/?>", "\n", h)
    h = re.sub(r"</(p|h2|h3|h4|li|blockquote|figure|figcaption|ul|ol)>", "\n\n", h)
    h = re.sub(r"<[^>]+>", "", h)
    h = html.unescape(h)
    paras = [re.sub(r"\s+", " ", p).strip() for p in h.split("\n\n")]
    text = "\n\n".join(p for p in paras if p)
    for printed, spoken in SPOKEN:
        text = text.replace(printed, spoken)
    return text


def script_for(post, text):
    title = post["title"]
    for printed, spoken in SPOKEN:
        title = title.replace(printed, spoken)
    lines = ["Narrator: Chapter %d. %s.\n" % (post["chapter"], title.rstrip("."))]
    lines += ["Narrator: %s\n" % p for p in text.split("\n\n") if p.strip()]
    return "".join(lines)


def duration_of(mp3):
    try:
        out = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                              "-of", "json", mp3], capture_output=True, text=True, timeout=60)
        return float(json.loads(out.stdout)["format"]["duration"])
    except Exception:
        return None


def narrate(post, text, digest):
    """Synthesize one chapter. Returns (basename, manifest entry) or
    (basename, None) with the failure printed."""
    slug = post["basename"]
    mp3 = os.path.join(AUDIO_DIR, slug + ".mp3")
    txt_path = os.path.join(TEXT_DIR, slug + ".txt")
    script = script_for(post, text)
    if not os.path.exists(txt_path) or open(txt_path, encoding="utf-8").read() != script:
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(script)
    try:
        out = subprocess.run([TTS_BIN, "synthesize-script", "--script", txt_path,
                              "--speaker", "Narrator=" + CHAPTER_VOICE, "--output", mp3],
                             capture_output=True, text=True, timeout=1200)
        result = json.loads(out.stdout[out.stdout.index("{"):])
        if not result.get("ok") or not os.path.exists(mp3):
            raise RuntimeError((out.stdout + out.stderr)[-300:])
    except Exception as err:
        print("  FAILED ch %d %s: %s" % (post["chapter"], slug, err), file=sys.stderr, flush=True)
        return slug, None
    entry = {"sha256": digest, "voice": CHAPTER_VOICE, "bytes": os.path.getsize(mp3),
             "duration": duration_of(mp3), "chapter": post["chapter"], "title": post["title"]}
    print("  narrated ch %d: %s (%d bytes)" % (post["chapter"], slug, entry["bytes"]), flush=True)
    return slug, entry


def cdata(s):
    return "<![CDATA[%s]]>" % (s or "").replace("]]>", "]]]]><![CDATA[>")


def esc(s):
    return html.escape(str(s), quote=True)


def iso_duration(secs):
    secs = int(round(secs))
    h, rem = divmod(secs, 3600)
    m, s = divmod(rem, 60)
    return "%d:%02d:%02d" % (h, m, s) if h else "%d:%02d" % (m, s)


def write_feed(posts, manifest):
    """audio.xml: the chapters as a listening series (the Mises model:
    the writing as its own feed). Newest first per podcast convention;
    itunes:episode carries the chapter number so apps can order the story,
    and full text rides in content:encoded."""
    done = [p for p in posts if p["basename"] in manifest
            and os.path.exists(os.path.join(AUDIO_DIR, p["basename"] + ".mp3"))]
    items = []
    for p in reversed(done):
        slug = p["basename"]
        url = SITE + p["permalink"]
        body = re.sub(r'((?:href|src)="/)(?!/)', r"\1" + SITE + "/", p["body"])
        entry = manifest[slug]
        x = ["<item>",
             "<title>%s</title>" % esc("Chapter %d: %s" % (p["chapter"], p["title"])),
             "<link>%s</link>" % url,
             '<guid isPermaLink="true">%s</guid>' % url,
             "<pubDate>%s</pubDate>" % email.utils.format_datetime(
                 p["date"].astimezone(datetime.timezone.utc), usegmt=True),
             "<dc:creator>%s</dc:creator>" % esc(AUTHOR),
             "<description>%s</description>" % esc(p["description"]),
             "<content:encoded>%s</content:encoded>" % cdata(body),
             "<itunes:episode>%d</itunes:episode>" % p["chapter"],
             "<itunes:episodeType>full</itunes:episodeType>",
             '<enclosure url="%s/assets/audio/%s.mp3" length="%d" type="audio/mpeg"/>'
             % (SITE, slug, entry["bytes"])]
        if entry.get("duration"):
            x.append("<itunes:duration>%s</itunes:duration>" % iso_duration(entry["duration"]))
        x.append("</item>")
        items.append("\n".join(x))
    newest = done[-1]["date"] if done else datetime.datetime.now(datetime.timezone.utc)
    art = SITE + "/podcast/hillMole.png"
    channel = [
        "<title>%s</title>" % cdata(FEED_TITLE),
        "<link>%s/complete.html</link>" % SITE,
        "<description>%s</description>" % cdata(
            "Hill Mole, Chris Abraham's serialized confession novel, read aloud in full: "
            "every chapter as audio, in order, in one feed. The text edition lives at "
            "hillmole.com, and the whole book, text and audio together, is on one page "
            "at hillmole.com/complete.html. This feed is the novel as a listening series."),
        "<language>en</language>",
        "<copyright>%s</copyright>" % esc("© 2005–%d %s" % (newest.year, AUTHOR)),
        "<lastBuildDate>%s</lastBuildDate>" % email.utils.format_datetime(
            newest.astimezone(datetime.timezone.utc), usegmt=True),
        '<atom:link href="%s/audio.xml" rel="self" type="application/rss+xml"/>' % SITE,
        "<itunes:author>%s</itunes:author>" % esc(AUTHOR),
        "<itunes:owner><itunes:name>%s</itunes:name><itunes:email>%s</itunes:email></itunes:owner>"
        % (esc(AUTHOR), OWNER_EMAIL),
        "<itunes:explicit>false</itunes:explicit>",
        '<itunes:image href="%s"/>' % art,
        '<itunes:category text="Arts"><itunes:category text="Books"/></itunes:category>',
        "<image><url>%s</url><title>%s</title><link>%s/complete.html</link></image>"
        % (art, esc(FEED_TITLE), SITE),
        "<podcast:medium>audiobook</podcast:medium>",
        "<podcast:guid>%s</podcast:guid>" % FEED_GUID,
    ]
    feed = "\n".join(['<?xml version="1.0" encoding="UTF-8"?>',
                      '<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" '
                      'xmlns:podcast="https://podcastindex.org/namespace/1.0" '
                      'xmlns:content="http://purl.org/rss/1.0/modules/content/" '
                      'xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/">',
                      "<channel>"] + channel + items + ["</channel>", "</rss>", ""])
    with open(FEED_PATH, "w", encoding="utf-8") as f:
        f.write(feed)
    return len(done)


def write_data_yml(posts, manifest):
    lines = ["# Generated by _audio/narrate.py — do not edit by hand.",
             "# basename -> narration for the chapter's read-aloud player."]
    n = 0
    for p in posts:
        slug = p["basename"]
        if slug in manifest and os.path.exists(os.path.join(AUDIO_DIR, slug + ".mp3")):
            e = manifest[slug]
            lines.append("%s:" % json.dumps(slug))
            lines.append("  file: %s" % json.dumps("/assets/audio/%s.mp3" % slug))
            if e.get("duration"):
                lines.append("  duration: %d" % int(round(e["duration"])))
            lines.append("  bytes: %d" % e["bytes"])
            n += 1
    with open(DATA_YML, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="narrate at most N owed chapters")
    ap.add_argument("--only", default="", help="comma-separated basenames to (re)narrate")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--no-feed", action="store_true", help="skip regenerating data/feed")
    args = ap.parse_args()

    posts = load_posts()
    manifest = {}
    if os.path.exists(MANIFEST):
        manifest = json.load(open(MANIFEST))
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(TEXT_DIR, exist_ok=True)

    texts, digests = {}, {}
    for p in posts:
        text = chapter_text(p["body"])
        texts[p["basename"]] = text
        digests[p["basename"]] = hashlib.sha256(
            (CHAPTER_VOICE + "\n" + p["title"] + "\n" + text).encode()).hexdigest()

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    owed = []
    for p in posts:  # chapter order
        slug = p["basename"]
        if only and slug not in only:
            continue
        mp3 = os.path.join(AUDIO_DIR, slug + ".mp3")
        if (manifest.get(slug) or {}).get("sha256") == digests[slug] and os.path.exists(mp3):
            continue
        owed.append(p)
    if args.limit:
        owed = owed[:args.limit]

    have_tts = os.path.exists(TTS_BIN)
    failed = []
    if owed and not have_tts:
        print("no tts tool here; %d chapters owed narration" % len(owed))
    elif owed:
        print("narrating %d chapter(s) with %d worker(s)..." % (len(owed), args.workers))
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futs = {pool.submit(narrate, p, texts[p["basename"]], digests[p["basename"]]): p
                    for p in owed}
            for fut in concurrent.futures.as_completed(futs):
                slug, entry = fut.result()
                if entry:
                    manifest[slug] = entry
                else:
                    failed.append(slug)
        with open(MANIFEST, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")

    if not args.no_feed:
        n_data = write_data_yml(posts, manifest)
        n_feed = write_feed(posts, manifest)
        print("data file: %d chapters with players; feed: %d items" % (n_data, n_feed))

    done = [p for p in posts if (manifest.get(p["basename"]) or {}).get("sha256") == digests[p["basename"]]
            and os.path.exists(os.path.join(AUDIO_DIR, p["basename"] + ".mp3"))]
    print("TOTAL: %d/%d chapters narrated; %d failed this run: %s"
          % (len(done), len(posts), len(failed), ", ".join(sorted(failed)) or "none"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
