#!/usr/bin/env python3
"""Stop hook: enforce the verification gate before the agent may finish.

Runs only when code was touched this session (marker left by mark_dirty.py), so
conversational or docs-only turns are never slowed down. If the gate passes, the
marker is cleared and the agent is allowed to stop. If it fails, we exit 2, which
Claude Code treats as "block stop" and feeds our stderr back to the model — so a
red test bar keeps the agent working instead of declaring success.

Vendor-neutral core lives in scripts/verify.py; this file is just the Claude glue.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent.parent
MARKER = ROOT / ".claude" / ".verify-dirty"
VERIFY = ROOT / "scripts" / "verify.py"


def main() -> int:
    # Read (and tolerate) the Stop-hook payload; we only need stop_hook_active.
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    if not MARKER.exists():
        return 0  # no code changed since last pass -> allow stop

    result = subprocess.run([sys.executable, str(VERIFY)], cwd=ROOT)
    if result.returncode == 0:
        try:
            MARKER.unlink()
        except OSError:
            pass
        return 0

    # Gate failed: block the stop and tell the model why (stderr -> model).
    print(
        "Verification gate FAILED (scripts/verify.py). Do not claim completion: "
        "fix the failing pytest / import-guard checks above, then finish. "
        "Run `python scripts/verify.py` yourself to reproduce.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
