#!/usr/bin/env python3
"""Share cards for every Hill Mole entry: assets/cards/<mt_basename>.jpg, 1200x630.

The star-nosed mole across the top, the entry's title and date on the white column,
on the site's grey page. Titles are printed exactly as written. Re-run after adding
entries (existing cards are skipped unless the title changed):
    ~/.venvs/site/bin/python _migration/build_cards.py
_includes/seo.html points each entry at its card.
"""
import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "cards"
MANIFEST = OUT / "manifest.json"
FONT = Path("/usr/share/fonts/truetype/dejavu")
OUT.mkdir(parents=True, exist_ok=True)
manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}

banner = Image.open(ROOT / "assets" / "hillmole-card.jpg").convert("RGB")
strip = banner.crop((0, 150, 1200, 480)).resize((1080, 297))  # the mole's snout and claws
bold = ImageFont.truetype(str(FONT / "DejaVuSans-Bold.ttf"), 54)
reg = lambda s: ImageFont.truetype(str(FONT / "DejaVuSans.ttf"), s)


def wrap(d, text, font, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= width or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    return lines + [cur]


made = 0
for f in sorted((ROOT / "_posts").glob("*.html")):
    head = f.read_text(encoding="utf-8").split("\n---\n", 1)[0]
    meta = dict(re.findall(r'^(\w+):\s*"?(.*?)"?\s*$', head, re.M))
    slug = meta.get("mt_basename") or f.stem[11:]
    title = meta["title"].replace('\\"', '"')
    when = datetime.strptime(meta["date"][:10], "%Y-%m-%d")
    key = f"v2|{title}|{meta['date'][:10]}"
    out = OUT / f"{slug}.jpg"
    if manifest.get(slug) == key and out.exists():
        continue
    im = Image.new("RGB", (1200, 630), "#cccccc")
    d = ImageDraw.Draw(im)
    d.rectangle([60, 0, 1140, 630], fill="#ffffff")
    im.paste(strip, (60, 0))
    d.text((100, 322), f"hill mole · {when:%B} {when.day}, {when:%Y}", font=reg(28), fill="#6b6b6b")
    size, font = 54, bold
    lines = wrap(d, title, font, 1000)
    while len(lines) > 3 and size > 36:
        size -= 4; font = ImageFont.truetype(str(FONT / "DejaVuSans-Bold.ttf"), size); lines = wrap(d, title, font, 1000)
    width = 1000
    while width > 300 and len(wrap(d, title, font, width - 10)) == len(lines):
        width -= 10
    y = 372
    for ln in wrap(d, title, font, width)[:3]:
        d.text((100, y), ln, font=font, fill="#000000"); y += int(size * 1.22)
    d.text((100, 572), "hillmole.com", font=reg(26), fill="#6f6f6f")
    d.text((1100, 572), "a serialized novel by Chris Abraham", font=reg(24), fill="#6f6f6f", anchor="ra")
    im.save(out, quality=70, optimize=True, progressive=True)
    manifest[slug] = key
    made += 1
MANIFEST.write_text(json.dumps(manifest, indent=1, sort_keys=True))
print(f"cards: {made} made, {len(manifest)} total")
