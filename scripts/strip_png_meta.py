#!/usr/bin/env python3
"""Removes text, EXIF and time chunks from PNG files (Blender writes the render settings and paths into them).

    python scripts/strip_png_meta.py <file-or-folder> [...]
"""
import struct
import sys
from pathlib import Path

DROP = {b"tEXt", b"iTXt", b"zTXt", b"eXIf", b"tIME"}


def strip(path):
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return False
    out, i, changed = [data[:8]], 8, False
    while i < len(data):
        n = struct.unpack(">I", data[i:i + 4])[0]
        kind = data[i + 4:i + 8]
        chunk = data[i:i + 12 + n]
        if kind in DROP:
            changed = True
        else:
            out.append(chunk)
        i += 12 + n
    if changed:
        path.write_bytes(b"".join(out))
    return changed


def main():
    for a in sys.argv[1:]:
        p = Path(a)
        for f in ([p] if p.is_file() else sorted(p.rglob("*.png"))):
            if strip(f):
                print("stripped", f)


if __name__ == "__main__":
    main()
