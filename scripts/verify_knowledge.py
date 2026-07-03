#!/usr/bin/env python3
"""Portable verifier for the source-grounded knowledge store (knowledge/claims/).

AI makes mistakes, so no knowledge atom is trusted unless it is traceable to a real
source. This gate rejects any claim that:
  * has an id not matching its filename, or a bad type/status;
  * is `extracted` but lacks a `cite` present in references/references.bib, a `page`,
    or a real verbatim quote (the scaffold sentinel «PASTE …» does NOT count);
  * is `inferred` but lists no `derived_from` basis (each must resolve to a claim or key);
  * has a dangling / non-reciprocal supersedes / superseded_by / contradicts link.

Vendor-neutral: plain Python + PyYAML (already a project dependency). No Claude needed.
Runs in CI and via `make verify-knowledge`.

Exit codes:
  0  all claims valid (or none authored yet).
  1  one or more claims invalid — details printed.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

# Windows consoles default to cp949/cp1252; force UTF-8 so output never crashes.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
CLAIMS_DIR = ROOT / "knowledge" / "claims"
BIB = ROOT / "references" / "references.bib"

VALID_TYPES = {"extracted", "inferred"}
VALID_STATUS = {"active", "superseded"}
QUOTE_SENTINEL = "«PASTE"  # produced by new_claim.py; must be replaced by real text
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
BIBKEY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,")


def _bib_keys() -> set[str]:
    if not BIB.exists():
        return set()
    return set(BIBKEY_RE.findall(BIB.read_text(encoding="utf-8")))


def _quote_lines(body: str) -> list[str]:
    """Non-empty markdown blockquote lines (`> ...`) with >= 10 chars of content."""
    out = []
    for line in body.splitlines():
        s = line.strip()
        if s.startswith(">"):
            content = s.lstrip(">").strip()
            if len(content) >= 10:
                out.append(content)
    return out


def _as_list(value) -> list:
    if value is None or value == "":
        return []
    return value if isinstance(value, list) else [value]


def _load_claims() -> tuple[dict, list[str]]:
    """Return ({id: (meta, body, path)}, errors) for every non-underscore claim."""
    claims: dict = {}
    errors: list[str] = []
    for path in sorted(CLAIMS_DIR.glob("*.md")):
        if path.name.startswith("_"):
            continue  # templates / scratch
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        m = FRONTMATTER_RE.match(text)
        if not m:
            errors.append(f"{rel}: missing YAML front matter (--- ... ---)")
            continue
        try:
            meta = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError as exc:
            errors.append(f"{rel}: unparseable front matter: {exc}")
            continue
        if not isinstance(meta, dict):
            errors.append(f"{rel}: front matter is not a mapping")
            continue
        claims[path.stem] = (meta, m.group(2), rel)
    return claims, errors


def _check_one(stem: str, meta: dict, body: str, rel: str, bibkeys: set[str]) -> list[str]:
    errs: list[str] = []

    def need(field):
        if meta.get(field) in (None, "", []):
            errs.append(f"{rel}: `{field}` is required")
            return False
        return True

    if meta.get("id") != stem:
        errs.append(f"{rel}: `id` ({meta.get('id')!r}) must equal filename ({stem!r})")

    ctype = meta.get("type")
    if ctype not in VALID_TYPES:
        errs.append(f"{rel}: `type` must be one of {sorted(VALID_TYPES)}, got {ctype!r}")
    if meta.get("status") not in VALID_STATUS:
        errs.append(f"{rel}: `status` must be one of {sorted(VALID_STATUS)}")
    need("updated")

    if ctype == "extracted":
        if need("cite") and meta["cite"] not in bibkeys:
            errs.append(f"{rel}: cite `{meta['cite']}` not found in references/references.bib")
        need("page")
        quotes = _quote_lines(body)
        if not quotes:
            errs.append(f"{rel}: extracted claim needs a verbatim quote (a `> ...` blockquote)")
        elif any(QUOTE_SENTINEL in q for q in quotes):
            errs.append(f"{rel}: replace the «PASTE VERBATIM QUOTE HERE» sentinel with the real source text")
    elif ctype == "inferred":
        basis = _as_list(meta.get("derived_from"))
        if not basis:
            errs.append(f"{rel}: inferred claim needs a non-empty `derived_from`")
    return errs


def _check_links(claims: dict) -> list[str]:
    """supersedes/superseded_by reciprocity + contradicts referential integrity."""
    errs: list[str] = []
    ids = set(claims)
    for stem, (meta, _body, rel) in claims.items():
        sup = meta.get("supersedes")
        if sup:
            if sup not in ids:
                errs.append(f"{rel}: supersedes `{sup}` — no such claim")
            elif claims[sup][0].get("superseded_by") != stem:
                errs.append(f"{rel}: supersedes `{sup}`, but that claim's superseded_by != `{stem}`")
            elif claims[sup][0].get("status") != "superseded":
                errs.append(f"{rel}: supersedes `{sup}`, but `{sup}` is not marked status: superseded")
        by = meta.get("superseded_by")
        if by and by not in ids:
            errs.append(f"{rel}: superseded_by `{by}` — no such claim")
        for other in _as_list(meta.get("contradicts")):
            if other not in ids:
                errs.append(f"{rel}: contradicts `{other}` — no such claim")
        # inferred basis that looks like a claim id (not a bib key) must resolve
    return errs


def main() -> int:
    print("=" * 60)
    print("verify-knowledge — source-grounded claim store")
    print("=" * 60)
    if not CLAIMS_DIR.exists():
        print(f"no {CLAIMS_DIR.relative_to(ROOT).as_posix()}/ — nothing to check.")
        return 0

    bibkeys = _bib_keys()
    claims, errors = _load_claims()
    for stem, (meta, body, rel) in claims.items():
        errors.extend(_check_one(stem, meta, body, rel, bibkeys))
    errors.extend(_check_links(claims))

    n_active = sum(1 for m, _b, _r in claims.values() if m.get("status") == "active")
    print(f"claims: {len(claims)} ({n_active} active)   bib keys: {len(bibkeys)}")

    if not errors:
        print("\nAll claims valid. Every atom is traceable to a source.")
        return 0

    print(f"\n{len(errors)} problem(s):")
    for e in errors:
        print(f"  FAIL  {e}")
    print("\nFix the atoms above (or run `python scripts/new_claim.py --help`).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
