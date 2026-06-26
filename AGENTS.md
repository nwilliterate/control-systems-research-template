# AGENTS.md — Generic AI Agent Rules

Vendor-neutral rules for any AI coding agent (Claude Code, Codex, Cursor, Copilot,
Gemini, …) working in this control-systems research repository. For the full rationale
and research workflow, see [`CLAUDE.md`](./CLAUDE.md) — this file is the short contract.

## Project at a glance
- Domain: **control-systems** academic research — state-space plants (`x' = f(x, u)`).
- The **robot** (`RobotPlant`, Pinocchio-backed) is the flagship example plant; other
  built-in plants (`double_integrator`, `mass_spring_damper`, `CartPole`) need no Pinocchio.
- Stack: `lib/systems/` (Plant ABC + LTI tools) + **Pinocchio** (robot plant, `lib/dynamics/`)
  + **python-control** (LQR, pole placement) + **cvxpy** (MPC / convex opt)
  + **SymPy** (symbolic) + **Runge-Kutta** (integration).
- Optional extras (`opt`): **CasADi** (nonlinear MPC) + **slycot** (MIMO routines).
- Style: **MATLAB/Spyder-like Python** — clear, top-to-bottom readable scripts; heavy
  logic hidden in a well-named library.

## Hard rules
1. Reusable logic goes in `lib/`. Scripts (`main.py`, `experiments/*`) only orchestrate.
2. `main.py` stays concise (target < 60 lines). Move any helper into `lib/`.
3. One clear responsibility per `lib/` file (m-file style). Prefer many small files.
4. Experiment scripts use Spyder `# %%` cells.
5. All tunable numbers live in `config/params.yaml`.
6. Outputs go to `results/figures` and `results/data` (git-ignored).
7. Docstrings must state physical **units** and array **shapes** (e.g. `x : (nx,) state`).
8. Code lives in `experiments/`; research writing lives in `docs/`. Each
   `experiments/run_NN_*.py` is paired with `docs/experiments/exp_NN_*.md`
   (same NN). Methodology → `docs/methodology/`, papers → `docs/paper/`.
9. New plants subclass `Plant` (`lib/systems/plant.py`) and are registered in
   `lib/systems/build.py`. Pinocchio imports stay confined to `lib/dynamics/`.

## Build / test commands
```bash
# Environment — uv (recommended):
uv sync                                       # core + dev tools (cvxpy, sympy; no Pinocchio)
uv sync --extra dynamics                      # + Pinocchio (Linux/macOS; Windows -> conda)
uv sync --extra opt                           # + CasADi + slycot
uv sync --extra dynamics --extra opt          # everything
# or Pinocchio via conda (required on Windows):
conda env create -f environment.yml && conda activate robot-control
# or plain pip, core deps only:
pip install -r requirements.txt
pip install -e '.[opt]'                       # add opt extras on top

uv run pytest -q      # run unit tests   (conda/pip: `pytest -q`)
uv run python main.py # end-to-end demo  (conda/pip: `python main.py`)
                      # set plant.type in config/params.yaml before running
```

## Definition of done
- Code runs; `pytest -q` passes for all pure-numpy/scipy library code.
- Pinocchio-dependent code is import-guarded so tests pass without it.
- New reusable routines have a docstring (units + shapes) and, if pure-numpy, a test.
- No scope reduction, no deleted tests, no hard-coded parameters.
