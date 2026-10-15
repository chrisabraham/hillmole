"""Build atlas.html: the Hill Mole map, with every place on it clickable and listed with its entries.
The map art was generated with AI from a prompt built from the book, then corrected by hand (EUROPE, Langley).
Pins are percentages of the 1536x1024 image, so they stay put at any width.
Re-run after editing entries:  python3 _migration/build_atlas.py
"""
import glob, html, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1536, 1024
posts = []
for p in glob.glob(os.path.join(ROOT, "_posts", "*.html")):
    s = open(p, encoding="utf-8").read()
    fm = s[:s.index("\n---\n", 4)]
    place = re.search(r"^place: (.*)$", fm, re.M)
    posts.append({"date": re.search(r"^date: (.*)$", fm, re.M).group(1), "place": place.group(1).strip() if place else "",
                  "title": html.unescape(re.search(r"^title: (.*)$", fm, re.M).group(1).strip('"')),
                  "url": re.search(r"^permalink: (.*)$", fm, re.M).group(1),
                  "body": html.unescape(re.sub(r"<[^>]+>", " ", s[s.index("\n---\n", 4) + 5:]))})
posts.sort(key=lambda p: p["date"])
for n, p in enumerate(posts, 1):
    p["n"] = n

# id, label, (x, y) on the 1536x1024 map, regex over entry text, place tags that set the scene, note
PLACES = [
 ("honolulu", "Honolulu and Oahu", [(97, 507), (1360, 121)], r"Hawaii|Honolulu|Oahu|haole|Salt Lake", {"honolulu"}, "Growing up haole: JROTC, the Rangers, and war games in the jungle."),
 ("washington", "Washington, DC", [(511, 327)], r"Washington(?! Post)|\bDC\b", {"washington-dc"}, "Where nobody is truly private sector."),
 ("capitol-hill", "Capitol Hill and the Capitol", [(713, 768)], r"Capitol Hill|the Hill\b|Cap Hill|the Capitol", {"capitol-hill", "us-capitol"}, "The bike messenger's open city, and the camouflage of khakis and blue blazers."),
 ("the-mall", "The Mall", [(570, 801)], r"\bthe [Mm]all\b", set(), "Acid, a bench, and W.'s lesson about looking."),
 ("treasury", "The Treasury", [(516, 737)], r"[Tt]reasury", set(), "The narrator's own brush with a security review."),
 ("zacks", "Zack's", [(549, 713)], r"Zack’s", set(), "Camels, pool, and bottles of Bud."),
 ("langley", "Langley and McLean", [(197, 702)], r"Langley|McLean", {"mclean"}, "Where the kids know whose dads are CIA."),
 ("arlington", "Arlington", [(329, 817)], r"Arlington", {"arlington"}, ""),
 ("alexandria", "Alexandria", [(395, 883)], r"Alexandria", {"alexandria"}, "The dive bar decorated in business cards."),
 ("dulles", "Dulles", [(66, 746)], r"Dulles", set(), "W. flies in from Berlin; the recruiters park you near a bus stop."),
 ("groton", "Groton, Connecticut", [(528, 304)], r"Groton|Electric Boat", set(), "Submarine parts passed through a hole in the wall."),
 ("pacific-passage", "Acapulco to Marina del Rey", [(317, 423), (271, 327)], r"Acapulco|Marina del Rey", set(), "Months under sail with W. and Otto Helm."),
 ("guatemala", "Guatemala", [(396, 473)], r"Guatemala", set(), "One of W.'s childhoods."),
 ("monrovia", "Monrovia, Liberia", [(775, 508)], r"Monrovia|Liberia", set(), "Another of W.'s childhoods."),
 ("brussels", "Brussels", [(872, 276)], r"Brussels", set(), "Where S. lived, and M. couldn't visit."),
 ("berlin", "Berlin", [(917, 259)], r"Berlin", {"berlin"}, "The poor but sexy years."),
 ("saint-petersburg", "Saint Petersburg", [(1032, 224)], r"Saint Petersburg", set(), ""),
 ("kathmandu", "Kathmandu, 1990", [(1313, 411)], r"Katmandu|Kathmandu|Nepal", set(), "The bargain charter over a Soviet Union full of aircraft carcasses."),
 ("afghanistan", "Afghanistan", [(1152, 384)], r"Afghan", set(), "The graveyard of empires."),
]

def link(p, bold):
    a = '<a href="{{ \'%s\' | relative_url }}" title="%s">%d</a>' % (p["url"], html.escape(p["title"]), p["n"])
    return "<strong>%s</strong>" % a if bold else a

pins, items = [], []
for pid, label, pts, rx, tags, note in PLACES:
    ps = [p for p in posts if re.search(rx, p["body"]) or p["place"] in tags]
    if not ps:
        continue
    for (x, y) in pts:
        pins.append('<a class="pin" href="#%s" style="left:%.2f%%;top:%.2f%%" aria-label="%s, %d entries"></a>'
                    % (pid, 100 * x / W, 100 * y / H, html.escape(label), len(ps)))
    items.append('  <li id="%s"><strong>%s</strong>%s %s</li>' % (pid, html.escape(label), (": " + html.escape(note)) if note else ":",
                 ", ".join(link(p, p["place"] in tags) for p in ps)))

page = """---
layout: default
title: Atlas
seo_title: "Hill Mole atlas: a map of the mole's world"
description: "A map of Hill Mole's world, from Honolulu to Washington, Berlin, and Kathmandu, with every place on it linked to the entries set there or about it."
permalink: /atlas.html
og_image: /assets/hillmole-atlas-card.jpg
og_image_width: 1200
og_image_height: 630
og_image_alt: "Hill Mole: A Map of the Mole's World, a hand-drawn antique map from Honolulu to Washington, Berlin, and Kathmandu"
---
<h1 class="archive-title">Atlas</h1>

<div class="entry-body about">
<p>Every novel worth reading has a map in the front. Here is Hill Mole's: the narrator's world from a childhood in Honolulu to the District and its suburbs, Berlin, and a 1990 flight over Russia to Kathmandu. Click a place to see its entries.</p>

<div class="atlas">
<a href="{{ '/assets/hillmole-atlas.jpg' | relative_url }}"><img src="{{ '/assets/hillmole-atlas.jpg' | relative_url }}" srcset="{{ '/assets/hillmole-atlas-768.jpg' | relative_url }} 768w, {{ '/assets/hillmole-atlas.jpg' | relative_url }} 1536w" sizes="(min-width: 760px) 700px, 100vw" width="1536" height="1024" alt="Hill Mole: A Map of the Mole's World, drawn like an antique book map in black and red ink on parchment. Red dashed routes run from Honolulu to Washington, along the Pacific coast from Acapulco to Marina del Rey, across the Atlantic to Berlin, and over Russia to Kathmandu. Insets show the District and its Virginia suburbs inside the Beltway, with a security blimp overhead, and the island of Oahu. A star-nosed mole sits in the title cartouche and forms the north point of the compass rose."></a>
""" + "\n".join(pins) + """
</div>

<h2 id="places">Places</h2>
<p>Numbers are entry numbers. Bold ones are entries set in that place.</p>
<ul class="atlas-places">
""" + "\n".join(items) + """
</ul>

<p class="date">The map was drawn with AI image tools from a prompt built from the book's own places and journeys, then corrected by hand. See also the <a href="{{ '/glossary.html' | relative_url }}">glossary</a>, the <a href="{{ '/book-index.html' | relative_url }}">index</a>, and the <a href="{{ '/notes.html' | relative_url }}">notes</a>.</p>
</div>
"""
open(os.path.join(ROOT, "atlas.html"), "w", encoding="utf-8").write(page)
print(len(items), "places,", len(pins), "pins")
