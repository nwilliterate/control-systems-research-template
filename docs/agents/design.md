# Design

This document is the global design guide for the control-systems research
template. It captures architecture and responsibility boundaries; detailed
coding rules remain in `docs/agents/coding_rules.md`.

## Project Design

### Project Overview

- This repository is an academic control-systems research template organized
  around state-space plants: `x' = f(x, u, t)`.
- `Plant` (`lib/systems/plant.py`) is the central abstraction. Anything with
  state `x`, input `u`, and derivative `xdot` can be modeled as a plant.
- The robot plant is an optional Pinocchio-backed example. Pure NumPy/SciPy
  plants (`double_integrator`, `mass_spring_damper`, `CartPole`) must continue
  to run without Pinocchio.
- The intended usage is MATLAB/Spyder-style research: readable experiment
  scripts, reusable math in `lib/`, and paired write-ups in `docs/`.

### Design Goals

- Keep the plant-agnostic core independent of robot-specific dependencies.
- Make physical units, array shapes, and numerical assumptions explicit.
- Keep experiments reproducible through `config/params.yaml`, `lib/utils`, and
  deterministic scaffolding scripts.
- Separate runnable experiment code from research writing and source-backed
  knowledge atoms.
- Prefer simple, inspectable numerical routines over clever abstractions.

### Core Concepts

- `Plant`: continuous-time system interface with `nx`, `nu`,
  `dynamics(x, u, t)`, and `output(x, u, t)`.
- `StateSpace`: linear time-invariant model `x'=Ax+Bu`, `y=Cx+Du`, plus
  controllability and conversion helpers.
- `Controller`: callable control law `(t, x) -> u`; examples include LQR,
  state feedback, PID, computed torque, pole placement, and MPC.
- `Integrator`: numerical time-stepper such as RK4 or RK45.
- `Simulation`: zero-order-hold loop that composes plant, controller,
  integrator, initial state, horizon, and step size.
- `Experiment`: Spyder-cell script in `experiments/` paired with a numbered
  markdown write-up in `docs/experiments/`.
- `Knowledge atom`: one cited, source-grounded research fact in
  `knowledge/claims/`.

### Responsibility Boundaries

- `lib/systems/` owns plant-agnostic abstractions and examples. It must not
  import Pinocchio.
- `lib/dynamics/` owns robot-specific rigid-body dynamics and is the only place
  Pinocchio imports belong.
- `lib/controllers/` owns reusable control laws and builders.
- `lib/integrators/` owns numerical integration routines.
- `lib/sim/` owns simulation orchestration, not experiment-specific analysis.
- `lib/utils/` owns config loading, plotting house style, and result IO.
- `experiments/` owns study scripts. These scripts should read as a narrative
  and import reusable work from `lib/`.
- `docs/` owns research writing. It is not a dumping ground for runnable code.
- `knowledge/` owns durable source-backed claims, not casual notes.
- `references/` owns bibliography identity and PDF hashes; PDFs stay
  git-ignored.
- `scripts/` owns verification and scaffolding helpers.

### Dependency Direction

- `main.py` and `experiments/*` may import from `lib/`.
- `lib/` must not import from `experiments/`, `docs/`, or `tests/`.
- `lib/systems/` must remain pure NumPy/SciPy and independent of Pinocchio.
- `lib/dynamics/` may adapt robot dynamics to the `Plant` interface.
- Controllers should depend on plant interfaces or matrices, not on experiment
  scripts.
- Plotting and IO should go through `lib/utils/` so outputs stay consistent and
  reproducible.

### Research Workflow Design

- A new study starts from `scripts/new_experiment.py` so code and write-up stay
  paired by number.
- Tunable parameters belong in `config/params.yaml`; experiment scripts should
  not hide magic numbers.
- New reusable math moves into `lib/` with units/shapes in docstrings and a
  focused test when it is pure NumPy/SciPy.
- Figures and data are saved under `results/figures` and `results/data`, which
  are not committed.
- Durable facts from papers/books are recorded in `knowledge/claims/` with
  BibTeX identity, page, and verbatim quote.

### Current Implementation Notes

- The default configuration currently supports `robot`, `double_integrator`,
  `mass_spring_damper`, and `cart_pole` plant types.
- `plant.type: robot` requires the Pinocchio-backed dynamics path; the other
  plants should work with the core install.
- `scripts/verify.py` is the completion gate for code changes.
- `scripts/verify_knowledge.py` is the completion gate for knowledge atoms.
- `docs/agents/progress.md` should stay newest-first and record the immediate
  next step after each completed slice.
