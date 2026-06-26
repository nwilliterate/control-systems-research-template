"""Closed-loop simulation with a zero-order-hold (ZOH) controller.

The control input is computed once per fixed time step and held constant while the
plant is integrated over that step. This is how a digital controller actually runs,
and it has two practical benefits over evaluating the controller inside every RK
sub-stage:

- A stateful controller (e.g. PID with an integrator) advances exactly once per
  step, not 4x per RK4 step.
- The applied torque is known and logged for every step (needed for torque/energy
  plots), instead of having to be re-derived afterwards.

A controller is any callable ``controller(t, q, v) -> tau`` returning a joint-torque
vector of shape (nv,). Build one with :func:`lib.controllers.factory.make_controller`.
"""

from __future__ import annotations

from typing import Callable, Tuple

import numpy as np

from lib.dynamics.forward_dynamics import state_derivative
from lib.dynamics.robot_model import RobotModel
from lib.integrators.runge_kutta import rk4_step, rk45_step

# A controller maps (time, positions, velocities) -> joint torques.
Controller = Callable[[float, np.ndarray, np.ndarray], np.ndarray]


def _step_fn(integrator: str):
    """Return a single-step integrator ``step(f, t, x, dt) -> x_next``."""
    if integrator == "rk4":
        return rk4_step
    if integrator == "rk45":
        # Use the 5th-order Dormand-Prince solution as a fixed-step stepper.
        return lambda f, t, x, dt: rk45_step(f, t, x, dt)[0]
    raise ValueError(f"unknown integrator {integrator!r} (use 'rk4' or 'rk45')")


def simulate(robot: RobotModel, controller: Controller, x0: np.ndarray,
             t_final: float, dt: float,
             integrator: str = "rk4") -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Simulate the closed loop with a zero-order-hold controller.

    Parameters
    ----------
    robot      : RobotModel
    controller : callable ``(t, q, v) -> tau`` returning shape (nv,) torques.
    x0         : (nq + nv,) initial stacked state [q, v].
    t_final    : end time [s] (start time is 0).
    dt         : fixed time step [s].
    integrator : 'rk4' (default) or 'rk45'.

    Returns
    -------
    t   : (N+1,) time grid [s].
    x   : (N+1, nq+nv) state trajectory; row k is the state at t[k].
    tau : (N, nv) applied torque held over step k (one row per step).
    """
    if dt <= 0:
        raise ValueError("dt must be positive")
    if t_final < 0:
        raise ValueError("t_final must be non-negative")

    step = _step_fn(integrator)
    x0 = np.asarray(x0, dtype=float).ravel()
    nq, nv = robot.nq, robot.nv

    n_steps = int(np.ceil(t_final / dt - 1e-9))
    t = dt * np.arange(n_steps + 1)
    x = np.empty((n_steps + 1, x0.size), dtype=float)
    tau = np.empty((n_steps, nv), dtype=float)
    x[0] = x0

    for k in range(n_steps):
        q, v = x[k, :nq], x[k, nq:]
        tau_k = np.asarray(controller(t[k], q, v), dtype=float)
        tau[k] = tau_k
        # Hold tau_k constant over the step (ZOH): the RHS ignores its own t/x torque.
        f = lambda t_, x_: state_derivative(robot, x_, tau_k)
        x[k + 1] = step(f, t[k], x[k], dt)

    return t, x, tau
