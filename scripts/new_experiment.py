#!/usr/bin/env python3
"""Scaffold a paired experiment (code + write-up) deterministically.

Enforces CLAUDE.md rule 5 / AGENTS.md rule 8: every ``experiments/run_NN_*.py``
has a paired ``docs/experiments/exp_NN_*.md`` with the SAME number NN. Rather
than let an agent improvise the structure, this script copies the two templates
and fills the placeholders.

Usage:
    python scripts/new_experiment.py NN slug ["Human Title"]

Example:
    python scripts/new_experiment.py 02 lqr_cartpole "LQR balance of a cart-pole"
      -> experiments/run_02_lqr_cartpole.py
      -> docs/experiments/exp_02_lqr_cartpole.md
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
PY_TEMPLATE = ROOT / "experiments" / "template_experiment.py"
MD_TEMPLATE = ROOT / "docs" / "experiments" / "_experiment_template.md"


def _fail(msg: str) -> "int":
    print(f"error: {msg}", file=sys.stderr)
    return 1


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        return _fail("usage: python scripts/new_experiment.py NN slug [\"Title\"]")

    nn_raw, slug = argv[0], argv[1]
    title = argv[2] if len(argv) > 2 else slug.replace("_", " ").title()

    if not nn_raw.isdigit():
        return _fail(f"NN must be numeric, got {nn_raw!r}")
    nn = nn_raw.zfill(2)
    if not re.fullmatch(r"[a-z0-9_]+", slug):
        return _fail(f"slug must be lowercase [a-z0-9_], got {slug!r}")

    tag = f"{nn}_{slug}"
    run_id = f"run_{tag}"
    py_out = ROOT / "experiments" / f"run_{tag}.py"
    md_out = ROOT / "docs" / "experiments" / f"exp_{tag}.md"

    for out in (py_out, md_out):
        if out.exists():
            return _fail(f"{out.relative_to(ROOT)} already exists — refusing to overwrite")

    # --- code script ------------------------------------------------------
    py = PY_TEMPLATE.read_text(encoding="utf-8")
    py = py.replace("run_NN_short_description", f"run_{tag}")
    py = py.replace("exp_NN_short_description", f"exp_{tag}")
    py = py.replace('"run_NN"', f'"{run_id}"')
    py = py.replace("run_NN", run_id)  # any stragglers
    py_out.write_text(py, encoding="utf-8")

    # --- write-up ---------------------------------------------------------
    md = MD_TEMPLATE.read_text(encoding="utf-8")
    md = md.replace("EXP-NN", f"EXP-{nn}")
    md = md.replace("<Experiment Title>", title)
    md = md.replace("run_NN_*.py", f"run_{tag}.py")
    md = md.replace("run_NN", run_id)
    md_out.write_text(md, encoding="utf-8")

    print("Scaffolded paired experiment:")
    print(f"  code : {py_out.relative_to(ROOT)}")
    print(f"  docs : {md_out.relative_to(ROOT)}")
    print("\nNext steps:")
    print(f"  1. Edit {py_out.relative_to(ROOT)} cell-by-cell (Spyder # %%).")
    print(f"  2. Record hypothesis/results in {md_out.relative_to(ROOT)}.")
    print(f"  3. Save outputs under results/*/{run_id}/ via lib.utils.io / plotting.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
