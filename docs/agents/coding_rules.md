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

The canonical directory layout is maintained in
[`README.md`](../../README.md#directory-layout) as the single owner. Read it there;
do not duplicate the tree in this file. Boundaries that the rules below depend on:
`lib/` is the reusable toolbox, `lib/systems/` is pure NumPy/SciPy with no Pinocchio,
`lib/dynamics/` confines all Pinocchio imports, `experiments/` holds Spyder scripts,
`config/params.yaml` holds all tunables, and `scripts/` holds the verification and
scaffolding gates.

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

## Naming Rules

- Use lowercase `snake_case` for directory names and Python file names.
- Use the established experiment/write-up pairing:
  `experiments/run_NN_slug.py` and `docs/experiments/exp_NN_slug.md`.
- Use lowercase `snake_case` for ordinary variables, functions, methods,
  keyword arguments, config keys, and dataclass fields.
- Use `PascalCase` for classes and type-like containers such as dataclasses,
  `NamedTuple`, `TypedDict`, and enums.
- Use uppercase `SNAKE_CASE` for module-level constants that behave as fixed
  constants.
- Use a leading underscore only for internal helpers, private module variables,
  or implementation details that should not be part of the public API.
- Do not use excessive abbreviations. Names should remain meaningful and
  reviewable.
- Standard control-systems abbreviations are allowed when they match common
  notation: `x`, `u`, `y`, `A`, `B`, `C`, `D`, `K`, `Q`, `R`, `dt`, `nx`, `nu`,
  `ny`, `q`, `v`, `qdd`, `tau`, `M`, `g`, `x0`, `u_max`, `x_ref`, `x_des`,
  `q_des`, and similar local equation variables.
- Do not rename standard mathematical symbols into verbose names when the
  equation notation is clearer and the docstring states units and shapes.
- Name functions by the action/result they provide using Python `snake_case`,
  for example `build_plant`, `linearize_plant`, `lqr_gain`, `rk4_step`, and
  `save_trajectory`.
- Class names should name the concept or object, for example `Plant`,
  `StateSpace`, `RobotPlant`, and `StateFeedback`.
- Boolean variables and functions should read as predicates where practical,
  such as `is_controllable`, `has_pinocchio`, or `save_figures`.
- Test files use `test_*.py`; test functions use `test_*`.

## Helper Extraction

- Do not over-extract helper functions. Keep logic inline by default, and
  extract a helper only when at least one of these is true:
  - The same logic is needed in two or more real call sites.
  - The helper makes the call site materially clearer by hiding a noisy block
    behind a well-named operation.
  - The helper is needed to test or isolate a meaningful numerical or physical
    step.
- Helpers added only for anticipated reuse, aesthetic symmetry, or a notional
  line-count limit should be inlined back.

## Comments And Docstrings

- For Python code, keep comments and docstrings concise.
- Reusable `lib/` routines still need docstrings that state physical units and
  array shapes.
- Do not use verbose `description` / `input` / `output` / `todo` docstring
  templates unless explicitly requested.
- Put comments directly above complex algorithmic logic, physical assumptions,
  numerical tolerances, or invariants that are easy to break.
- Avoid comments that restate obvious code.

## Error Handling And Logging

- Wherever an error case can occur, make the error visibly detectable with a
  clear exception, assertion, or log message.
- Use `raise` for invalid external inputs and runtime failures that callers
  must handle.
- Use `assert` for internal development checks and invariants.
- Library code under `lib/` should use `logging` instead of `print()`.
- In library modules that log, use `logger = logging.getLogger(__name__)`.
- Configure logging only at entry points such as `main.py`, scripts, or
  experiments. Do not configure logging inside reusable libraries.
- During exception handling, preserve the original context. Use
  `logger.exception("...")` when logging an exception before re-raising.
- Log messages should be actionable: include the failing path, parameter, unit,
  tolerance, or alternative when that context matters.
- `print()` is acceptable in experiment scripts and scaffolders when it is part
  of the notebook-style narrative or command-line user feedback.

## Development Scope

- In one development step, implement one small, clearly scoped responsibility.
- The default implementation unit should be one function, one method, one
  experiment slice, or one small interface.
- Do not implement multiple responsibilities together in a single step unless
  the user explicitly asks for a larger slice.
- Do not add surrounding features, abstractions, or refactors that the user did
  not request.
- For larger features, add the minimum useful scaffold first and extend behavior
  step by step in later work.
- Keep each `lib/` module independently understandable and avoid unnecessary
  dependencies.

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

## Commit Message Rules

- Use a concise Conventional Commit-style subject by default:
  `<type>: <summary>`.
- Prefer the commit types already used in this repository history:
  - `docs`: documentation, research writing, citation metadata, or agent docs.
  - `fix`: bug fixes, stale-reference corrections, or safety hardening.
  - `feat`: new template capability, scaffold, workflow, or user-facing
    behavior.
  - `chore`: repository maintenance, agent harness work, or non-user-facing
    upkeep.
  - `build`: dependency, packaging, environment, or build-system changes.
- Keep the subject line short and specific. Name the changed behavior or
  structure, not the tool that made the change.
- Use a plain descriptive subject only when the change is a repository-wide
  rename, migration, or merge-style change that does not fit the common types.
- Do not use decorative emoji or AI-generated watermarks in commit messages.
- Before committing, stage only the intended files and review the staged diff.

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
