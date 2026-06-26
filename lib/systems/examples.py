"""Canonical example plants — so the robot is not the only system in the template.

These are the textbook benchmarks of a control course, written against the
:class:`~lib.systems.plant.Plant` interface so they share the simulator and
controllers with the robot:

- :func:`double_integrator` — ``x'' = u`` (LTI), the simplest controllable plant.
- :func:`mass_spring_damper` — ``m x'' + c x' + k x = u`` (LTI).
- :class:`CartPole` — the nonlinear cart-pole / inverted-pendulum-on-a-cart.

Pure NumPy — no Pinocchio.
"""

from __future__ import annotations

import numpy as np

from .plant import Plant
from .state_space import StateSpace


def double_integrator() -> StateSpace:
    """Double integrator ``x'' = u`` with state ``x = [position, velocity]``.

    Returns
    -------
    StateSpace with nx=2, nu=1 (A=[[0,1],[0,0]], B=[[0],[1]]).
    """
    A = np.array([[0.0, 1.0], [0.0, 0.0]])
    B = np.array([[0.0], [1.0]])
    return StateSpace(A, B)


def mass_spring_damper(m: float = 1.0, k: float = 1.0, c: float = 0.2) -> StateSpace:
    """Mass-spring-damper ``m x'' + c x' + k x = u``; state ``x = [position, velocity]``.

    Parameters
    ----------
    m : mass [kg] (> 0).
    k : spring stiffness [N/m].
    c : damping coefficient [N*s/m].

    Returns
    -------
    StateSpace with nx=2, nu=1.
    """
    if m <= 0:
        raise ValueError("mass m must be positive")
    A = np.array([[0.0, 1.0], [-k / m, -c / m]])
    B = np.array([[0.0], [1.0 / m]])
    return StateSpace(A, B)


class CartPole(Plant):
    """Nonlinear cart-pole (inverted pendulum on a cart).

    State ``x = [p, theta, p_dot, theta_dot]`` (cart position [m], pole angle from
    upright [rad], and their rates); input ``u`` is the horizontal force on the cart
    [N]. The equations of motion are the standard frictionless cart-pole model.

    Parameters
    ----------
    m_cart : cart mass [kg].
    m_pole : pole mass [kg].
    length : pole half-length (pivot to centre of mass) [m].
    gravity : gravitational acceleration [m/s^2].
    """

    def __init__(self, m_cart: float = 1.0, m_pole: float = 0.1,
                 length: float = 0.5, gravity: float = 9.81) -> None:
        self.m_cart = float(m_cart)
        self.m_pole = float(m_pole)
        self.length = float(length)
        self.gravity = float(gravity)
        self.nx = 4
        self.nu = 1

    def dynamics(self, x: np.ndarray, u: np.ndarray, t: float = 0.0) -> np.ndarray:
        """Cart-pole state derivative; ``theta`` is measured from the upright."""
        x = np.asarray(x, dtype=float)
        _, theta, p_dot, theta_dot = x
        force = float(np.asarray(u, dtype=float).ravel()[0])

        mc, mp, ell, g = self.m_cart, self.m_pole, self.length, self.gravity
        sin, cos = np.sin(theta), np.cos(theta)
        total = mc + mp

        # Standard cart-pole equations (Florian 2007 sign convention, theta=0 upright).
        temp = (force + mp * ell * theta_dot**2 * sin) / total
        theta_acc = (g * sin - cos * temp) / (ell * (4.0 / 3.0 - mp * cos**2 / total))
        p_acc = temp - mp * ell * theta_acc * cos / total
        return np.array([p_dot, theta_dot, p_acc, theta_acc])
