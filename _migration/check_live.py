"""After the DNS move: check the live site the way Google will see it.

  python3 _migration/check_live.py                      # https://hillmole.com
  python3 _migration/check_live.py https://chrisabraham.github.io/hillmole

Checks every URL the old Movable Type site served (old-urls.txt) answers 200,
that indexable pages carry no noindex and a canonical on this host, that
http:// and www. redirect to https://hillmole.com, and that robots.txt,
sitemap.xml, the feeds and the Search Console verification file are right.
"""
import concurrent.futures as cf
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://hillmole.com").rstrip("/")
LIVE = BASE == "https://hillmole.com"
HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "hillmole-cutover-check"}


def get(url, method="GET"):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA, method=method), timeout=30)
        return r.status, r.geturl(), (r.read() if method == "GET" else b"")
    except urllib.error.HTTPError as e:
        return e.code, url, b""
    except Exception as e:
        return 0, url, str(e).encode()


problems = []


def bad(msg):
    problems.append(msg)
    print("  FAIL", msg)


print(f"Checking {BASE}")

# 1. Every old URL still answers.
paths = [p for p in open(f"{HERE}/old-urls.txt").read().split() if p]
with cf.ThreadPoolExecutor(6) as ex:
    results = list(ex.map(lambda p: (p, get(BASE + p, "HEAD")[0]), paths))
missing = [p for p, s in results if s != 200]
print(f"old URLs: {len(paths) - len(missing)}/{len(paths)} answer 200")
for p in missing[:20]:
    bad(f"{p} -> {dict(results)[p]}")

# 2. Indexable pages: no noindex, canonical on this host.
status, _, body = get(BASE + "/sitemap.xml")
locs = [e.text for e in ET.fromstring(body).iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")] if status == 200 else []
print(f"sitemap: {len(locs)} URLs")
if not locs:
    bad("sitemap.xml missing or empty")
off_host = [u for u in locs if not u.startswith(BASE + "/")]
if off_host:
    bad(f"{len(off_host)} sitemap URLs not on {BASE}, e.g. {off_host[0]}")


def page_check(u):
    s, _, b = get(u)
    h = b.decode("utf-8", "replace")
    errs = []
    if s != 200:
        errs.append(f"{u} -> {s}")
    if LIVE and re.search(r'<meta name="robots" content="[^"]*noindex', h):
        errs.append(f"{u} has noindex")
    m = re.search(r'<link rel="canonical" href="([^"]+)"', h)
    if not m or not m.group(1).startswith(BASE + "/"):
        errs.append(f"{u} canonical is {m.group(1) if m else 'missing'}")
    return errs


with cf.ThreadPoolExecutor(6) as ex:
    for errs in ex.map(page_check, locs):
        for e in errs:
            bad(e)

# 3. Host variants all land on https://hillmole.com.
if LIVE:
    for v in ["http://hillmole.com/", "https://www.hillmole.com/", "http://www.hillmole.com/",
              "http://www.hillmole.com/archives/2005/05/i_was_merely_a.html"]:
        s, final, _ = get(v)
        if s != 200 or not final.startswith("https://hillmole.com/"):
            bad(f"{v} ends at {final} ({s}); should redirect to https://hillmole.com/")

# 4. Files Google and readers depend on.
s, _, b = get(BASE + "/robots.txt")
if s != 200 or f"Sitemap: {BASE}/sitemap.xml" not in b.decode():
    bad("robots.txt missing or Sitemap line wrong")
s, _, b = get(BASE + "/googlee028701e4dbb21d7.html")
if s != 200 or b"google-site-verification: googlee028701e4dbb21d7.html" not in b:
    bad("Search Console verification file missing")
for f in ["/index.rdf", "/index.xml", "/atom.xml", "/llms.txt"]:
    s, _, b = get(BASE + f)
    if s != 200 or not b:
        bad(f"{f} -> {s}")

print("\nALL GOOD" if not problems else f"\n{len(problems)} problem(s)")
sys.exit(1 if problems else 0)
