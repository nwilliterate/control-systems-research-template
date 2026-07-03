#!/usr/bin/env python3
"""Print the sha256 of a file, for pasting into references/pdfs/manifest.yaml.

Usage:
    python scripts/hash_pdf.py references/pdfs/featherstone2008rigid.pdf

The first 12+ hex of the printed digest also goes in a claim's ``sha256`` field, so
CI (scripts/verify_knowledge.py) can flag the claim stale if the PDF ever changes.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python scripts/hash_pdf.py <path-to-file>", file=sys.stderr)
        return 1
    path = Path(argv[0])
    if not path.is_file():
        print(f"error: {path} is not a file", file=sys.stderr)
        return 1

    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    digest = h.hexdigest()
    print(digest)
    print(f"\nmanifest sha256: {digest}")
    print(f"claim   sha256: {digest[:12]}   (first 12 hex is enough for the staleness guard)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
