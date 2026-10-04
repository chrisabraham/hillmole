"""Minimal parser for mysqldump extended-INSERT files.

Reads the dump as raw bytes and returns rows as lists of Python values
(str for quoted strings, int/float for numbers, None for NULL). String
values are decoded as UTF-8 exactly as mysqldump wrote them; encoding
repair happens later, per field, in extract.py.
"""
import re

ESCAPES = {
    b"0": b"\x00", b"n": b"\n", b"r": b"\r", b"t": b"\t",
    b"Z": b"\x1a", b"\\": b"\\", b"'": b"'", b'"': b'"', b"b": b"\b",
}


def columns(dump: bytes, table: str):
    m = re.search(rb"CREATE TABLE `" + table.encode() + rb"` \((.*?)\n\) ENGINE", dump, re.S)
    return [c.decode() for c in re.findall(rb"^\s+`([^`]+)`", m.group(1), re.M)]


def _parse_values(buf: bytes, i: int):
    """Parse a sequence of (..),(..); starting at buf[i]. Yields rows."""
    n = len(buf)
    while i < n:
        assert buf[i:i + 1] == b"(", buf[i:i + 40]
        i += 1
        row = []
        while True:
            c = buf[i:i + 1]
            if c == b"'":
                i += 1
                out = bytearray()
                while True:
                    c = buf[i:i + 1]
                    if c == b"\\":
                        nxt = buf[i + 1:i + 2]
                        out += ESCAPES.get(nxt, nxt)
                        i += 2
                    elif c == b"'":
                        i += 1
                        break
                    else:
                        out += c
                        i += 1
                row.append(out.decode("utf-8"))
            else:
                j = i
                while buf[j:j + 1] not in (b",", b")"):
                    j += 1
                tok = buf[i:j].decode()
                i = j
                if tok == "NULL":
                    row.append(None)
                elif re.fullmatch(r"-?\d+", tok):
                    row.append(int(tok))
                else:
                    row.append(float(tok))
            c = buf[i:i + 1]
            i += 1
            if c == b")":
                break
            assert c == b",", (c, buf[i - 40:i + 40])
        yield row
        c = buf[i:i + 1]
        i += 1
        if c == b";":
            return
        assert c == b",", c


def rows(dump: bytes, table: str):
    cols = columns(dump, table)
    prefix = b"INSERT INTO `" + table.encode() + b"` "
    start = 0
    while True:
        k = dump.find(prefix, start)
        if k < 0:
            return
        k += len(prefix)
        if dump[k:k + 1] == b"(":
            # --complete-insert: explicit column list precedes VALUES
            close = dump.index(b") VALUES ", k)
            cols = [c.decode() for c in re.findall(rb"`([^`]+)`", dump[k:close])]
            k = close + 2
        k += len(b"VALUES ")
        end = dump.find(b"\n", k)
        for r in _parse_values(dump[k:end], 0):
            assert len(r) == len(cols), (table, len(r), len(cols))
            yield dict(zip(cols, r))
        start = end
