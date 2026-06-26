# CLAUDE.md — AI Collaboration Rules for this Control-Systems Research Project

This file tells Claude (and any AI assistant) how to work inside this repository.
It is the **single source of truth** for coding style, structure, and research workflow.

---

## 1. What this project is

An **academic research** codebase for **control-systems research** organised around
a general state-space **plant** abstraction (`x' = f(x, u, t)`). Any system with a
state `x`, an input `u`, and a continuous-time derivative is a plant. The numerical
stack is:

- **`lib/systems/`** — `Plant` ABC, `StateSpace` (LTI), `c2d` (ZOH discretization),
  `linearize_plant` (central-difference Jacobians), and example plants
  (`double_integrator`, `mass_spring_damper`, `CartPole`). Pure NumPy/SciPy.
- **Pinocchio** — rigid-body dynamics for the **robot plant** (`RobotPlant` in
  `lib/dynamics/`). The robot is *one* plant; all other plants run without Pinocchio.
- **python-control** — LQR (`lqr_gain`), pole placement (via slycot), transfer functions.
- **cvxpy** — convex optimisation, LMI / SDP, linear MPC (`lib/controllers/mpc.py`).
- **SymPy** — symbolic state-space derivation and Jacobian cross-checks.
- **CasADi** *(optional, `opt` extra)* — nonlinear MPC and autodiff.
- **slycot** *(optional, `opt` extra)* — MIMO routines (`place`, `care`, `hinfsyn`).
- **Runge-Kutta** — custom ODE integration (`lib/integrators/`): `rk4_step`, `rk45_step`.

The development philosophy is **"MATLAB/Spyder-style Python"**: code should be
*read like a clear lab notebook*, easy to follow top-to-bottom, with the heavy
machinery hidden inside well-named library functions.

---

## 2. The golden rules (do not violate)

1. **Common functions live in `lib/`.** Never inline reusable math/control/plotting
   logic into `main.py` or an experiment. Put it in the right `lib/` submodule and
   `import` it.
2. **`main.py` and experiment scripts stay short and readable.** They orchestrate;
   they do not implement. If a script grows a helper, move the helper into `lib/`.
3. **One logical function per file (m-file style).** Each file in `lib/` should do
   one clear thing. Prefer many small, well-named files over one big module.
4. **Experiments are Spyder cell scripts.** Use `# %%` cell separators so each block
   runs independently in Spyder (like MATLAB sections). See `experiments/`.
5. **All tunable numbers go in `config/params.yaml`,** never hard-coded in `lib/`.
6. **Results are written under `results/`** (figures → `results/figures`, data →
   `results/data`). Never commit generated data; `.gitignore` handles this.
7. **Docstrings state units and array shapes.** e.g. `q : (nq,) joint positions [rad]`.
   This is research code — physical correctness matters more than cleverness.

---

## 3. Directory map

```
lib/                  Reusable library (the "toolbox") — import from here
  systems/            Plant-agnostic core (pure NumPy/SciPy — no Pinocchio)
    plant.py          Plant ABC: nx, nu, dynamics(x,u,t)->xdot, output(x,u,t)->y
    state_space.py    StateSpace: LTI x'=Ax+Bu, y=Cx+Du; controllability helpers
    discretize.py     c2d(A,B,dt): ZOH exact discretization via matrix exponential
    linearize.py      linearize_plant(plant,x0,u0): central-difference A,B Jacobians
    examples.py       double_integrator(), mass_spring_damper(), CartPole
    build.py          build_plant(cfg): maps config plant.type to a concrete Plant
  dynamics/           Robot plant — Pinocchio rigid-body dynamics
    robot_plant.py    RobotPlant: adapts RobotModel to Plant (x=[q,v], u=tau)
    robot_model.py    Pinocchio URDF loader
    forward_dynamics.py  ABA, gravity, state_derivative
    linearize.py      robot-specific linearization
  integrators/        Runge-Kutta: rk4_step / rk45_step
  controllers/        Control laws — all expose (t,x)->u
    pid.py            PID (robot joint space)
    computed_torque.py  Computed-torque / inverse dynamics (robot plant)
    lqr.py            lqr_gain(A,B,Q,R) via python-control
    state_feedback.py StateFeedback: static gain K with optional setpoint x_ref
    pole_placement.py Pole placement via python-control / slycot
    mpc.py            Linear MPC via cvxpy
    factory.py        make_controller — robot-plant controller factory
    build.py          build_controller — plant-agnostic controller builder
  sim/                simulate(plant,controller,x0,t_final,dt,integrator)->(t,x,u)
  utils/              plotting, io, config loading
experiments/          Spyder cell scripts (# %%), one per study, numbered
models/               URDF robot descriptions
config/params.yaml    All parameters (sim, plant, robot, controller, references)
results/figures       Saved plots (git-ignored)
results/data          Saved trajectories .npz (git-ignored)
tests/                pytest unit tests (all pure-numpy code runs without Pinocchio)
docs/                 Research WRITING (separate from code)
  methodology/        Problem formulation, assumptions, controller design
  experiments/        One write-up per study: exp_NN_*.md (paired with run_NN)
  literature/         Paper reading notes, prior-work summaries
  paper/              Manuscript outline & drafts (ARS skills can assist)
  research_notes.md   Dated running log (short memos)
references/           Cited PDFs + references.bib
main.py               Concise end-to-end demo (plant-agnostic)
```

## 4. Coding style

- **Naming — state-space (plant-agnostic):** `x` (state vector), `u` (input/control),
  `y` (output), `A`, `B`, `C`, `D` (system matrices), `K` (feedback gain),
  `x_ref` / `x_des` (setpoint), `nx`, `nu`, `ny` (dimensions).
- **Naming — robot plant convention:** `q`, `v`, `a`/`qdd` (configuration, velocity,
  acceleration), `tau` (joint torques), `M`, `C`, `g` (mass matrix, Coriolis,
  gravity). Use `_des` for desired/reference, `_hat` for estimates.
- **Arrays:** always `numpy.ndarray`, float64, column-consistent. Document shapes.
- **No silent magic:** read parameters from config, not literals buried in functions.
- **Plotting:** go through `lib/utils/plotting.py` for a consistent house style.
- **Imports:** `import numpy as np`, `import pinocchio as pin` (robot plant only).
  Keep `lib` imports explicit (`from lib.systems.plant import Plant`,
  `from lib.integrators.runge_kutta import rk4_step`).

## 5. Research workflow Claude should follow

1. New study → copy `experiments/template_experiment.py` to `experiments/run_NN_*.py`
   AND copy `docs/experiments/_experiment_template.md` to `docs/experiments/exp_NN_*.md`
   (same number NN pairs the code with its write-up).
2. Put any new reusable routine in `lib/…`, with a docstring + a `tests/` unit test
   if it is pure-numpy (no Pinocchio dependency).
3. Keep the experiment script a readable narrative of the study; record the
   hypothesis/setup/results/discussion in the paired `docs/experiments/exp_NN_*.md`.
4. Save figures/data through `lib/utils` so runs are reproducible (per-run subdirs).
5. Record big-picture methods in `docs/methodology/`, reading notes in
   `docs/literature/`, and a one-line summary in `docs/research_notes.md`.
   When results accumulate, draft the paper in `docs/paper/`.
6. When adding a new plant, subclass `Plant` in `lib/systems/` (or `lib/dynamics/`
   for Pinocchio-backed plants), register it in `lib/systems/build.py`, and add a
   `config/params.yaml` entry. Keep the new plant free of Pinocchio unless it is a
   rigid-body system.

## 6. Verification expectations

- Before claiming something works, **run it**: `pytest -q` for library units, and run
  the relevant experiment script.
- Pinocchio may be unavailable on some machines (Windows pip). All `lib/systems/`,
  `lib/integrators/`, `lib/controllers/` code must work and be tested **without**
  Pinocchio. Only `lib/dynamics/` (robot plant) may depend on it.
- Never delete a test to make it pass. Never reduce scope silently.

## 7. AI usage disclosure (academic integrity)

This is research code. If AI assistance materially contributes to a publication,
follow the target venue's AI-disclosure policy. Keep a short note of AI-assisted
modules in `docs/research_notes.md` when relevant.
