"""Linear model-predictive control (MPC) via a cvxpy quadratic program.

At each step MPC re-solves a finite-horizon optimal-control problem over a
discrete-time LTI prediction model ``x[k+1] = Ad x[k] + Bd u[k]``,

    minimize   sum_{k=0..N-1} ( x[k]^T Q x[k] + u[k]^T R u[k] ) + x[N]^T Qf x[N]
    subject to x[0] = x_meas,  the model,  and (optional) input bounds |u| <= u_max,

and applies the first optimal input (receding horizon). The QP is built and solved
with **cvxpy**, demonstrating the optimization stack added to the template.

The discrete model is obtained from a continuous (A, B) via
:func:`lib.systems.discretize.c2d`. Requires cvxpy at construction time.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from lib.systems.discretize import c2d


class LinearMPC:
    """Receding-horizon linear MPC regulating an LTI plant to ``x_ref``.

    Parameters
    ----------
    A, B : continuous-time LTI matrices (discretized internally via ZOH).
    dt : control sample period [s].
    horizon : prediction horizon length N (number of steps).
    Q, R : (nx,nx) / (nu,nu) stage cost weights.
    Qf : (nx,nx) terminal weight, default equal to ``Q``.
    u_max : optional symmetric input bound (scalar or (nu,)); ``None`` = unconstrained.
    x_ref : (nx,) regulation target, default origin.
    """

    def __init__(self, A, B, dt: float, horizon: int, Q, R, Qf=None,
                 u_max: Optional[float] = None, x_ref=None) -> None:
        import cvxpy as cp

        self.Ad, self.Bd = c2d(A, B, dt)
        self.nx, self.nu = self.Bd.shape
        self.N = int(horizon)
        self.Q = np.atleast_2d(np.asarray(Q, dtype=float))
        self.R = np.atleast_2d(np.asarray(R, dtype=float))
        self.Qf = self.Q if Qf is None else np.atleast_2d(np.asarray(Qf, dtype=float))
        self.x_ref = np.zeros(self.nx) if x_ref is None else np.asarray(x_ref, dtype=float)
        self.u_max = u_max

        # Build the parametric QP once; re-solve each step by updating x0.
        self._x0 = cp.Parameter(self.nx)
        x = cp.Variable((self.nx, self.N + 1))
        u = cp.Variable((self.nu, self.N))
        cost = 0
        constraints = [x[:, 0] == self._x0]
        for k in range(self.N):
            dx = x[:, k] - self.x_ref
            cost += cp.quad_form(dx, self.Q) + cp.quad_form(u[:, k], self.R)
            constraints += [x[:, k + 1] == self.Ad @ x[:, k] + self.Bd @ u[:, k]]
            if u_max is not None:
                constraints += [cp.norm_inf(u[:, k]) <= u_max]
        cost += cp.quad_form(x[:, self.N] - self.x_ref, self.Qf)
        self._prob = cp.Problem(cp.Minimize(cost), constraints)
        self._u = u

    def compute(self, x: np.ndarray) -> np.ndarray:
        """Solve the horizon QP for measured ``x`` and return the first input ``u[0]``.

        Returns
        -------
        u : (nu,) optimal input to apply now.
        """
        self._x0.value = np.asarray(x, dtype=float).ravel()
        self._prob.solve(warm_start=True)
        if self._u.value is None:
            raise RuntimeError(f"MPC QP did not solve (status={self._prob.status})")
        return np.asarray(self._u.value[:, 0], dtype=float)

    def __call__(self, t: float, x: np.ndarray) -> np.ndarray:
        """Sim-facing ``(t, x) -> u`` adapter."""
        return self.compute(x)
