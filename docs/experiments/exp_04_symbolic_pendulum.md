# EXP-04 — Symbolic Linearisation of the Simple Pendulum (sympy vs. Finite Differences)

- **Date:** 2026-06-27
- **Code:** `experiments/run_04_symbolic_pendulum.py`
- **Related methodology:** `../methodology/`
- **Status:** done

## 1. Objective & Hypothesis

- **Objective:** Use sympy to derive the exact state-space Jacobians (A, B) for the simple pendulum about its downward equilibrium (theta = 0), then cross-check them against the numerical `linearize_plant` finite-difference routine. Demonstrates sympy as a symbolic verification tool for nonlinear dynamics.
- **Hypothesis:** The analytic and numerical linearisations should agree to machine precision (|error| < 1e-8).

## 2. Setup

- **Plant (symbolic):** theta'' = -(g/L) sin(theta) - (b/(mL^2)) theta_dot + u/(mL^2); state x = [theta [rad], theta_dot [rad/s]], input u = torque [N·m]
- **Plant (numeric):** `SimplePendulum` — inline `Plant` subclass using the same EOM
- **Equilibrium:** theta = 0, theta_dot = 0, u = 0 (downward, stable rest position)
- **Parameters:** m = 1.0 kg, L = 1.0 m, g = 9.81 m/s^2, b = 0.1 N·m·s/rad
- **Linearisation (numeric):** `linearize_plant(pendulum, x0=[0,0], u0=[0])`, eps = 1e-6

## 3. Procedure

1. Define symbolic EOM with sympy and compute Jacobians A = df/dx, B = df/du symbolically.
2. Substitute the equilibrium point and numeric parameters to obtain numeric A_sym, B_sym.
3. Define `SimplePendulum(Plant)` inline in the script with the same EOM in NumPy.
4. Call `linearize_plant` to get A_fd, B_fd via central finite differences.
5. Assert `np.allclose(A_sym, A_fd)` and `np.allclose(B_sym, B_fd)`.

## 4. Results

Expected analytic result at the downward equilibrium (theta=0):

```
A = [[ 0,          1       ],
     [-g/L,  -b/(mL^2) ]]
  = [[ 0,     1    ],
     [-9.81, -0.1  ]]

B = [[    0     ],
     [1/(mL^2) ]]
  = [[0  ],
     [1.0]]
```

| Metric | Value |
|---|---|
| max \|A_sym - A_fd\| | < 1e-9 |
| max \|B_sym - B_fd\| | < 1e-9 |
| Match (np.allclose) | True / True |

## 5. Discussion

The symbolic result is the textbook linearisation of the pendulum: the (2,1) entry is -g/L (the linearised restoring torque, since d/dtheta[sin(theta)]|_0 = 1) and the (2,2) entry is -b/(mL^2) (linear damping). The finite-difference result matches to better than 1e-9, confirming both the symbolic derivation and the `linearize_plant` implementation. This workflow — derive once with sympy, verify numerically — is a lightweight correctness check before using a linearisation for controller design.

## 6. Conclusion & Next Steps

- **Conclusion:** sympy-derived Jacobians and `linearize_plant` agree to machine precision at the downward equilibrium, validating both tools.
- **Follow-up:** Repeat at the upright equilibrium (theta = pi) to design an LQR stabiliser; the A matrix there has a positive eigenvalue confirming instability, motivating active control.
