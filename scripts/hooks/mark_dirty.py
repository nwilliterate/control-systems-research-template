#!/usr/bin/env python3
"""PostToolUse hook: flag the repo 'dirty' when code (not prose) is edited.

Claude Code passes the tool call as JSON on stdin. If the edited file is code
that the verification gate covers (lib/, experiments/, main.py, config params),
we drop a marker file so the Stop hook (scripts/hooks/gate.py) knows it must run
the gate before the agent is allowed to finish. Editing docs/ or results/ does
NOT arm the gate, so ordinary writing turns stay fast.

Always exits 0 — this hook observes, it never blocks.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MARKER = ROOT / ".claude" / ".verify-dirty"

# Editing any of these arms the verification gate.
WATCHED_DIRS = ("lib/", "experiments/", "scripts/", "tests/")
WATCHED_FILES = ("main.py", "config/params.yaml")


def _relpath(file_path: str) -> str:
    try:
        return Path(file_path).resolve().relative_to(ROOT).as_posix()
    except (ValueError, OSError):
        return Path(file_path).as_posix()


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # nothing parseable; do not block

    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path") or tool_input.get("path")
    if not file_path:
        return 0

    rel = _relpath(str(file_path))
    is_code = rel.startswith(WATCHED_DIRS) or rel in WATCHED_FILES
    if is_code:
        MARKER.parent.mkdir(parents=True, exist_ok=True)
        MARKER.write_text(rel + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
