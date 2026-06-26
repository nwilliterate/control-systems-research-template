# Control-Systems Research Template

[![Use this template](https://img.shields.io/badge/Use%20this%20template-2ea44f?logo=github&logoColor=white)](https://github.com/nwilliterate/control-systems-research-template/generate)
[![tests](https://github.com/nwilliterate/control-systems-research-template/actions/workflows/tests.yml/badge.svg)](https://github.com/nwilliterate/control-systems-research-template/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![Stack](https://img.shields.io/badge/stack-Plant%20%2B%20python--control%20%2B%20cvxpy%20%2B%20Runge--Kutta-orange)

A reusable Python template for **academic control-systems research**, organised around
a general state-space **plant** abstraction (`x' = f(x, u)`), designed for
**AI-assisted collaboration** (Claude Code / any agent) and a **MATLAB / Spyder-like**
development style.

The unifying abstraction is the `Plant` ABC (`lib/systems/plant.py`): anything with a
state `x`, an input `u`, and a continuous-time derivative `x' = f(x, u, t)`. The
**robot** (`RobotPlant` backed by Pinocchio) is the flagship example plant, but
`double_integrator`, `mass_spring_damper`, and `CartPole` ship out of the box and
need no Pinocchio.

> **Starting a new study?** Click **[Use this template](https://github.com/nwilliterate/control-systems-research-template/generate)**
> (or `gh repo create my-study --private --template nwilliterate/control-systems-research-template --clone`)
> to spin off a fresh private repo, then fill in `config/`, `experiments/`, and `docs/`.

> One project = one paper = one repo. Reusable math lives in `lib/`; studies live as
> readable scripts in `experiments/`.

## Stack

| Concern | Tool |
|---|---|
| Plant abstraction | `lib/systems/` — `Plant` ABC, `StateSpace`, `c2d`, `linearize_plant`, example plants |
| Rigid-body dynamics (robot plant) | [Pinocchio](https://github.com/stack-of-tasks/pinocchio) (`pin.aba`, `crba`, …) via `lib/dynamics/` |
| Classical / modern control design | [python-control](https://python-control.org) — LQR, pole placement (via slycot) |
| Convex optimisation / LMI / MPC | [cvxpy](https://www.cvxpy.org) |
| Symbolic state-space derivation | [SymPy](https://www.sympy.org) |
| Nonlinear MPC / autodiff (optional) | [CasADi](https://web.casadi.org) (`opt` extra) |
| MIMO routines — `place`, `care`, `hinfsyn` (optional) | [slycot](https://github.com/python-control/Slycot) (`opt` extra) |
| Integration | custom **Runge-Kutta** (`lib/integrators/`) — `rk4_step`, `rk45_step` |
| Numerics / plots | NumPy, SciPy, Matplotlib |
| Config | a single `config/params.yaml` |

## Directory layout

```
lib/                  Reusable toolbox — import from here, never inline logic
  systems/            Plant core (no Pinocchio)
    plant.py          Plant ABC: nx, nu, dynamics(x,u,t)->xdot, output(x,u,t)->y
    state_space.py    StateSpace: LTI x'=Ax+Bu, y=Cx+Du; controllability; python-control interop
    discretize.py     c2d(A,B,dt): exact ZOH discretization (Van Loan / matrix-exponential)
    linearize.py      linearize_plant(plant,x0,u0): central-difference Jacobians A,B
    examples.py       double_integrator(), mass_spring_damper(), CartPole — pure NumPy
    build.py          build_plant(cfg): maps config plant.type to a concrete Plant
  dynamics/           Robot plant (Pinocchio-backed)
    robot_plant.py    RobotPlant: adapts RobotModel to the Plant interface (x=[q,v], u=tau)
    robot_model.py    RobotModel: Pinocchio URDF loader
    forward_dynamics.py  ABA, gravity, state_derivative
    linearize.py      robot-specific linearization utility
  integrators/        Runge-Kutta: rk4_step / rk45_step
  controllers/        Control laws — all return (t,x)->u callables
    pid.py            PID (joint-space, for robot plant)
    computed_torque.py  Computed-torque / inverse dynamics (robot plant)
    lqr.py            LQR: lqr_gain(A,B,Q,R) via python-control
    state_feedback.py StateFeedback: static gain K with optional setpoint x_ref
    pole_placement.py Pole placement via python-control / slycot
    mpc.py            Linear MPC via cvxpy
    factory.py        make_controller(cfg,plant,q_des,dt) — robot-plant controller factory
    build.py          build_controller(cfg,plant,dt) — plant-agnostic controller builder
  sim/                simulate(plant,controller,x0,t_final,dt,integrator)->(t,x,u): ZOH loop
  utils/              config loading, plotting house-style, result IO
experiments/          Spyder cell scripts (# %%); run_NN_*.py per study
models/               URDF robots (double_pendulum.urdf included)
config/params.yaml    All tunable parameters (sim, plant, robot, controller, references)
results/figures       Saved plots (git-ignored)
results/data          Saved trajectories .npz (git-ignored)
tests/                pytest units (all pure-numpy code runs without Pinocchio)
docs/                 Research WRITING — methodology/ experiments/ literature/ paper/
references/           Cited PDFs + references.bib
main.py               Concise end-to-end demo (plant-agnostic)
CLAUDE.md / AGENTS.md AI-collaboration rules
```

> **Code vs. writing:** `experiments/` holds runnable scripts; `docs/` holds the
> research write-ups. Each experiment `run_NN_*.py` is paired with a write-up
> `docs/experiments/exp_NN_*.md` of the same number. See `docs/README.md`.

> **Pinocchio is optional.** Set `plant.type` to `double_integrator`,
> `mass_spring_damper`, or `cart_pole` in `config/params.yaml` to run entirely on
> pure NumPy/SciPy. Only `plant.type: robot` requires Pinocchio.

## Install

**Recommended — [uv](https://docs.astral.sh/uv/)** (fast, reproducible via `uv.lock`):

```bash
uv sync                               # core stack + dev tools (pytest) into .venv
                                      # includes cvxpy and sympy
uv sync --extra dynamics              # + Pinocchio (Linux/macOS; Windows: use conda below)
uv sync --extra opt                   # + CasADi + slycot (nonlinear MPC, MIMO routines)
uv sync --extra dynamics --extra opt  # everything
```

For the full Pinocchio stack everywhere (and required on Windows), conda is most reliable:

```bash
conda env create -f environment.yml
conda activate control-systems
```

Or, with plain pip (pure-numpy/scipy/cvxpy/sympy parts; no Pinocchio):

```bash
pip install -r requirements.txt
pip install -e '.[opt]'   # add CasADi + slycot on top
```

## Quick start

```bash
uv run pytest -q      # unit tests — works with the core install (no Pinocchio needed)
uv run python main.py # end-to-end demo: build plant -> control -> simulate -> plot
                      # default plant.type is 'robot' — needs Pinocchio
                      # switch to 'double_integrator' in config/params.yaml for no-Pinocchio run
```

(With conda or a plain pip venv, drop the `uv run` prefix: `pytest -q`, `python main.py`.)

The plant, controller, integrator, and output flags are all chosen in `config/params.yaml`
(`plant.type`, `controller.type`, `simulation.integrator`, `output.*`) — edit there,
not in code.

In **Spyder**: open an `experiments/run_NN_*.py` file and run it cell-by-cell
(`Ctrl+Enter`) — each `# %%` block behaves like a MATLAB section.

## How to add a study (the workflow)

1. Copy `experiments/template_experiment.py` → `experiments/run_NN_description.py`,
   and `docs/experiments/_experiment_template.md` → `docs/experiments/exp_NN_description.md`.
2. Put any new reusable routine in the right `lib/` submodule (one job per file).
3. Add a `tests/` unit test for pure-numpy routines.
4. Save figures/data through `lib/utils` so runs are reproducible.
5. Write up hypothesis/results in `docs/experiments/exp_NN_*.md`; add a one-line
   summary to `docs/research_notes.md`.

See [`CLAUDE.md`](./CLAUDE.md) for the full coding rules and rationale.
