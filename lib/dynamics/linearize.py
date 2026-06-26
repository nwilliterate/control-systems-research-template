"""Numerical linearization of the robot dynamics about an operating point.

Produces the continuous-time state-space matrices (A, B) of

    delta_xdot = A delta_x + B delta_tau

for the stacked state x = [q, v], by central finite differences of the forward
dynamics. Useful to design an LQR controller for the (nonlinear) robot about a
setpoint. Assumes nq == nv (Euclidean configuration); see
:func:`lib.dynamics.forward_dynamics.state_derivative`.
"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

from .forward_dynamics import state_derivative
from .robot_model import RobotModel


def linearize(robot: RobotModel, q0: np.ndarray, v0: np.ndarray,
              tau0: Optional[np.ndarray] = None,
              eps: float = 1e-6) -> Tuple[np.ndarray, np.ndarray]:
    """Linearize xdot = f(x, tau) about (x0 = [q0, v0], tau0).

    Parameters
    ----------
    robot : RobotModel
    q0, v0 : (nv,) operating-point position and velocity.
    tau0 : (nv,) operating-point torque; defaults to zeros. For an equilibrium at
           rest use the gravity torque g(q0) (see lib.dynamics.forward_dynamics.gravity).
    eps : finite-difference step.

    Returns
    -------
    A : (2nv, 2nv) state Jacobian df/dx.
    B : (2nv, nv) input Jacobian df/dtau.
    """
    nv = robot.nv
    q0 = np.asarray(q0, dtype=float)
    v0 = np.asarray(v0, dtype=float)
    x0 = np.concatenate([q0, v0])
    tau0 = np.zeros(nv) if tau0 is None else np.asarray(tau0, dtype=float)

    n = x0.size
    A = np.empty((n, n))
    for i in range(n):
        dx = np.zeros(n)
        dx[i] = eps
        f_plus = state_derivative(robot, x0 + dx, tau0)
        f_minus = state_derivative(robot, x0 - dx, tau0)
        A[:, i] = (f_plus - f_minus) / (2 * eps)

    B = np.empty((n, nv))
    for j in range(nv):
        dtau = np.zeros(nv)
        dtau[j] = eps
        f_plus = state_derivative(robot, x0, tau0 + dtau)
        f_minus = state_derivative(robot, x0, tau0 - dtau)
        B[:, j] = (f_plus - f_minus) / (2 * eps)

    return A, B
