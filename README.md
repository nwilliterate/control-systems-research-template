# Robot-Control Research Template

A reusable Python template for **academic robot-control research**, designed for
**AI-assisted collaboration** (Claude Code / any agent) and a **MATLAB / Spyder-like**
development style.

> One project = one paper = one repo. Reusable math lives in `lib/`; studies live as
> readable scripts in `experiments/`.

## Stack

| Concern | Tool |
|---|---|
| Rigid-body dynamics | [Pinocchio](https://github.com/stack-of-tasks/pinocchio) (`pin.aba`, `crba`, …) |
| Control design | [python-control](https://python-control.org), `scipy.linalg` |
| Integration | custom **Runge-Kutta** (`lib/integrators/runge_kutta.py`) |
| Numerics / plots | NumPy, SciPy, Matplotlib |
| Config | a single `config/params.yaml` |

## Directory layout

```
lib/                  Reusable toolbox — import from here, never inline logic
  dynamics/           Pinocchio: model, forward dynamics (ABA/CRBA/gravity), Jacobians, linearize
  integrators/        Runge-Kutta: rk4 / rk45 drivers (+ rk4_step / rk45_step)
  controllers/        PID, computed-torque, LQR + factory (config-selected (t,q,v)->tau)
  sim/                simulate(): zero-order-hold closed-loop driver (logs tau)
  utils/              config loading, plotting house-style, result IO
experiments/          Spyder cell scripts (# %%); run_NN_*.py per study
models/               URDF robots (double_pendulum.urdf included)
config/params.yaml    All tunable parameters (sim, robot, controller, references)
results/figures       Saved plots (git-ignored)
results/data          Saved trajectories .npz (git-ignored)
tests/                pytest units (numpy parts run without Pinocchio)
docs/                 Research WRITING — methodology/ experiments/ literature/ paper/
references/           Cited PDFs + references.bib
main.py               Concise end-to-end demo
CLAUDE.md / AGENTS.md AI-collaboration rules
```

> **Code vs. writing:** `experiments/` holds runnable scripts; `docs/` holds the
> research write-ups. Each experiment `run_NN_*.py` is paired with a write-up
> `docs/experiments/exp_NN_*.md` of the same number. See `docs/README.md`.

## Install

Pinocchio installs most reliably through conda:

```bash
conda env create -f environment.yml
conda activate robot-control
```

Or, for the pure-numpy parts only (integrators, PID, LQR, plotting) without Pinocchio:

```bash
pip install -r requirements.txt
```

## Quick start

```bash
pytest -q             # run the unit tests — works on the pip-only install (no Pinocchio)
python main.py        # full demo: load model -> control -> simulate -> plot
                      #   NOTE: needs Pinocchio (use the conda env above)
```

The controller, integrator, and output flags are all chosen in `config/params.yaml`
(`controller.type`, `simulation.integrator`, `output.*`) — edit there, not in code.

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
