#!/usr/bin/env python3
"""Portable verification gate for this control-systems research repo.

Vendor-neutral: any agent or human runs ``python scripts/verify.py`` (or
``make verify``). The Claude Code harness calls it from a Stop hook, but nothing
here depends on Claude — it is plain Python + subprocess.

Checks, in order:
  1. pytest      — all pure-numpy/scipy library units must pass.
  2. import-guard — ``import lib`` must succeed WITHOUT pulling in Pinocchio,
                    proving the plant-agnostic core works on machines (e.g.
                    Windows pip) where Pinocchio is unavailable.
  3. ruff        — advisory lint IF ruff is installed (never fails the gate;
                   this template does not force ruff as a dependency).

Exit codes:
  0  gate passed.
  2  gate failed (pytest or import-guard). Exit 2 doubles as the Claude Code
     "block stop" signal, so a failing gate keeps the agent working.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Windows consoles default to cp949/cp1252; force UTF-8 so output never crashes.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent


def _run(cmd: list[str]) -> int:
    """Run a subprocess from the repo root, streaming its output. Return rc."""
    print(f"\n$ {' '.join(cmd)}", flush=True)
    return subprocess.run(cmd, cwd=ROOT).returncode


def check_pytest() -> bool:
    print("=" * 60)
    print("[1/3] pytest - library unit tests")
    print("=" * 60)
    rc = _run([sys.executable, "-m", "pytest", "-q"])
    ok = rc == 0
    print("  -> PASS" if ok else "  -> FAIL")
    return ok


def check_import_guard() -> bool:
    """`import lib` must not drag in Pinocchio (plant-agnostic core stays pure)."""
    print("\n" + "=" * 60)
    print("[2/3] import-guard - core imports without Pinocchio")
    print("=" * 60)
    probe = (
        "import sys; import lib;\n"
        "assert 'pinocchio' not in sys.modules, "
        "'importing lib pulled in pinocchio (leak from lib/dynamics)';\n"
        "print('lib imported; pinocchio not loaded')"
    )
    rc = _run([sys.executable, "-c", probe])
    ok = rc == 0
    print("  -> PASS" if ok else "  -> FAIL")
    return ok


def check_ruff() -> bool:
    """Advisory only: run ruff if present, never fail the gate on it."""
    print("\n" + "=" * 60)
    print("[3/3] ruff - lint (advisory; skipped if not installed)")
    print("=" * 60)
    try:
        import ruff  # noqa: F401  (import just to detect availability)
        has_ruff = True
    except ImportError:
        has_ruff = subprocess.run(
            [sys.executable, "-m", "ruff", "--version"],
            cwd=ROOT,
            capture_output=True,
        ).returncode == 0

    if not has_ruff:
        print("  -> SKIP (ruff not installed)")
        return True
    rc = _run([sys.executable, "-m", "ruff", "check", "lib", "scripts"])
    print("  -> clean" if rc == 0 else "  -> lint findings (advisory, non-blocking)")
    return True  # advisory: never blocks the gate


def main() -> int:
    results = {
        "pytest": check_pytest(),
        "import-guard": check_import_guard(),
        "ruff": check_ruff(),
    }
    blocking_ok = results["pytest"] and results["import-guard"]

    print("\n" + "=" * 60)
    print("VERIFY SUMMARY")
    print("=" * 60)
    for name, ok in results.items():
        print(f"  {'OK  ' if ok else 'FAIL'}  {name}")
    if blocking_ok:
        print("\nGate PASSED. Safe to claim completion.")
        return 0
    print("\nGate FAILED. Fix the failures above before claiming completion.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
