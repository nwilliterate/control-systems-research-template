#!/usr/bin/env python3
"""Scaffold a source-grounded knowledge atom (knowledge/claims/<id>.md).

Rather than let an agent improvise the front matter, this fills the template so the
required provenance fields are always present. The generated file intentionally still
FAILS `scripts/verify_knowledge.py` until a human/agent pastes the real verbatim quote
(for extracted claims) — that red bar is the forcing function against fabricated facts.

Usage:
    # extracted (default): must cite a BibTeX key + page, then paste the real quote
    python scripts/new_claim.py lqr-riccati --cite anderson1990optimal --page 47 \
        "LQR gives the optimal quadratic-cost control via the algebraic Riccati equation"

    # inferred: reasoned from other claims / sources
    python scripts/new_claim.py mpc-recovers-lqr --inferred \
        --from lqr-riccati,mpc-receding-horizon \
        "Unconstrained MPC with a quadratic cost recovers the LQR gain"

It refuses to overwrite an existing claim.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
CLAIMS_DIR = ROOT / "knowledge" / "claims"
SENTINEL = "«PASTE VERBATIM QUOTE HERE»"


def _fail(msg: str) -> int:
    print(f"error: {msg}", file=sys.stderr)
    return 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Scaffold a knowledge atom under knowledge/claims/.")
    p.add_argument("id", help="claim id / filename slug, e.g. lqr-riccati (lowercase [a-z0-9-])")
    p.add_argument("claim", nargs="?", default="<one crisp, checkable statement>",
                   help="the claim text (quote it)")
    p.add_argument("--inferred", action="store_true",
                   help="mark as reasoned-from-sources rather than quoted")
    p.add_argument("--cite", help="BibTeX key in references/references.bib (extracted claims)")
    p.add_argument("--page", help="source page number (extracted claims)")
    p.add_argument("--from", dest="derived", default="",
                   help="comma-separated claim ids / bib keys (inferred claims)")
    p.add_argument("--sha256", default="", help="first 12+ hex of the source PDF hash")
    p.add_argument("--confidence", default="high", choices=["high", "medium", "low"])
    return p


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)

    slug = args.id
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        return _fail(f"id must be lowercase [a-z0-9-], got {slug!r}")

    ctype = "inferred" if args.inferred else "extracted"
    out = CLAIMS_DIR / f"{slug}.md"
    if out.exists():
        return _fail(f"{out.relative_to(ROOT).as_posix()} already exists — refusing to overwrite")

    if ctype == "extracted" and not args.cite:
        return _fail("extracted claims need --cite <bibkey> (or pass --inferred)")

    derived = [d.strip() for d in args.derived.split(",") if d.strip()]
    if ctype == "inferred" and not derived:
        return _fail("inferred claims need --from id1,id2 (the basis they rest on)")

    fm = [
        "---",
        f"id: {slug}",
        f"type: {ctype}",
        "status: active",
        f"cite: {args.cite or ''}",
        f"page: {args.page or ''}",
        f"sha256: {args.sha256}",
        f"confidence: {args.confidence}",
        f"derived_from: [{', '.join(derived)}]",
        "supersedes:",
        "superseded_by:",
        "contradicts: []",
        f"updated: {date.today().isoformat()}",
        "---",
        "",
        f"**Claim:** {args.claim}",
        "",
    ]
    if ctype == "extracted":
        fm += [f"> {SENTINEL}", "",
               "<!-- ^ paste the EXACT source text; the verifier rejects the sentinel above. -->", ""]
    else:
        fm += ["**Notes:** <derivation: how this follows from the sources in derived_from>", ""]
    fm += ["**Applies to:** `lib/...`", ""]

    CLAIMS_DIR.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(fm), encoding="utf-8")

    rel = out.relative_to(ROOT).as_posix()
    print(f"Scaffolded knowledge atom: {rel}")
    if ctype == "extracted":
        print("\nNext steps:")
        print(f"  1. Open {rel} and replace the «PASTE VERBATIM QUOTE HERE» line with the real quote.")
        print(f"  2. Confirm cite `{args.cite}` is in references/references.bib (and page is right).")
        print("  3. python scripts/verify_knowledge.py   # must pass before commit")
    else:
        print("\nNext steps:")
        print(f"  1. Fill in **Notes:** in {rel} with the derivation.")
        print("  2. python scripts/verify_knowledge.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
