#!/usr/bin/env python3
"""Stop hook: nudge to persist source-grounded knowledge before the session ends.

This is the harness answer to "sessions get long and the agent stops saving." If the
agent engaged a source this session (marker from mark_sources.py) but wrote no
knowledge/claims/ atom, we block the stop ONCE and tell the model to capture the
durable facts now — moving the save from the model's fading discretion into a
deterministic gate.

It never traps the user: if a claim file is newer than the marker (something was
saved), or we already nudged once this stop (`stop_hook_active`), the marker is cleared
and the stop is allowed.

Exit codes:
  0  allow stop (nothing engaged, already captured, or already nudged once).
  2  block stop once and feed the reminder back to the model.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent.parent
MARKER = ROOT / ".claude" / ".knowledge-dirty"
CLAIMS_DIR = ROOT / "knowledge" / "claims"


def _clear() -> None:
    try:
        MARKER.unlink()
    except OSError:
        pass


def _claim_saved_since(marker_mtime: float) -> bool:
    if not CLAIMS_DIR.exists():
        return False
    for p in CLAIMS_DIR.glob("*.md"):
        if p.name.startswith("_"):
            continue
        try:
            if p.stat().st_mtime >= marker_mtime:
                return True
        except OSError:
            continue
    return False


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    if not MARKER.exists():
        return 0  # no source engaged this session -> nothing to nudge

    marker_mtime = MARKER.stat().st_mtime
    if _claim_saved_since(marker_mtime):
        _clear()
        return 0  # a claim was written after the source was touched -> captured

    if payload.get("stop_hook_active"):
        _clear()
        return 0  # already nudged once this stop -> don't trap the session

    touched = MARKER.read_text(encoding="utf-8").strip() or "a source"
    print(
        f"You engaged a source this session ({touched}) but wrote no knowledge/claims/ "
        "atom. Before finishing, capture any durable, source-grounded fact worth keeping: "
        "`python scripts/new_claim.py <id> --cite <bibkey> --page <N> \"<claim>\"` "
        "(or /new-claim), paste the verbatim quote, and run "
        "`python scripts/verify_knowledge.py`. If nothing is worth saving, stop again to proceed.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
