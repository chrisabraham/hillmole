"""Extract Hill Mole entries from the MT MySQL dump.

Writes entries.json (all entries, repaired text) and encoding-repairs.log.
Usage: python3 extract.py <path-to-mysqldump.sql> <out-dir>
"""
import json
import re
import sys

import mysqldump as md

# MySQL "latin1" is cp1252, except 0x81 0x8D 0x8F 0x90 0x9D pass through.
PASSTHRU = {0x81, 0x8D, 0x8F, 0x90, 0x9D}


def to_bytes(s):
    out = bytearray()
    for ch in s:
        o = ord(ch)
        if o < 0x80 or (0xA0 <= o < 0x100) or o in PASSTHRU:
            out.append(o)
        else:
            try:
                out += ch.encode("cp1252")
            except UnicodeEncodeError:
                return None  # genuine non-latin1 char: field was stored correctly
    return bytes(out)


UTF8_SEQ = re.compile(
    rb"[\xC2-\xDF][\x80-\xBF]"
    rb"|[\xE0-\xEF][\x80-\xBF]{2}"
    rb"|[\xF0-\xF4][\x80-\xBF]{3}"
)


def from_bytes(b):
    """Inverse of to_bytes for single bytes."""
    if b < 0x80 or b >= 0xA0 or b in PASSTHRU:
        return chr(b)
    return bytes([b]).decode("cp1252")


def repair(s):
    """Undo double-encoded UTF-8, leaving lone cp1252 characters alone.

    Only byte runs forming valid multi-byte UTF-8 are decoded; every other
    character is returned unchanged. Repeats in case of triple encoding.
    """
    if not s or s.isascii():
        return s
    for _ in range(3):
        b = to_bytes(s)
        if b is None:
            return s
        out, pos = [], 0
        for m in UTF8_SEQ.finditer(b):
            out.extend(from_bytes(x) for x in b[pos:m.start()])
            out.append(m.group().decode("utf-8"))
            pos = m.end()
        out.extend(from_bytes(x) for x in b[pos:])
        new = "".join(out)
        if new == s:
            return s
        s = new
    return s


BLOCK = re.compile(
    r"^</?(?:h1|h2|h3|h4|h5|h6|table|ol|dl|ul|menu|dir|p|pre|center|form|"
    r"fieldset|select|blockquote|address|div|hr)"
)


def convert_breaks(s):
    """MT::Util::html_text_transform (MT 3.x 'Convert Line Breaks')."""
    paras = re.split(r"\r?\n\r?\n", s or "")
    while paras and paras[-1] == "":  # Perl's split drops trailing empty fields
        paras.pop()
    for k, p in enumerate(paras):
        if not BLOCK.match(p):
            p = re.sub(r"\r?\n", "<br />\n", p)
            paras[k] = "<p>" + p + "</p>"
    return "\n\n".join(paras)


def main(dump_path, out_dir):
    dump = open(dump_path, "rb").read()
    entries, log = [], []
    for e in md.rows(dump, "mt_entry"):
        rec = {
            "mt_id": e["entry_id"],
            "status": {1: "draft", 2: "published"}.get(e["entry_status"], e["entry_status"]),
            "created_on": e["entry_created_on"],
            "basename": e["entry_basename"],
            "convert_breaks": e["entry_convert_breaks"],
        }
        for f in ("title", "text", "text_more", "excerpt", "keywords"):
            raw = e["entry_" + f]
            fixed = repair(raw)
            rec[f] = fixed
            rec["raw_" + f] = raw
            if fixed != raw:
                diffs = sorted({m.group() for m in re.finditer(r"[^\x00-\x7f]+", raw)} -
                               {m.group() for m in re.finditer(r"[^\x00-\x7f]+", fixed)})
                log.append(f"{e['entry_id']}\t{e['entry_basename']}\t{f}\t"
                           + " ".join(f"{d!r}->{repair(d)!r}" for d in diffs))
        entries.append(rec)
    entries.sort(key=lambda r: (r["created_on"], r["mt_id"]))
    json.dump(entries, open(f"{out_dir}/entries.json", "w"), ensure_ascii=False, indent=1)
    open(f"{out_dir}/encoding-repairs.log", "w").write("\n".join(log) + "\n")
    print(f"{len(entries)} entries, {len(log)} repaired fields "
          f"across {len({l.split(chr(9))[0] for l in log})} entries")


if __name__ == "__main__":
    main(*sys.argv[1:])
