"""Spelling and grammar corrections, at Chris' request (October 2026).

corrections.tsv lists each fix: entry (mt_id), field (title or text), the
exact text to find, its replacement, and why. Candidates came from Hunspell
(dictionary) and LanguageTool (rule-based grammar); only objective errors were
kept: misspellings, wrong homophones, doubled words, broken agreement. Voice,
slang, coinages and deliberate usage are left alone.

Each find string must match exactly once in its entry, or the build stops,
so a correction can never land somewhere it wasn't meant to.
"""
import csv
import os
from collections import defaultdict

_ROWS = defaultdict(list)
with open(os.path.join(os.path.dirname(__file__), "corrections.tsv"), encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        _ROWS[(int(r["mt_id"]), r["field"])].append(r)


def correct(mt_id, field, s):
    notes = []
    for r in _ROWS.get((mt_id, field), []):
        n = s.count(r["find"])
        if n != 1:
            raise SystemExit(f"correction for mt_id {mt_id} {field} matches {n} times: {r['find']!r}")
        s = s.replace(r["find"], r["replace"])
        notes.append(f"corrected ({r['note']}): {r['find']!r} -> {r['replace']!r}")
    return s, notes
