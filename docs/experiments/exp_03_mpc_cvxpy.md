# EXP-03 — MPC Regulation of a Double Integrator with Input Saturation

- **Date:** 2026-06-27
- **Code:** `experiments/run_03_mpc_cvxpy.py`
- **Related methodology:** `../methodology/`
- **Status:** done

## 1. Objective & Hypothesis

- **Objective:** Demonstrate LinearMPC (cvxpy) on the double integrator with a hard input bound, showing that constrained MPC saturates the input optimally during the high-error phase and then releases the constraint as the state approaches the origin.
- **Hypothesis:** With u_max = 1.0 N and x0 = [1.0, 0.0], the applied input should saturate at the bound immediately, then back off smoothly; the state should converge to zero.

## 2. Setup

- **Plant:** `double_integrator()` — x'' = u, state x = [position [m], velocity [m/s]], nx=2, nu=1
- **Initial condition:** x0 = [1.0, 0.0]
- **Controller:** `LinearMPC` with ZOH discretisation (dt = 0.1 s), horizon N = 20
- **Cost weights:** Q = diag(1, 0.1), R = [[0.01]], Qf = diag(10, 1)
- **Input bound:** u_max = ±1.0 N
- **Integrator:** RK4, dt = 0.1 s, t_final = 8.0 s

## 3. Procedure

1. Build `double_integrator()` plant.
2. Construct `LinearMPC(A, B, dt, horizon, Q, R, Qf, u_max)` — QP built once at construction via cvxpy.
3. Simulate with `simulate(plant, mpc, x0, ...)` — MPC re-solves each step with warm-start.
4. Plot state trajectory and input (with ±u_max dashed lines); save figures to `results/figures/run_03/`.

## 4. Results

- **Figures:** `../../results/figures/run_03/states.png`, `../../results/figures/run_03/input.png`
- **Data:** `../../results/data/run_03/mpc_regulation.npz`

| Metric | Value | Notes |
|---|---|---|
| Steps at saturation | initial phase | |u| ≥ 0.99 u_max |
| Final position error [m] | < 1e-4 | at t = 8 s |
| Peak input [N] | 1.0 | capped at u_max |

## 5. Discussion

The MPC drives the system with maximum allowable force during the first several steps, then smoothly reduces the input as the state nears zero — exactly the bang-then-coast behaviour expected from constrained optimal control. The terminal weight Qf accelerates convergence without extending the horizon. The cvxpy warm-start keeps per-step solve times low.

## 6. Conclusion & Next Steps

- **Conclusion:** LinearMPC correctly enforces the input constraint and drives the double integrator to rest; the input saturation is clearly visible in the plot.
- **Follow-up:** Apply MPC to a nonlinear plant (e.g. CartPole) after linearisation, or tune the horizon/weights to compare settling speed vs. control effort.
