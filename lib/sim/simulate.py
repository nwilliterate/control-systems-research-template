"""Closed-loop simulation of any plant with a zero-order-hold (ZOH) controller.

The control input is computed once per fixed time step and held constant while the
plant is integrated over that step. This is how a digital controller actually runs,
and it has two practical benefits over evaluating the controller inside every RK
sub-stage:

- A stateful controller (e.g. PID with an integrator) advances exactly once per
  step, not 4x per RK4 step.
- The applied input is known and logged for every step (needed for input/energy
  plots), instead of having to be re-derived afterwards.

The simulator is plant-agnostic: it drives any :class:`lib.systems.plant.Plant`
(the robot via :class:`lib.dynamics.robot_plant.RobotPlant`, an LTI
:class:`lib.systems.state_space.StateSpace`, a cart-pole, ...). A controller is any
callable ``controller(t, x) -> u`` returning an input vector of shape (nu,); build a
robot one with :func:`lib.controllers.factory.make_controller`.
"""

from __future__ import annotations

from typing import Callable, Tuple

import numpy as np

from lib.systems.plant import Plant
from lib.integrators.runge_kutta import rk4_step, rk45_step

# A controller maps (time, full state) -> control input.
Controller = Callable[[float, np.ndarray], np.ndarray]


def _step_fn(integrator: str):
    """Return a single-step integrator ``step(f, t, x, dt) -> x_next``."""
    if integrator == "rk4":
        return rk4_step
    if integrator == "rk45":
        # Use the 5th-order Dormand-Prince solution as a fixed-step stepper.
        return lambda f, t, x, dt: rk45_step(f, t, x, dt)[0]
    raise ValueError(f"unknown integrator {integrator!r} (use 'rk4' or 'rk45')")


def simulate(plant: Plant, controller: Controller, x0: np.ndarray,
             t_final: float, dt: float,
             integrator: str = "rk4") -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Simulate the closed loop with a zero-order-hold controller.

    Parameters
    ----------
    plant      : Plant
        Any plant exposing ``nx``, ``nu`` and ``dynamics(x, u, t) -> xdot``.
    controller : callable ``(t, x) -> u`` returning shape (nu,) inputs.
    x0         : (nx,) initial state.
    t_final    : end time [s] (start time is 0).
    dt         : fixed time step [s].
    integrator : 'rk4' (default) or 'rk45'.

    Returns
    -------
    t : (N+1,) time grid [s].
    x : (N+1, nx) state trajectory; row k is the state at t[k].
    u : (N, nu) applied input held over step k (one row per step).
    """
    if dt <= 0:
        raise ValueError("dt must be positive")
    if t_final < 0:
        raise ValueError("t_final must be non-negative")

    step = _step_fn(integrator)
    x0 = np.asarray(x0, dtype=float).ravel()
    nu = plant.nu

    n_steps = int(np.ceil(t_final / dt - 1e-9))
    t = dt * np.arange(n_steps + 1)
    x = np.empty((n_steps + 1, x0.size), dtype=float)
    u = np.empty((n_steps, nu), dtype=float)
    x[0] = x0

    for k in range(n_steps):
        u_k = np.asarray(controller(t[k], x[k]), dtype=float).ravel()
        u[k] = u_k
        # Hold u_k constant over the step (ZOH): the RHS ignores its own t/x input.
        f = lambda t_, x_: plant.dynamics(x_, u_k, t_)
        x[k + 1] = step(f, t[k], x[k], dt)

    return t, x, u
