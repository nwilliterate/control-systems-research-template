# Coding Rules

This file is the single source of coding and research-code rules for this
repository. Root `AGENTS.md` is the entrypoint; this file holds the detailed
project rules.

Development philosophy: **MATLAB/Spyder-style Python**. Code should read like a
clear lab notebook, top-to-bottom, with heavy machinery hidden inside
well-named `lib/` functions. This is research code: **physical correctness
matters more than cleverness**.

## Project At A Glance

- Domain: **control-systems** academic research: state-space plants
  (`x' = f(x, u, t)`). Any system with a state `x`, input `u`, and derivative is
  a plant.
- The **robot** (`RobotPlant`, Pinocchio-backed) is the flagship example plant;
  other built-in plants (`double_integrator`, `mass_spring_damper`, `CartPole`)
  need no Pinocchio.
- Stack: `lib/systems/` (Plant ABC + LTI tools) + **Pinocchio** (robot plant,
  `lib/dynamics/`) + **python-control** (LQR, pole placement) + **cvxpy**
  (MPC / convex opt) + **SymPy** (symbolic) + **Runge-Kutta** (integration).
- Optional extras (`opt`): **CasADi** (nonlinear MPC) + **slycot** (MIMO
  routines).

## Directory Map

```text
lib/                  Reusable toolbox - import from here, never inline into scripts
  systems/            Plant-agnostic core (pure NumPy/SciPy - NO Pinocchio)
    plant.py          Plant ABC: nx, nu, dynamics(x,u,t)->xdot, output(x,u,t)->y
    state_space.py    StateSpace LTI x'=Ax+Bu, y=Cx+Du; controllability helpers
    discretize.py     c2d(A,B,dt): ZOH exact discretization via matrix exponential
    linearize.py      linearize_plant(plant,x0,u0): central-difference A,B Jacobians
    examples.py       double_integrator(), mass_spring_damper(), CartPole
    build.py          build_plant(cfg): maps config plant.type -> concrete Plant
  dynamics/           Robot plant - Pinocchio rigid-body dynamics (imports confined here)
  integrators/        Runge-Kutta: rk4_step / rk45_step
  controllers/        Control laws (t,x)->u: pid, computed_torque, lqr, state_feedback,
                      pole_placement, mpc, factory (robot), build (plant-agnostic)
  sim/                simulate(plant,controller,x0,t_final,dt,integrator)->(t,x,u)
  utils/              Plotting, IO, config loading
experiments/          Spyder cell scripts (# %%); one per study: run_NN_*.py
models/               URDF robot descriptions
config/params.yaml    ALL tunable numbers (sim, plant, robot, controller, references)
results/figures       Saved plots (git-ignored)
results/data          Saved .npz files (git-ignored)
tests/                pytest units (all pure-numpy code runs without Pinocchio)
docs/                 Research writing: methodology/, experiments/, literature/, paper/
docs/agents/          Agent-facing rules, design notes, persona, progress log
knowledge/            Source-grounded knowledge atoms: claims/*.md
references/           references.bib + pdfs/manifest.yaml (PDFs are git-ignored)
scripts/              verify.py, verify_knowledge.py, new_experiment.py, new_claim.py
main.py               Concise end-to-end demo (plant-agnostic)
```

## Hard Rules

1. Reusable logic goes in `lib/`. Scripts (`main.py`, `experiments/*`) only
   orchestrate.
2. `main.py` stays concise (target < 60 lines). Move helpers into `lib/`.
3. One clear responsibility per `lib/` file (m-file style). Prefer many small
   files.
4. Experiment scripts use Spyder `# %%` cells.
5. All tunable numbers live in `config/params.yaml`; do not bury literals in
   `lib/`.
6. Outputs go to `results/figures` and `results/data` (git-ignored). Never
   commit data.
7. Docstrings must state physical **units** and array **shapes** (for example,
   `x : (nx,) state`).
8. Code lives in `experiments/`; research writing lives in `docs/`. Each
   `experiments/run_NN_*.py` pairs with `docs/experiments/exp_NN_*.md`
   using the same `NN`.
9. New plants subclass `Plant` (`lib/systems/plant.py`), register in
   `lib/systems/build.py`, get a `config/params.yaml` entry, and keep
   Pinocchio imports confined to `lib/dynamics/`.
10. After a coding task or substantial research-documentation task, update
    `docs/agents/progress.md` with the completed work, current result, and next
    planned goal.

## Coding Style And Naming

- **State-space (plant-agnostic):** `x` state, `u` input, `y` output,
  `A B C D` system matrices, `K` feedback gain, `x_ref`/`x_des` setpoint, and
  `nx nu ny` dimensions.
- **Robot plant:** `q v a`/`qdd` (configuration, velocity, acceleration),
  `tau` joint torques, `M C g` (mass matrix, Coriolis, gravity). Use `_des` for
  desired values and `_hat` for estimates.
- **Arrays:** always `numpy.ndarray`, float64. Document shapes.
- **Plotting:** go through `lib/utils/plotting.py` for consistent house style.
- **Imports:** use `import numpy as np`; use `import pinocchio as pin` only in
  robot-plant code. Use explicit `lib` imports, such as
  `from lib.systems.plant import Plant`.
- Wildcard imports are prohibited.
- Keep comments concise. Use comments for physical assumptions, non-obvious
  numerical choices, or invariants that are easy to break.

## Research Workflow

1. New study:
   `python scripts/new_experiment.py NN slug "Title"` (or `/new-experiment`).
   This scaffolds the paired `experiments/run_NN_*.py` and
   `docs/experiments/exp_NN_*.md`.
2. Put new reusable routines in `lib/...`, with a docstring that states units
   and shapes. If the routine is pure NumPy/SciPy, add a focused `tests/` unit
   test.
3. Keep the experiment script a readable narrative; record hypothesis, setup,
   results, and discussion in the paired `docs/experiments/exp_NN_*.md`.
4. Save figures/data through `lib/utils` per-run helpers so runs are
   reproducible.
5. Record methods in `docs/methodology/`, reading notes in `docs/literature/`,
   a one-line summary in `docs/research_notes.md`, and paper drafts in
   `docs/paper/`.
6. Capture durable, source-backed facts as knowledge atoms:
   `python scripts/new_claim.py <id> --cite <bibkey> --page <N> "<claim>"`
   (or `/new-claim`). Paste the verbatim quote and register the source in
   `references/references.bib` plus `references/pdfs/manifest.yaml`.
   Never overwrite a fact; supersede it with `supersedes` / `superseded_by` so
   history survives. `python scripts/verify_knowledge.py` must exit 0.

## Adding A New Plant

A plant subclasses `Plant` (`lib/systems/plant.py`) and exposes `nx`, `nu`,
`dynamics(x, u, t) -> xdot` with shape `(nx,)` and `output(x, u, t) -> y`.

1. Pure-NumPy plant: add a new file in `lib/systems/` with no Pinocchio import.
   Rigid-body/URDF plant: add code under `lib/dynamics/`, adapting
   `RobotModel`, with Pinocchio imports confined there.
2. Docstrings give units and shapes; parameters come from config, never
   hard-coded.
3. Register the plant in `lib/systems/build.py`; add a `config/params.yaml`
   block and `plant.type` option.
4. Pure-NumPy plants get a `tests/test_<plant>.py` covering shapes,
   equilibrium, and linearization.
5. `python scripts/verify.py` must exit 0 (pytest + Pinocchio import guard).

## Agent Harness

This repo ships a light, mostly vendor-neutral harness so verification is
enforced, not merely requested:

- `scripts/verify.py`: the code gate. Runs pytest, a Pinocchio import guard
  proving core imports work without Pinocchio, and advisory ruff if installed.
  Exit 0 means it is safe to claim the code slice is done. Run it, or
  `make verify`, before reporting completion.
- `scripts/new_experiment.py`: deterministic experiment scaffolder.
- `scripts/verify_knowledge.py`: the knowledge gate. Rejects any
  `knowledge/claims/` atom that is not traceable to a source: unknown/missing
  BibTeX `cite`, no `page` or verbatim quote for `extracted`, no
  `derived_from` for `inferred`, or broken supersede/contradict links.
- `scripts/new_claim.py` and `scripts/hash_pdf.py`: knowledge atom and PDF
  manifest helpers.
- Claude Code glue under `.claude/` may exist for Claude-specific hooks and
  commands. Other agents may read it as plain markdown/config, but repository
  policy remains in `AGENTS.md` and `docs/agents/`.

## Build And Test Commands

```bash
uv sync                                       # core + dev (cvxpy, sympy; no Pinocchio)
uv sync --extra dynamics                      # + Pinocchio (Linux/macOS; Windows -> conda)
uv sync --extra opt                           # + CasADi + slycot
conda env create -f environment.yml && conda activate control-systems
pip install -r requirements.txt               # plain pip, core deps only

python scripts/verify.py   # verification gate (pytest + import guard + advisory ruff)
uv run pytest -q           # unit tests only
uv run python main.py      # end-to-end demo (set plant.type in config first)
```

## Definition Of Done

- `python scripts/verify.py` exits 0: `pytest -q` passes for all pure
  NumPy/SciPy code, and the core imports without Pinocchio.
- Pinocchio-dependent code is import-guarded so tests pass without it.
- New reusable routines have a docstring with units and shapes and, if
  pure-NumPy/SciPy, a test.
- Physical invariants relevant to the change were checked, not assumed:
  equilibria, integrator convergence, closed-loop eigenvalues, `c2d` vs
  `expm`, energy conservation, or the relevant local equivalent.
- No scope reduction, no deleted tests, no hard-coded parameters.
- `docs/agents/progress.md` reflects what changed, the current result, and the
  next follow-up.

## AI Usage Disclosure

This is research code. If AI assistance materially contributes to a
publication, follow the target venue's AI-disclosure policy and keep a short
note of AI-assisted modules in `docs/research_notes.md`.
