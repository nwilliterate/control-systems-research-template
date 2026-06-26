# CLAUDE.md — AI Collaboration Rules for this Robot-Control Research Project

This file tells Claude (and any AI assistant) how to work inside this repository.
It is the **single source of truth** for coding style, structure, and research workflow.

---

## 1. What this project is

An **academic research** codebase for **robot control**. The numerical stack is:

- **Pinocchio** — rigid-body dynamics (forward/inverse dynamics, Jacobians).
- **python-control** — classical / modern control design (LQR, transfer functions).
- **Runge-Kutta** — custom ODE integration of the robot state.

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
  dynamics/           Pinocchio model, forward dynamics, Jacobians, linearize
  integrators/        Runge-Kutta (rk4, rk45 drivers + steppers)
  controllers/        PID, computed-torque, LQR + factory (config-selected)
  sim/                simulate(): zero-order-hold closed-loop driver
  utils/              plotting, io, config loading
experiments/          Spyder cell scripts (# %%), one per study, numbered
models/               URDF robot descriptions
config/params.yaml    All parameters (sim, robot, controller, references)
results/figures       Saved plots (git-ignored)
results/data          Saved trajectories .npz (git-ignored)
tests/                pytest unit tests (numpy parts run without pinocchio)
docs/                 Research WRITING (separate from code)
  methodology/        Problem formulation, assumptions, controller design
  experiments/        One write-up per study: exp_NN_*.md (paired with run_NN)
  literature/         Paper reading notes, prior-work summaries
  paper/              Manuscript outline & drafts (ARS skills can assist)
  research_notes.md   Dated running log (short memos)
references/           Cited PDFs + references.bib
main.py               Concise end-to-end demo (load → control → simulate → plot)
```

## 4. Coding style

- **Naming:** physics-faithful symbols — `q`, `v`, `a`/`qdd`, `tau`, `M`, `C`, `g`.
  Use `_des` for desired/reference, `_hat` for estimates.
- **Arrays:** always `numpy.ndarray`, float64, column-consistent. Document shapes.
- **No silent magic:** read parameters from config, not literals buried in functions.
- **Plotting:** go through `lib/utils/plotting.py` for a consistent house style.
- **Imports:** `import numpy as np`, `import pinocchio as pin`. Keep `lib` imports
  explicit (`from lib.integrators.runge_kutta import rk4`).

## 5. Research workflow Claude should follow

1. New study → copy `experiments/template_experiment.py` to `experiments/run_NN_*.py`
   AND copy `docs/experiments/_experiment_template.md` to `docs/experiments/exp_NN_*.md`
   (same number NN pairs the code with its write-up).
2. Put any new reusable routine in `lib/…`, with a docstring + a `tests/` unit test
   if it is pure-numpy (no pinocchio dependency).
3. Keep the experiment script a readable narrative of the study; record the
   hypothesis/setup/results/discussion in the paired `docs/experiments/exp_NN_*.md`.
4. Save figures/data through `lib/utils` so runs are reproducible (per-run subdirs).
5. Record big-picture methods in `docs/methodology/`, reading notes in
   `docs/literature/`, and a one-line summary in `docs/research_notes.md`.
   When results accumulate, draft the paper in `docs/paper/`.

## 6. Verification expectations

- Before claiming something works, **run it**: `pytest -q` for library units, and run
  the relevant experiment script.
- Pinocchio may be unavailable on some machines (Windows pip). Pure-numpy code
  (integrators, PID, LQR) must work and be tested **without** pinocchio.
- Never delete a test to make it pass. Never reduce scope silently.

## 7. AI usage disclosure (academic integrity)

This is research code. If AI assistance materially contributes to a publication,
follow the target venue's AI-disclosure policy. Keep a short note of AI-assisted
modules in `docs/research_notes.md` when relevant.
