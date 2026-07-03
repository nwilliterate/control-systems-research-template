# AGENTS.md — AI agent rules (single source of truth)

The **one** file every AI coding agent (Claude Code, Codex, Cursor, Copilot, Gemini,
…) and human reads before working in this control-systems research repository.
`CLAUDE.md` is just a pointer to this file.

Development philosophy: **MATLAB/Spyder-style Python** — code reads like a clear lab
notebook, top-to-bottom, with heavy machinery hidden inside well-named `lib/`
functions. This is research code: **physical correctness matters more than cleverness.**

## Project at a glance
- Domain: **control-systems** academic research — state-space plants (`x' = f(x, u, t)`).
  Any system with a state `x`, input `u`, and derivative is a plant.
- The **robot** (`RobotPlant`, Pinocchio-backed) is the flagship example plant; other
  built-in plants (`double_integrator`, `mass_spring_damper`, `CartPole`) need no Pinocchio.
- Stack: `lib/systems/` (Plant ABC + LTI tools) + **Pinocchio** (robot plant, `lib/dynamics/`)
  + **python-control** (LQR, pole placement) + **cvxpy** (MPC / convex opt)
  + **SymPy** (symbolic) + **Runge-Kutta** (integration).
- Optional extras (`opt`): **CasADi** (nonlinear MPC) + **slycot** (MIMO routines).

## Directory map
```
lib/                  Reusable toolbox — import from here, never inline into scripts
  systems/            Plant-agnostic core (pure NumPy/SciPy — NO Pinocchio)
    plant.py          Plant ABC: nx, nu, dynamics(x,u,t)->xdot, output(x,u,t)->y
    state_space.py    StateSpace LTI x'=Ax+Bu, y=Cx+Du; controllability helpers
    discretize.py     c2d(A,B,dt): ZOH exact discretization via matrix exponential
    linearize.py      linearize_plant(plant,x0,u0): central-difference A,B Jacobians
    examples.py       double_integrator(), mass_spring_damper(), CartPole
    build.py          build_plant(cfg): maps config plant.type -> concrete Plant
  dynamics/           Robot plant — Pinocchio rigid-body dynamics (imports confined here)
  integrators/        Runge-Kutta: rk4_step / rk45_step
  controllers/        Control laws (t,x)->u: pid, computed_torque, lqr, state_feedback,
                      pole_placement, mpc, factory (robot), build (plant-agnostic)
  sim/                simulate(plant,controller,x0,t_final,dt,integrator)->(t,x,u)
  utils/              plotting, io, config loading
experiments/          Spyder cell scripts (# %%), one per study: run_NN_*.py
models/               URDF robot descriptions
config/params.yaml    ALL tunable numbers (sim, plant, robot, controller, references)
results/figures       Saved plots (git-ignored)   results/data  Saved .npz (git-ignored)
tests/                pytest units (all pure-numpy code runs without Pinocchio)
docs/                 Research writing: methodology/, experiments/exp_NN_*.md,
                      literature/, paper/, research_notes.md
scripts/              Agent harness core: verify.py (gate), new_experiment.py (scaffold)
main.py               Concise end-to-end demo (plant-agnostic)
```

## Hard rules
1. Reusable logic goes in `lib/`. Scripts (`main.py`, `experiments/*`) only orchestrate.
2. `main.py` stays concise (target < 60 lines). Move any helper into `lib/`.
3. One clear responsibility per `lib/` file (m-file style). Prefer many small files.
4. Experiment scripts use Spyder `# %%` cells.
5. All tunable numbers live in `config/params.yaml` — no literals buried in `lib/`.
6. Outputs go to `results/figures` and `results/data` (git-ignored). Never commit data.
7. Docstrings must state physical **units** and array **shapes** (e.g. `x : (nx,) state`).
8. Code lives in `experiments/`; research writing in `docs/`. Each
   `experiments/run_NN_*.py` pairs with `docs/experiments/exp_NN_*.md` (same NN).
9. New plants subclass `Plant` (`lib/systems/plant.py`), register in
   `lib/systems/build.py`, get a `config/params.yaml` entry. Pinocchio imports stay
   confined to `lib/dynamics/`.

## Coding style & naming
- **State-space (plant-agnostic):** `x` state, `u` input, `y` output, `A B C D` system
  matrices, `K` feedback gain, `x_ref`/`x_des` setpoint, `nx nu ny` dimensions.
- **Robot plant:** `q v a`/`qdd` (config, velocity, acceleration), `tau` joint torques,
  `M C g` (mass matrix, Coriolis, gravity). `_des` desired, `_hat` estimate.
- **Arrays:** always `numpy.ndarray`, float64. Document shapes.
- **Plotting:** go through `lib/utils/plotting.py` for a consistent house style.
- **Imports:** `import numpy as np`, `import pinocchio as pin` (robot plant only).
  Explicit `lib` imports (`from lib.systems.plant import Plant`).

## Research workflow
1. New study -> `python scripts/new_experiment.py NN slug "Title"` (or `/new-experiment`).
   It scaffolds the paired `experiments/run_NN_*.py` + `docs/experiments/exp_NN_*.md`.
2. Put any new reusable routine in `lib/…`, with a docstring (units + shapes) and, if
   pure-numpy, a `tests/` unit test.
3. Keep the experiment script a readable narrative; record hypothesis/setup/results/
   discussion in the paired `docs/experiments/exp_NN_*.md`.
4. Save figures/data through `lib/utils` (per-run subdirs) so runs are reproducible.
5. Record methods in `docs/methodology/`, reading notes in `docs/literature/`, a
   one-line summary in `docs/research_notes.md`. Draft the paper in `docs/paper/`.

## Adding a new plant
A plant subclasses `Plant` (`lib/systems/plant.py`) and exposes `nx`, `nu`,
`dynamics(x, u, t) -> xdot` (shape `(nx,)`, float64), and `output(x, u, t) -> y`.
1. Pure-numpy plant -> new file in `lib/systems/` (no Pinocchio). Rigid-body/URDF plant
   -> `lib/dynamics/`, adapting `RobotModel`, Pinocchio imports confined there.
2. Docstrings give units + shapes; parameters come from config, never hard-coded.
3. Register in `lib/systems/build.py`; add a `config/params.yaml` block + `plant.type`.
4. Pure-numpy plants get a `tests/test_<plant>.py` (shapes, equilibrium, linearization).
5. `python scripts/verify.py` must exit 0 (pytest + the Pinocchio import-guard).

## Agent harness (verification & scaffolding)
This repo ships a light, mostly vendor-neutral harness so verification is enforced,
not merely requested:
- **`scripts/verify.py`** — the gate. Runs pytest + a Pinocchio import-guard (proves the
  core imports without Pinocchio) + advisory ruff (only if installed). Exit 0 = safe to
  claim done. Run it, or `make verify`, before reporting completion.
- **`scripts/new_experiment.py`** — deterministic experiment scaffolder (rule 8).
- **Claude Code glue** under `.claude/` (other tools ignore it, but may read it):
  - `settings.json` — a `Stop` hook runs the gate when code changed this session and
    blocks completion on failure; a `PostToolUse` hook arms it; a permissions allowlist
    pre-approves pytest/uv/python/git.
  - `agents/control-verifier.md` — an independent verification subagent (physical sanity
    checks: equilibria, integrator convergence, closed-loop stability, energy). Readable
    as plain markdown by any tool.
  - `commands/new-experiment.md` — the `/new-experiment` slash command.

## Build / test commands
```bash
uv sync                                       # core + dev (cvxpy, sympy; no Pinocchio)
uv sync --extra dynamics                      # + Pinocchio (Linux/macOS; Windows -> conda)
uv sync --extra opt                           # + CasADi + slycot
conda env create -f environment.yml && conda activate control-systems   # Pinocchio on Windows
pip install -r requirements.txt               # or plain pip, core deps only

python scripts/verify.py   # verification gate (pytest + import-guard + advisory ruff)
uv run pytest -q           # unit tests only          (conda/pip: `pytest -q`)
uv run python main.py      # end-to-end demo          (set plant.type in config first)
```

## Definition of done
- `python scripts/verify.py` exits 0: `pytest -q` passes for all pure-numpy/scipy code,
  and the core imports without Pinocchio.
- Pinocchio-dependent code is import-guarded so tests pass without it.
- New reusable routines have a docstring (units + shapes) and, if pure-numpy, a test.
- Physical invariants relevant to the change were checked, not assumed (equilibria,
  integrator convergence, closed-loop eigenvalues, `c2d` vs `expm`, energy conservation).
- No scope reduction, no deleted tests, no hard-coded parameters.

## AI usage disclosure (academic integrity)
This is research code. If AI assistance materially contributes to a publication, follow
the target venue's AI-disclosure policy and keep a short note of AI-assisted modules in
`docs/research_notes.md`.
