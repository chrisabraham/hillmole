"""Build notes.html: Hill Mole's endnotes, the threads that run through it, and the book by the numbers.
Endnotes are hand-written and sourced; threads are found by pattern over the entry text; numbers are counted.
Re-run after editing entries:  python3 _migration/build_notes.py
"""
import collections, glob, html, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
posts = []
for p in glob.glob(os.path.join(ROOT, "_posts", "*.html")):
    s = open(p, encoding="utf-8").read()
    fm = s[:s.index("\n---\n", 4)]
    posts.append({"date": re.search(r"^date: (.*)$", fm, re.M).group(1),
                  "title": html.unescape(re.search(r"^title: (.*)$", fm, re.M).group(1).strip('"')),
                  "url": re.search(r"^permalink: (.*)$", fm, re.M).group(1),
                  "body": html.unescape(re.sub(r"<[^>]+>", " ", s[s.index("\n---\n", 4) + 5:]))})
posts.sort(key=lambda p: p["date"])
for n, p in enumerate(posts, 1):
    p["n"] = n
norm = lambda t: t.replace("’", "'").lower()
by_title = {}
for p in posts:
    by_title.setdefault(norm(p["title"]), p)

def entry(title):
    p = by_title.get(norm(title))
    if not p:
        raise SystemExit("notes: no entry titled %r" % title)
    return p

def ref(p, label=None):
    return '<a href="{{ \'%s\' | relative_url }}">%s</a>' % (p["url"], label or "entry %d, “%s”" % (p["n"], html.escape(p["title"])))

def num(p):
    return '<a href="{{ \'%s\' | relative_url }}" title="%s">%d</a>' % (p["url"], html.escape(p["title"]), p["n"])

W = lambda u, t: '<a href="%s">%s</a>' % (u, t)

# ---------------------------------------------------------------- endnotes: (entry title, note)
NOTES = [
 ("In Washington Nobody is Truly Private Sector", "Electric Boat, in Groton, Connecticut, has built submarines for the U.S. Navy for more than a century. It never built a Typhoon, though: the Typhoon class was the Soviet Union's, the largest submarines ever made. Our narrator's memory, like his sources, is not always reliable. " + W("https://en.wikipedia.org/wiki/Typhoon-class_submarine", "Typhoon class") + "."),
 ("Bee Hives and Ant Colonies", "The idea that a colony behaves intelligently with no one in charge is the heart of " + W("https://en.wikipedia.org/wiki/Emergence", "emergence") + ", and ants are its favorite example. It returns whenever the narrator wonders who, if anyone, is running Washington."),
 ("It Takes a Village to Raise a Holy Man", "Aldous Huxley's " + W("https://en.wikipedia.org/wiki/The_Doors_of_Perception", "The Doors of Perception") + " (1954) borrows from the philosopher C. D. Broad the idea that the brain works as a “reducing valve,” letting through only the trickle of reality we need to survive."),
 ("Emerson’s Invisible Eye", "Emerson's own phrase, in " + W("https://en.wikipedia.org/wiki/Nature_(essay)", "Nature") + " (1836), is “I become a transparent eye-ball; I am nothing; I see all.” The narrator turns it invisible, which suits a mole."),
 ("Sousveillance and the Sousveiller", "The word " + W("https://en.wikipedia.org/wiki/Sousveillance", "sousveillance") + " was coined by the wearable-computing pioneer Steve Mann: watching from below, by the watched."),
 ("Star-Nosed Mole (Condylura cristata cristata)", "The " + W("https://en.wikipedia.org/wiki/Star-nosed_mole", "star-nosed mole") + " really does have 22 fleshy rays around its nose, among the most sensitive touch organs known in any mammal. The narrator could hardly have picked a better mascot for someone who senses everything and sees very little."),
 ("The Mata Hari Syndrome", W("https://en.wikipedia.org/wiki/Mata_Hari", "Mata Hari") + ", the Dutch dancer Margaretha Zelle, was executed by a French firing squad on October 15, 1917, convicted of spying for Germany. Historians still argue over how much she actually did."),
 ("Constant Peace Through Constant War", "The Orwell passage comes from the forbidden book inside " + W("https://en.wikipedia.org/wiki/Nineteen_Eighty-Four", "Nineteen Eighty-Four") + ", the chapter called “War Is Peace.”"),
 ("Public Relations is Newspeak for Propaganda", "Edward Bernays did publish " + W("https://en.wikipedia.org/wiki/Propaganda_(book)", "Propaganda") + " in 1928 and Public Relations in 1952. The Baudelaire line closing the entry is from the prose poem “Le Joueur généreux” (1864). It comes back, in English, two years and six entries later."),
 ("How well do you really know someone?", "“Trust, but verify” is a Russian proverb, doveryai, no proveryai, that Ronald Reagan learned from the writer Suzanne Massie and used on Mikhail Gorbachev. At 816 words, this is the longest entry in the book."),
 ("Making a Spy in a Poor Multicultural City is Tough", "Klaus Wowereit, Berlin's mayor, called his city " + W("https://en.wikipedia.org/wiki/Arm,_aber_sexy", "“arm, aber sexy”") + " (poor but sexy) in a 2003 interview, and the city never let him forget it."),
 ("And ye shall hear of wars and rumors of wars", "The title is Matthew 24:6. The closing prayer is the " + W("https://en.wikipedia.org/wiki/Serenity_Prayer", "Serenity Prayer") + ", usually credited to Reinhold Niebuhr, and the fear line is from Franklin Roosevelt's first inaugural address, March 4, 1933."),
 ("I'll probably, legally, shoot you to death", "The 21-foot rule comes from Dennis Tueller, a Salt Lake City police trainer, whose 1983 article “How Close Is Too Close?” timed how fast a knife can cover the distance."),
 ("The Smith–Mundt Act is Dead", "The " + W("https://en.wikipedia.org/wiki/Smith%E2%80%93Mundt_Act", "Smith–Mundt Modernization Act of 2012") + " rode in on that year's defense authorization bill and took effect on July 2, 2013, two days before the holiday the entry names."),
 ("The shy Trump factor will get Donald Trump handily reëlected in November", "The " + W("https://en.wikipedia.org/wiki/Shy_Tory_factor", "shy Tory factor") + " got its name after the 1992 British general election, which the polls called for Labour and the Conservatives won. In 2020, unlike 1992, the pollsters were right about the winner."),
 ("Godwin’s rule of Trump analogies", "Mike Godwin, a lawyer, posted " + W("https://en.wikipedia.org/wiki/Godwin%27s_law", "his law") + " to Usenet in 1990."),
 ("West coast fires are false flag ecoterrorism", "In Michael Crichton's " + W("https://en.wikipedia.org/wiki/State_of_Fear", "State of Fear") + " (2004), the eco-terrorists' weapons include an engineered tsunami, which is why the narrator remembers water."),
 ("With no evidence", "There's no record that Joseph Goebbels ever said the “big lie” quotation pinned to him here; researchers have searched his speeches and diaries without finding it. The idea of the big lie itself is in Hitler's Mein Kampf, where he accuses others of using it. A misattributed quotation, in an entry about lies repeated until believed."),
 ("How about this as a baseless Novel Coronavirus theory?", "“Lies, damned lies, and statistics” was popularized by Mark Twain, who credited it to Benjamin Disraeli. No one has found it in Disraeli's work either."),
 ("Useful idiots", "This entry is the rare one that fact-checks itself: it ends by noting the phrase can't be traced to Lenin, which is correct."),
 ("The slave would rise in rebellion", "Callicles is the hard-headed opponent of Socrates in Plato's " + W("https://en.wikipedia.org/wiki/Gorgias_(dialogue)", "Gorgias") + ", arguing that natural justice belongs to the strong."),
 ("These are the buds of the socialist spring", "The passage opens Timothy Snyder's " + W("https://en.wikipedia.org/wiki/Bloodlands", "Bloodlands") + " (2010), describing the 1933 famine in Soviet Ukraine."),
 ("Déjà Afghanistan", "The lines are from Kipling's “The Young British Soldier,” in Barrack-Room Ballads (1892)."),
 ("America could win the Afghan war with crimes against humanity", "The Sun Tzu line is from chapter two of The Art of War, “Waging War.”"),
 ("It's all fancy dress", "The reckoning: the narrator, who in entry 1 called himself “merely a dupe and a fool,” decides fifteen years later that he is “neither an unwitting dupe nor even anyone's fool,” and then, two paragraphs on, “What a fool I've been.”"),
]

# ---------------------------------------------------------------- threads: (name, regex, note)
THREADS = [
 ("The dupe and the fool", r"\bdupe\b|\bfool\b", "The opening confession, and the verdict fifteen years later."),
 ("Pattern recognition", r"pattern", "The narrator's gift and his curse, from the fifth entry to the reckoning of 2020."),
 ("Hiding in plain sight", r"plain sight|plain site", "W.'s lesson on the Mall, repeated as doctrine."),
 ("The invisible man", r"invisib", "Photographers, moles, the fat, the ugly, and the old: everyone who can watch unseen."),
 ("Blowback", r"blowback", "A spy's word that becomes the book's theory of everything."),
 ("Hearts and minds", r"hearts and minds", "Seduction, propaganda, and counterinsurgency, treated as one craft."),
 ("“I'm just a simple man and I don't know much”", r"simple man.{0,30}don’t know", "The tell of the hustler, flagged twice, five years apart."),
 ("James Bond", r"James Bond", "The boyhood competition with W., and the license to kill."),
 ("The license to kill", r"license to kill", "Bond's, and then the narrator's own, by way of a Virginia carry permit."),
 ("The fairy godmother", r"fairy godmother", "Quoted in 2005, named fifteen years later."),
 ("The devil's best trick", r"devil’s best trick|ruses du diable", "Baudelaire, quoted with a translation in 2008, and again in English in 2010."),
 ("Our secrets are our sickness", r"secrets are our sickness", "The same five words, eight years apart."),
 ("Ants and hives", r"\bants?\b|\bhives?\b", "The emergent system that runs Washington, or doesn't."),
 ("The panopticon", r"panopticon", "From domestic spying in 2005 to citizen video in 2021."),
]

def matches(rx):
    return [p for p in posts if re.search(rx, p["body"], re.I)]

out = []
out.append('<h2 id="notes">Notes</h2>\n<ol class="endnotes">')
for i, (t, note) in enumerate(NOTES, 1):
    p = entry(t)
    out.append('  <li id="note-%d">%s. %s</li>' % (i, ref(p).replace(">entry", ">Entry", 1), note))
out.append("</ol>")

out.append('<h2 id="threads">Threads</h2>\n<p>Phrases and ideas the book keeps returning to, found by searching every entry. The years show how long each one runs.</p>\n<ul class="threads">')
for name, rx, note in THREADS:
    ps = matches(rx)
    if len(ps) < 2:
        continue
    y0, y1 = ps[0]["date"][:4], ps[-1]["date"][:4]
    span = y0 if y0 == y1 else "%s to %s" % (y0, y1)
    out.append("  <li><strong>%s</strong> (%d entries, %s). %s %s</li>" % (name, len(ps), span, note, ", ".join(num(p) for p in ps)))
out.append("</ul>")

years = collections.Counter(p["date"][:4] for p in posts)
words = [len(p["body"].split()) for p in posts]
longest = posts[words.index(max(words))]
shortest = posts[words.index(min(words))]
first, last = posts[0], posts[-1]
quiet = [y for y in range(int(first["date"][:4]), int(last["date"][:4]) + 1) if str(y) not in years]
busy = years.most_common(2)
out.append('<h2 id="numbers">By the numbers</h2>\n<ul class="numbers">')
out += ["  <li>%d entries, %s words, from %s to %s.</li>" % (len(posts), "{:,}".format(sum(words)), "May 13, 2005", "June 11, 2022"),
        "  <li>%d of them written in %s alone, and %d in %s.</li>" % (busy[0][1], busy[0][0], busy[1][1], busy[1][0]),
        "  <li>Years with no entries at all: %s.</li>" % ", ".join(map(str, quiet)),
        "  <li>Longest entry: %s, at %d words. Shortest: %s, at %d.</li>" % (ref(longest, "“%s”" % html.escape(longest["title"])), max(words), ref(shortest, "“%s”" % html.escape(shortest["title"])), min(words)),
        "  <li>W. appears in %d entries; nobody else in the cast comes close.</li>" % len([p for p in posts if re.search(r"(?<![\w.])W(?:’s)?(?=[\s,.’])", re.sub(r"George W\.? Bush|Donald J\.|S&W", "", p["body"]))]),
        "  <li>The word “Washington” appears in %d entries; “Berlin” in %d; “Hawaii” in %d.</li>" % tuple(len(matches(r"\b%s\b" % w)) for w in ("Washington", "Berlin", "Hawaii")),
        "</ul>"]

page = """---
layout: default
title: Notes
seo_title: "Hill Mole notes: endnotes, threads, and the numbers"
description: "Endnotes for Hill Mole on the real history behind the fiction, the threads the book keeps returning to across seventeen years, and the novel by the numbers."
permalink: /notes.html
---
<h1 class="archive-title">Notes</h1>

<div class="entry-body about">
<p>Endnotes on the real history, books, and quotations behind Hill Mole, sometimes including where the narrator gets them wrong. Then the threads that run through the book, and the book by the numbers. See also the <a href="{{ '/glossary.html' | relative_url }}">glossary</a> and the <a href="{{ '/book-index.html' | relative_url }}">index</a>.</p>

""" + "\n".join(out) + "\n</div>\n"
open(os.path.join(ROOT, "notes.html"), "w", encoding="utf-8").write(page)
print(len(NOTES), "notes,", len(THREADS), "threads")
