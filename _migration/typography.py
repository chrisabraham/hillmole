"""Plain-text clean-up of entry bodies, at Chris' request (October 2026).

Hill Mole is plain prose, not hyperfiction, so entries carry no links:
  - every <a> is unwrapped, keeping its visible words
  - except the 2006 "[Listen ...]" links to the podcast MP3s, which sit
    outside the prose: the website keeps them as they were (keep_listen);
    the plain-text manuscript drops them
  - blogging-tool widgets with no text (Zemanta) are removed
Typography, applied to text only (never inside tags):
  - "--" becomes a closed-up em dash: "word -- word" -> "word—word"
  - "..." becomes "…"
  - straight quotes become curly; a quote between digits (6'4) is a
    feet/inches mark and is left alone

clean() returns the new HTML, the audio filename (or None), and a list of
human-readable changes for the per-entry log.
"""
import re

ZEMANTA = re.compile(r'\s*<div[^>]*class="zemanta-pixie".*?</div>', re.S)
LISTEN = re.compile(r'\s*\[<a href="[^"]*/podcast/([^"/]+\.mp3)">[^<]*</a>\]')
ANCHOR = re.compile(r"<a\b[^>]*>(.*?)</a>", re.S)
TAG = re.compile(r"(<[^>]+>)")

OPENERS = set(" \t\n\r ([{—–-/“‘") | {""}
ELISIONS = re.compile(r"(?:\d\ds?|em|cause|til|tis|round|n)\b", re.I)


def _quotes(text, prev):
    """Curl quotes in one text node. prev is the last visible char before it."""
    out = []
    for i, ch in enumerate(text):
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if ch == '"':
            if prev.isdigit():
                out.append(ch)  # inches
            else:
                # Opening only when a word follows; "I said—" closes.
                opening = prev in OPENERS and (nxt.isalnum() or nxt in "‘'(…")
                out.append("“" if opening else "”")
        elif ch == "'":
            if prev.isdigit() and nxt.isdigit():
                out.append(ch)  # feet: 6'4
            elif prev in OPENERS and nxt.isalnum() and not ELISIONS.match(text, i + 1):
                out.append("‘")
            else:
                out.append("’")
        else:
            out.append(ch)
        prev = out[-1]
    return "".join(out), prev


def clean(body, keep_listen=False):
    changes = []
    audio = None
    kept = []

    if ZEMANTA.search(body):
        body = ZEMANTA.sub("", body)
        changes.append("removed Zemanta reblog widget (no text)")

    m = LISTEN.search(body)
    if m:
        audio = m.group(1)
        if keep_listen:
            kept.append(m.group(0))
            body = LISTEN.sub("\x00LISTEN\x00", body)
        else:
            changes.append(f"dropped [{re.sub('<[^>]+>', '', m.group(0)).strip(' []')}] podcast link")
            body = LISTEN.sub("", body)

    def unwrap(a):
        changes.append(f"unlinked: {re.sub('<[^>]+>', '', a.group(1)).strip()!r}")
        return a.group(1)
    body = ANCHOR.sub(unwrap, body)

    parts = TAG.split(body)
    prev, n_dash, n_ell, n_q = "", 0, 0, 0
    for k, part in enumerate(parts):
        if not part or part.startswith("<"):
            continue
        before = part
        part, d = re.subn(r"[ \t ]*--[ \t ]*", "—", part)
        part, e = re.subn(r"\.\.\.", "…", part)
        part, prev = _quotes(part, prev)
        n_dash, n_ell = n_dash + d, n_ell + e
        n_q += sum(1 for a, b in zip(before.replace("--", "—").replace("...", "…"), part) if a != b)
        parts[k] = part
    body = "".join(parts)
    for k in kept:
        body = body.replace("\x00LISTEN\x00", k, 1)
    if n_dash:
        changes.append(f"{n_dash} × -- → —")
    if n_ell:
        changes.append(f"{n_ell} × ... → …")
    if n_q:
        changes.append(f"{n_q} straight quotes curled")
    return body, audio, changes


def clean_title(title):
    t = re.sub(r"[ \t]*--[ \t]*", "—", title).replace("...", "…")
    return _quotes(t, "")[0]
