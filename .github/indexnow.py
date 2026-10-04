"""Tell IndexNow (Bing, Yandex, Seznam, Naver, Yep) which URLs changed.

Run by .github/workflows/indexnow.yml after a push to main. Does nothing
until _config.yml's url is https://hillmole.com, so the github.io preview
never gets submitted.

  python3 .github/indexnow.py <before-sha> <after-sha>   changed entries + index pages
  python3 .github/indexnow.py --all                      every URL in the live sitemap
"""
import json
import re
import subprocess
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET

LIVE = "https://hillmole.com"


def config():
    c = open("_config.yml", encoding="utf-8").read()
    get = lambda k: (re.search(rf'^{k}:\s*"?([^"\n]*)"?', c, re.M) or [None, ""])[1].strip()
    return get("url"), get("indexnow_key")


def post_url(path):
    """URL of a _posts file: its permalink, or /archives/YYYY/MM/slug.html."""
    text = open(path, encoding="utf-8").read()
    m = re.search(r"^permalink:\s*(\S+)", text, re.M)
    if m:
        return LIVE + m.group(1)
    m = re.match(r"_posts/(\d{4})-(\d{2})-\d{2}-(.+)\.(md|markdown|html)$", path)
    slug = re.sub(r"[^a-z0-9]+", "-", m.group(3).lower()).strip("-")
    return f"{LIVE}/archives/{m.group(1)}/{m.group(2)}/{slug}.html"


def changed_urls(before, after):
    if not before or set(before) == {"0"}:
        return []
    files = subprocess.run(["git", "diff", "--name-only", "--diff-filter=AM", before, after],
                           capture_output=True, text=True, check=True).stdout.split()
    posts = [f for f in files if f.startswith("_posts/")]
    if not posts:
        return []
    return [post_url(f) for f in posts] + [LIVE + "/", LIVE + "/archives.html"]


def sitemap_urls():
    with urllib.request.urlopen(LIVE + "/sitemap.xml", timeout=30) as r:
        tree = ET.fromstring(r.read())
    return [e.text.strip() for e in tree.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]


def wait_live(urls, timeout=900):
    """GitHub Pages deploys after the push; wait until new pages answer."""
    deadline = time.time() + timeout
    pending = list(urls)
    while pending and time.time() < deadline:
        still = []
        for u in pending:
            try:
                urllib.request.urlopen(urllib.request.Request(u, method="HEAD"), timeout=20)
            except Exception:
                still.append(u)
        pending = still
        if pending:
            time.sleep(30)
    return [u for u in urls if u not in pending]


def submit(urls, key):
    body = json.dumps({"host": "hillmole.com", "key": key,
                       "keyLocation": f"{LIVE}/{key}.txt", "urlList": urls}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"IndexNow: HTTP {r.status} for {len(urls)} URLs")


def main():
    url, key = config()
    if url.rstrip("/") != LIVE:
        print(f"site url is {url}, not {LIVE}; skipping IndexNow")
        return
    urls = sitemap_urls() if sys.argv[1:] == ["--all"] else changed_urls(*sys.argv[1:3])
    if not urls:
        print("no entry changes; nothing to submit")
        return
    urls = wait_live(sorted(set(urls)))
    for i in range(0, len(urls), 10000):
        submit(urls[i:i + 10000], key)


if __name__ == "__main__":
    main()
