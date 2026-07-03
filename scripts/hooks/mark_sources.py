#!/usr/bin/env python3
"""PostToolUse hook: notice when the agent engages a source this session.

Fights "session decay" — the tendency to stop recording knowledge as a session
grows long. When a PDF is read, or a file under references/ or docs/literature/ is
edited, we drop a marker. The Stop hook (knowledge_reminder.py) later uses it to nudge
(once) for a knowledge/claims/ atom if none was written. Reading/writing a claim file
itself clears the marker, so honest capture is never nagged.

Always exits 0 — this hook observes, it never blocks.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MARKER = ROOT / ".claude" / ".knowledge-dirty"
CLAIMS_REL = "knowledge/claims/"
SOURCE_DIRS = ("references/", "docs/literature/")


def _rel(file_path: str) -> str:
    try:
        return Path(file_path).resolve().relative_to(ROOT).as_posix()
    except (ValueError, OSError):
        return Path(file_path).as_posix()


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path") or tool_input.get("path")
    if not file_path:
        return 0
    rel = _rel(str(file_path))

    # Authoring/reading a claim = capture is happening -> clear the nag.
    if rel.startswith(CLAIMS_REL):
        try:
            MARKER.unlink()
        except OSError:
            pass
        return 0

    engaged_pdf = tool == "Read" and rel.lower().endswith(".pdf")
    engaged_source = tool in ("Edit", "Write", "MultiEdit") and rel.startswith(SOURCE_DIRS)
    if engaged_pdf or engaged_source:
        MARKER.parent.mkdir(parents=True, exist_ok=True)
        MARKER.write_text(rel + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
