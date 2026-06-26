# EXP-01 — Free Response of the Double Pendulum

- **Date:** 2026-06-26
- **Code:** `experiments/run_01_free_simulation.py`
- **Related methodology:** `../methodology/methodology_template.md`
- **Status:** example (template demo)

## 1. Objective & Hypothesis
- Objective: sanity-check that the dynamics model (Pinocchio) + RK4 integration
  loop work correctly.
- Hypothesis: with zero input torque (`τ = 0`), the double pendulum exhibits a
  nonlinear (chaotic) free oscillation under gravity.

## 2. Setup
- Robot/model: `models/double_pendulum.urdf` (2-DOF, links 1 m / 1 kg)
- Initial conditions: `q0 = [0.5, 0.0]` rad, `v0 = [0.0, 0.0]` rad/s
- Controller: none (`τ = 0`)
- Integrator: RK4, `dt = 1e-3` s, `t_final = 5.0` s

## 3. Procedure
1. Load the URDF with `RobotModel`.
2. Define the closed-loop RHS `f(t,x) = state_derivative(robot, x, 0)`.
3. Integrate with `rk4`, then plot and save the joint-position trajectories.

## 4. Results
- Figures: `../../results/figures/run_01/free_response.png`
- Data: `../../results/data/run_01/free_response.npz`
- _(Fill in after running — joint-angle time response, energy-conservation trend, etc.)_

## 5. Discussion
- _(e.g., how well energy is conserved / drifts over long horizons under fixed-step RK4)_

## 6. Conclusion & Next Steps
- Conclusion: validates the dynamics + integration pipeline.
- Next: add a controller (computed-torque / LQR) in EXP-02 and measure regulation
  performance.
