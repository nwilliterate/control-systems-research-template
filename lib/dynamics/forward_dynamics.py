"""Forward dynamics and dynamics quantities for a :class:`RobotModel`.

The equation of motion is

    M(q) qdd + C(q, v) v + g(q) = tau

so the forward (direct) dynamics solve for the acceleration

    qdd = M(q)^{-1} ( tau - C(q,v) v - g(q) )

Pinocchio's Articulated Body Algorithm (``pin.aba``) computes this in O(n) without
forming/inverting M explicitly. Helpers for M, the nonlinear terms, and gravity are
provided for model-based controllers (e.g. computed torque).

All functions take a :class:`lib.dynamics.robot_model.RobotModel`.
"""

from __future__ import annotations

import numpy as np

from .robot_model import RobotModel


def forward_dynamics(robot: RobotModel, q: np.ndarray, v: np.ndarray,
                     tau: np.ndarray) -> np.ndarray:
    """Joint accelerations via the Articulated Body Algorithm (ABA).

    Parameters
    ----------
    robot : RobotModel
    q   : (nq,) joint positions [rad or m].
    v   : (nv,) joint velocities [rad/s or m/s].
    tau : (nv,) joint torques/forces [N*m or N].

    Returns
    -------
    qdd : (nv,) joint accelerations [rad/s^2 or m/s^2].
    """
    pin = robot._pin
    q = np.asarray(q, dtype=float)
    v = np.asarray(v, dtype=float)
    tau = np.asarray(tau, dtype=float)
    return pin.aba(robot.model, robot.data, q, v, tau)


def mass_matrix(robot: RobotModel, q: np.ndarray) -> np.ndarray:
    """Joint-space inertia matrix M(q) via CRBA.

    Returns
    -------
    M : (nv, nv) symmetric positive-definite inertia matrix.
    """
    pin = robot._pin
    q = np.asarray(q, dtype=float)
    M = pin.crba(robot.model, robot.data, q)
    # CRBA fills only the upper triangle; mirror it to get the full matrix.
    return np.triu(M) + np.triu(M, 1).T


def nonlinear_effects(robot: RobotModel, q: np.ndarray,
                      v: np.ndarray) -> np.ndarray:
    """Combined Coriolis/centrifugal + gravity terms  C(q,v) v + g(q).

    Returns
    -------
    b : (nv,) generalized bias forces [N*m or N].
    """
    pin = robot._pin
    q = np.asarray(q, dtype=float)
    v = np.asarray(v, dtype=float)
    return pin.nonLinearEffects(robot.model, robot.data, q, v)


def gravity(robot: RobotModel, q: np.ndarray) -> np.ndarray:
    """Gravity torque vector g(q).

    Returns
    -------
    g : (nv,) gravity generalized forces [N*m or N].
    """
    pin = robot._pin
    q = np.asarray(q, dtype=float)
    return pin.computeGeneralizedGravity(robot.model, robot.data, q)


def state_derivative(robot: RobotModel, x: np.ndarray,
                     tau: np.ndarray) -> np.ndarray:
    """Right-hand side f(x, tau) for the stacked state x = [q, v].

    Convenient to pass to the Runge-Kutta integrators as
    ``f = lambda t, x: state_derivative(robot, x, controller(t, x))``.

    Parameters
    ----------
    robot : RobotModel
    x   : (nq + nv,) stacked state [q, v].
    tau : (nv,) joint torques.

    Returns
    -------
    xdot : (nq + nv,) stacked derivative [v, qdd].

    Notes
    -----
    Assumes ``nq == nv`` (Euclidean configuration: revolute/prismatic joints), so a
    plain ``q_next = q + v*dt`` integration is valid. Models with ``nq > nv``
    (floating base, spherical/continuous joints) need manifold-aware integration via
    ``pin.integrate``; this helper rejects them rather than silently corrupting q.
    """
    if robot.nq != robot.nv:
        raise ValueError(
            f"state_derivative assumes nq == nv (got nq={robot.nq}, nv={robot.nv}); "
            "use pin.integrate for models with a non-Euclidean configuration manifold."
        )
    nq = robot.nq
    q = x[:nq]
    v = x[nq:]
    qdd = forward_dynamics(robot, q, v, tau)
    return np.concatenate([v, qdd])
