"""Build book-index.html: a back-of-the-book index for Hill Mole, the way Washington tell-alls have one.

Headings are people (the novel's initials and real names), places, organizations, themes, and scenes.
Each lists the entry numbers where it appears, numbered as on the site ("Entry 47 of 309"), each linked.
Re-run after adding or editing entries:  python3 _migration/build_index.py
"""
import glob, html, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
posts = []
for p in glob.glob(os.path.join(ROOT, "_posts", "*.html")):
    s = open(p, encoding="utf-8").read()
    fm = s[:s.index("\n---\n", 4)]
    body = html.unescape(re.sub(r"<[^>]+>", " ", s[s.index("\n---\n", 4) + 5:]))
    posts.append({"date": re.search(r"^date: (.*)$", fm, re.M).group(1),
                  "title": html.unescape(re.search(r"^title: (.*)$", fm, re.M).group(1).strip('"')),
                  "url": re.search(r"^permalink: (.*)$", fm, re.M).group(1), "body": body})
posts.sort(key=lambda p: p["date"])
for n, p in enumerate(posts, 1):
    p["n"] = n
norm = lambda t: t.replace("’", "'").replace("‘", "'").lower()
by_title = {}
for p in posts:
    by_title.setdefault(norm(p["title"]), p["n"])  # the first entry with a title wins (two are named "Hiding in Plain Sight")

# People in the novel go by initials, so they're matched by hand-checked entry titles, never by a bare letter.
def titles(*ts):
    missing = [t for t in ts if norm(t) not in by_title]
    if missing:
        raise SystemExit("index: no entry titled %r" % missing)
    return {by_title[norm(t)] for t in ts}

def W_entries():
    out = set()
    for p in posts:
        b = re.sub(r"George W\.? Bush|Donald J\.|S&W", "", p["body"])
        if re.search(r"(?<![\w.])W(?:’s)?(?=[\s,.’])", b):
            out.add(p["n"])
    return out

# heading -> regex over the entry text, or a set of entry numbers
H = {
  # people in the novel
  "W. (the narrator's best friend)": W_entries(),
  "R. (a college chum)": titles("Dosed on Acid", "People Recognize Patterns", "Pervert or Kidnapper", "Hiding in Plain Sight", "Exactly the Opposite"),
  "L. (the painter friend)": titles("Quite Talented"),
  "M., also known as J.": titles("False Name", "Catch-22"),
  "B. (a former girlfriend)": titles("The Lovers My Lovers Have Had"),
  "C. (a friend from McLean)": titles("Little Kids in Langley Protect National Security"),
  "Charlie (the Ranger)": r"\bCharlie\b",
  "Otto Helm": r"Otto Helm",
  "Ira and Ruth": r"\bIra\b",
  "Jana and Carrie": r"\bJana\b",
  "the narrator's father": r"\bdad\b|my father",
  "the narrator's mother": r"my mother|\bmom\b",
  # real people
  "Babbitt, Ashli": r"Babbitt", "Baudelaire, Charles": r"Baudelaire", "Bell, Art": r"Art Bell",
  "Bernays, Edward": r"Bernays", "Biden, Joe": r"Biden", "Bond, James": r"James Bond|\bBond[’'.]",
  "Bush, George W.": r"George W\.? Bush",
  "Áder, János": r"Áder", "Berlusconi, Silvio": r"Berlusconi", "bin Laden, Osama": r"bin Laden",
  "Bolsonaro, Jair": r"Bolsonaro", "Columbus, Christopher": r"Columbus", "Cortés, Hernán": r"Cortés",
  "Derwinski, Ed": r"Derwinski", "Gore, Al": r"\bGore\b", "Harris, Kamala": r"Harris",
  "Mao Zedong": r"\bMao", "McCarthy, Joseph (McCarthyism)": r"McCarthy", "Mussolini, Benito": r"Mussolini",
  "Phillips, Howard": r"Howard Phillips", "Pizarro, Francisco": r"Pizarro", "Pope Alexander VI": r"Pope Alexander",
  "Roosevelt, Franklin D.": r"\bFDR\b|Roosevelt", "Sung, Jennifer": r"Jennifer Sung", "Tito, Josip Broz": r"\bTito", "Callicles": r"Callicles", "Carter, Jimmy": r"Jimmy Carter|peanut farmer",
  "Chomsky, Noam": r"Chomsky", "Clinton, Bill": r"Bill Clinton|\bClinton\b(?! won)", "Clinton, Hillary": r"Clinton won|Hillary",
  "Crichton, Michael": r"Crichton", "Emerson, Ralph Waldo": r"Emerson", "Epstein, Jeffrey": r"Epstein",
  "Freud, Sigmund": r"Freud", "Giffords, Gabby": r"Giffords", "Godwin, Mike (Godwin's law)": r"Godwin",
  "Goebbels, Joseph": r"Goebbels", "Gorbachev, Mikhail": r"Gorbachev", "Hitler, Adolf": r"Hitler",
  "Huxley, Aldous": r"Huxley", "Indiana Jones": r"Indiana Jones|\bIndy\b", "Jesus": r"\bJesus\b|\bChrist\b",
  "Kavanaugh, Brett": r"Kavanaugh", "Khrushchev, Nikita": r"Khrushchev", "Kipling, Rudyard": r"Kipling",
  "Lenin, Vladimir": r"Lenin", "Lippmann, Walter": r"Lippmann", "Luntz, Frank": r"Luntz", "Malcolm X": r"Malcolm X",
  "Mata Hari": r"Mata Hari", "Mendez, Jonna": r"Mendez", "Obama, Barack": r"Obama", "Orwell, George": r"Orwell",
  "Pelosi, Nancy": r"Pelosi", "Pence, Mike": r"Pence", "Plato": r"Plato", "Poe, Edgar Allan": r"\bPoe\b",
  "Putin, Vladimir": r"Putin", "Reagan, Nancy": r"Nancy Reagan", "Reagan, Ronald": r"Ronald Reagan|Reagan(?!-level)(?! Teflon)",
  "Rogan, Joe": r"Rogan", "Safire, William": r"Safire", "Sagan, Carl": r"Sagan", "Sartre, Jean-Paul": r"Sartre",
  "Scholz, Olaf": r"Scholz", "Stalin, Joseph": r"Stalin", "Stanislavsky, Konstantin": r"Stanislavsky",
  "Sun Tzu": r"Sun Tzu", "Trump, Donald": r"Trump", "Vonnegut, Kurt": r"Vonnegut", "Wellesley, Arthur": r"Wellesley",
  "Wowereit, Klaus": r"Wowereit",
  # places
  "Afghanistan": r"Afghan", "Alexandria, Virginia": r"Alexandria", "Arlington, Virginia": r"Arlington",
  "Berlin": r"Berlin", "Capitol Hill": r"Capitol Hill|the Hill\b|Cap Hill", "Germany": r"German",
  "Hawaii": r"Hawaii|Honolulu|Oahu|haole", "Kathmandu and Nepal": r"Katmandu|Kathmandu|Nepal",
  "Langley and McLean": r"Langley|McLean", "Russia and the Soviet Union": r"Russia|Soviet|USSR|Moscow|CCCP",
  "Saint Petersburg": r"Saint Petersburg", "Ukraine": r"Ukrain", "Washington, DC": r"Washington(?! Post)|\bDC\b",
  "Zack's (the bar)": r"Zack’s",
  # organizations
  "CIA": r"\bCIA\b|Central Intelligence|Pickle Factory|Company guys", "DIA": r"\bDIA\b",
  "FBI": r"\bFBI\b", "Freemasonry": r"Freemason", "JROTC and the Rangers": r"JROTC|Ranger", "NATO": r"\bNATO\b",
  "NPR": r"\bNPR\b", "Secret Service": r"Secret Service", "Treasury Department": r"[Tt]reasury",
  "World Bank": r"World Bank",
  # themes
  "9/11 and the war on terror": r"9/11|9-11|[Ww]ar on [Tt]error|September 11",
  "addiction and the lab rat": r"crack|addict",
  "ants, hives, and emergent systems": r"\bants?\b|[Hh]ive|colony|[Ee]mergent",
  "blowback and unintended consequences": r"[Bb]lowback|unintended consequences",
  "camouflage and hiding in plain sight": r"[Cc]amouflag|plain sight|[Gg]rey man|[Ii]nvisib",
  "COVID-19": r"COVID|Coronavirus|pandemic",
  "doctors as spies": r"\bdoctors?\b|\bdocs?\b",
  "drinking": r"\bdrunk|\bdrink|[Bb]eer\b|\bbars?\b",
  "fear and panic": r"\bpanic|\bfear",
  "free speech and censorship": r"[Ff]ree speech|[Cc]ensor|First Amendment",
  "guns and self-defense": r"\bgun|pistol|firearm|Glock|concealed carr",
  "January 6": r"January 6|Jan 6|1/6",
  "loneliness": r"lonel",
  "moles, handlers, and cover stories": r"\bmoles?\b|handler|cover stor|false name|alias",
  "Nazis and Hitler comparisons": r"Nazi|Hitler",
  "patience": r"[Pp]atien",
  "pattern recognition": r"pattern",
  "photography": r"photograph|camera",
  "propaganda and public relations": r"[Pp]ropaganda|public relations|\bPR\b|spin\b",
  "race and racism": r"racis|white supremac|reparations|ADOS",
  "secrets": r"\bsecret",
  "sex, seduction, and infidelity": r"seduc|\baffair|cheat|\blovers?\b|mistress|one.night",
  "surveillance": r"surveil|[Pp]anopticon|CCTV|sousveill",
  # scenes
  "scene: bike messenger days in Washington": titles("Bike Messenger", "Pre-Internet in a Big Way", "Washington Summers", "Capitol Hill was Open Door", "Security Eats Away"),
  "scene: W.'s visit and the dive watch": titles("Gaunt and Exhausted", "All Bezel and Links", "In One Deft Motion", "Shower Gel in the Bathroom"),
  "scene: JROTC war games in Hawaii": titles("I Was a Haole", "Junior Reserve Officer Training Corps", "Class A's on Thursdays", "Being a Young Cadet", "I Want to Be An Airborne Ranger", "Exit, Stage Left", "A Code of Silence", "Us Cadets", "A Fresh Clip of Ammo into the Chamber", "Spetsnaz-Trained Special Forces Operatives", "Hazing"),
  "scene: acid on the Mall with W. and R.": titles("Dosed on Acid", "All the Shapes and Colors Around Me", "People Recognize Patterns", "Pervert or Kidnapper", "Hiding in Plain Sight"),
  "scene: sailing from Acapulco to Marina del Rey": titles("The Sea is a Mean Bitch", "She Seems Gentle But it is Life or Death"),
  "scene: the strip club": titles("Memory of a Simpler Time and a Better Woman"),
  "scene: the dive bar in Alexandria": titles("Only Your Failures", "Full of Pride and Hunger"),
  "scene: the panic attack and the paper sack": titles("Infinite Loop and Core Dump", "Breathing Into A Brown Paper Sack"),
  "scene: the oligarch client who disappeared": titles("When Business Intelligence and Spycraft Meet"),
  "scene: moving to Berlin": titles("Upon Moving to Berlin"),
  "scene: the recruitment day near Dulles": titles("Even Spies Are Recruited By Headhunters"),
  "scene: flying over Russia to Kathmandu, 1990": titles("And ye shall hear of wars and rumors of wars"),
  # plot points
  "plot: the opening confession, a dupe and a fool": titles("I Was Merely a Dupe and a Fool.", "Inside the Beltway", "According to Plan"),
  "plot: the documents on the USB dongle": titles("Zack's is Small and Dark"),
  "plot: the filament in W.'s watch": titles("All Bezel and Links", "In One Deft Motion"),
  "plot: becoming privy to the patterns": titles("Privy to the Patterns", "False-Positives", "Washington is Rife with Intrigue"),
  "plot: wanting to go back to sleep": titles("Fancying Myself So Clever", "Myself, My New Wife, and My Future Children", "Sour Grapes", "Nobody Gives a Fuck", "I Do My Kegels", "Bumbling Around"),
  "plot: the interrogation and the panic attack": titles("Infinite Loop and Core Dump", "Breathing Into A Brown Paper Sack"),
  "plot: the recurring dream": titles("Wet Pillow"),
  "plot: W. arranges the move to Berlin": titles("Upon Moving to Berlin"),
  "plot: the client who vanished": titles("When Business Intelligence and Spycraft Meet"),
  "plot: applying to the intelligence service": titles("Even Spies Are Recruited By Headhunters"),
  "plot: the last word, it's all fancy dress": titles("It's all fancy dress"),
}

entries = []
for head, rule in H.items():
    nums = sorted(rule if isinstance(rule, set) else {p["n"] for p in posts if re.search(rule, p["body"])})
    if nums:
        entries.append((head, nums))
key = lambda h: re.sub(r"^(the |scene: |plot: )", "", h[0].lower())
entries.sort(key=key)

def link(n):
    p = posts[n - 1]
    return '<a href="{{ \'%s\' | relative_url }}" title="%s">%d</a>' % (p["url"], html.escape(p["title"]), n)

rows, letter = [], None
for head, nums in entries:
    first = key((head,))[0].upper()
    if first != letter:
        if letter:
            rows.append("</ul>")
        rows += ['<h2 id="index-%s">%s</h2>' % (first.lower(), first), '<ul class="book-index">']
        letter = first
    rows.append("  <li>%s, %s</li>" % (html.escape(head, quote=False), ", ".join(link(n) for n in nums)))
rows.append("</ul>")

page = """---
layout: default
title: Index
seo_title: "Hill Mole index: every person, place, theme, and scene"
description: "A back of the book index for Hill Mole: people, places, agencies, themes, and scenes, with the number of every entry where each one appears."
permalink: /book-index.html
---
<h1 class="archive-title">Index</h1>

<div class="entry-body about">
<p>Every Washington book has an index in the back, and everyone in town flips to it first. Here is Hill Mole's. Numbers are entry numbers, as shown at the top of each entry, and each one links to its entry. People in the novel go by initials. See also the <a href="{{ '/glossary.html' | relative_url }}">glossary</a>.</p>

""" + "\n".join(rows) + "\n</div>\n"
open(os.path.join(ROOT, "book-index.html"), "w", encoding="utf-8").write(page)
print(len(entries), "headings,", sum(len(n) for _, n in entries), "references")
