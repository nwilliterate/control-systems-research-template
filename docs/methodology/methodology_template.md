# Research Methodology — <Research Topic>

> Document the methodology for the whole study. Individual experiment records go in
> `../experiments/`; here you capture the big-picture **why / what / how**. Split
> into multiple files by topic if useful.

## 1. Problem Statement
- Research question (RQ):
- Target system (robot/plant):
- Control problem (regulation / tracking / trajectory optimization / ...):

## 2. Assumptions & Scope
- Modeling assumptions (rigid body, frictionless, ideal actuators, ...):
- Out of scope:

## 3. System Model
- Equation of motion:  `M(q) q̈ + C(q,v) v + g(q) = τ`
- State definition:  `x = [q, v]`,  input:  `u = τ`
- Frame / unit conventions (SI, frame definitions):
- Implementation mapping: Pinocchio `aba` (forward dynamics), `crba` (M),
  `nonLinearEffects` (C·v + g) → `lib/dynamics/forward_dynamics.py`

## 4. Controller Design
- Approach (PID / computed torque / LQR / MPC / ...):
- Design rationale and derivation:
- Gain selection method:
- Implementation: `lib/controllers/...`,  parameters: `config/params.yaml`

## 5. Numerical Integration
- Method: fixed-step RK4 / adaptive RK45 (`lib/integrators/runge_kutta.py`)
- Step size `dt`, stability/accuracy rationale:

## 6. Evaluation Metrics
- Quantitative metrics (settling time, overshoot, RMSE, control effort, ...):
- Baseline for comparison:

## 7. Reproducibility
- Environment: `environment.yml` (Pinocchio via conda-forge)
- Run: `python main.py`, `experiments/run_NN_*.py`
- Result storage: `results/figures`, `results/data` (per-experiment subfolders)

## References
- See `../literature/` and `../../references/references.bib`
