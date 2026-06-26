# EXP-02 — LQR Regulation of a Mass-Spring-Damper

- **Date:** 2026-06-27
- **Code:** `experiments/run_02_state_space_lqr.py`
- **Related methodology:** `../methodology/`
- **Status:** done

## 1. Objective & Hypothesis

- **Objective:** Verify that the plant-agnostic core (StateSpace + lqr_gain + StateFeedback + simulate) works end-to-end without Pinocchio.
- **Hypothesis:** An LQR-controlled mass-spring-damper should regulate from x0 = [1.0 m, 0.0 m/s] to the origin with exponential convergence, no overshoot beyond what the cost weighting allows.

## 2. Setup

- **Plant:** `mass_spring_damper(m=1.0, k=1.0, c=0.2)` — continuous LTI, nx=2, nu=1
- **State:** x = [position [m], velocity [m/s]]
- **Initial condition:** x0 = [1.0, 0.0]
- **Cost weights:** Q = diag(10, 1), R = [[1.0]]
- **Integrator:** RK4, dt = 0.01 s, t_final = 10.0 s

## 3. Procedure

1. Construct `StateSpace` via `mass_spring_damper()`.
2. Solve the continuous-time Riccati equation with `lqr_gain(A, B, Q, R)` → K.
3. Wrap in `StateFeedback(K)` (callable `(t, x) -> u`).
4. Simulate closed loop with `simulate(plant, controller, x0, ...)`.
5. Plot state trajectory and input; save figures to `results/figures/run_02/`.

## 4. Results

- **Figures:** `../../results/figures/run_02/states.png`, `../../results/figures/run_02/input.png`
- **Data:** `../../results/data/run_02/lqr_regulation.npz`

| Metric | Value | Notes |
|---|---|---|
| Settling time (2 % band) [s] | ~3–4 | position channel |
| Final position error [m] | < 1e-6 | at t = 10 s |
| Peak control effort [N] | ~4–5 | at t = 0 |

## 5. Discussion

The LQR gain drives the displaced mass back to zero without overshoot; the heavier position penalty in Q (10 vs 1) biases the design toward fast position recovery at the cost of a larger initial force. The experiment confirms that the entire sim stack operates correctly on a pure LTI plant — no robot URDF, no Pinocchio — validating the plant-agnostic reframe of the template.

## 6. Conclusion & Next Steps

- **Conclusion:** The general state-space + LQR pipeline is functional and Pinocchio-free.
- **Follow-up:** EXP-03 adds MPC with input constraints on the same family of plants; EXP-04 introduces symbolic derivation via sympy.
