# AGENTS.md — Generic AI Agent Rules

Vendor-neutral rules for any AI coding agent (Claude Code, Codex, Cursor, Copilot,
Gemini, …) working in this robot-control research repository. For the full rationale
and research workflow, see [`CLAUDE.md`](./CLAUDE.md) — this file is the short contract.

## Project at a glance
- Domain: **robot control** academic research.
- Stack: **Pinocchio** (dynamics) + **python-control** (control design) + **Runge-Kutta** (integration).
- Style: **MATLAB/Spyder-like Python** — clear, top-to-bottom readable scripts; heavy
  logic hidden in a well-named library.

## Hard rules
1. Reusable logic goes in `lib/`. Scripts (`main.py`, `experiments/*`) only orchestrate.
2. `main.py` stays concise (target < 60 lines). Move any helper into `lib/`.
3. One clear responsibility per `lib/` file (m-file style). Prefer many small files.
4. Experiment scripts use Spyder `# %%` cells.
5. All tunable numbers live in `config/params.yaml`.
6. Outputs go to `results/figures` and `results/data` (git-ignored).
7. Docstrings must state physical **units** and array **shapes**.
8. Code lives in `experiments/`; research writing lives in `docs/`. Each
   `experiments/run_NN_*.py` is paired with `docs/experiments/exp_NN_*.md`
   (same NN). Methodology → `docs/methodology/`, papers → `docs/paper/`.

## Build / test commands
```bash
# Environment — uv (recommended):
uv sync                                  # core + dev tools (no Pinocchio)
uv sync --extra dynamics                 # + Pinocchio (Linux/macOS; Windows -> conda)
# or pinocchio via conda (required on Windows):
conda env create -f environment.yml && conda activate robot-control
# or plain pip, numpy parts only:
pip install -r requirements.txt

uv run pytest -q     # run unit tests   (conda/pip: `pytest -q`)
uv run python main.py # end-to-end demo (conda/pip: `python main.py`)
```

## Definition of done
- Code runs; `pytest -q` passes for pure-numpy library code.
- Pinocchio-dependent code is import-guarded so numpy tests pass without it.
- New reusable routines have a docstring (units + shapes) and, if pure-numpy, a test.
- No scope reduction, no deleted tests, no hard-coded parameters.
