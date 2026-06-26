"""Numerical linearization of any :class:`~lib.systems.plant.Plant`.

Linearizes the (possibly nonlinear) state equation ``x' = f(x, u, t)`` about an
operating point ``(x0, u0)`` by central finite differences, producing the
continuous-time Jacobians

    delta_x' = A delta_x + B delta_u,   A = df/dx |_(x0,u0),   B = df/du |_(x0,u0).

This is the plant-agnostic generalization of the robot-specific
:func:`lib.dynamics.linearize.linearize`: it works on a cart-pole, a pendulum, or
any other plant, and at an equilibrium ``u0`` it yields the (A, B) an LQR or
pole-placement design needs. Pure NumPy.
"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

from .plant import Plant


def linearize_plant(plant: Plant, x0: np.ndarray, u0: Optional[np.ndarray] = None,
                    t: float = 0.0, eps: float = 1e-6) -> Tuple[np.ndarray, np.ndarray]:
    """Linearize ``plant.dynamics`` about ``(x0, u0)`` via central differences.

    Parameters
    ----------
    plant : Plant
    x0 : (nx,) operating-point state.
    u0 : (nu,) operating-point input; defaults to zeros. For an equilibrium pass the
         input that makes ``f(x0, u0) == 0`` (e.g. the gravity-cancelling input).
    t : float, time at which to linearize (for time-varying plants).
    eps : finite-difference step.

    Returns
    -------
    A : (nx, nx) state Jacobian df/dx.
    B : (nx, nu) input Jacobian df/du.
    """
    x0 = np.asarray(x0, dtype=float)
    nx = plant.nx
    nu = plant.nu
    u0 = np.zeros(nu) if u0 is None else np.asarray(u0, dtype=float)

    A = np.empty((nx, nx))
    for i in range(nx):
        dx = np.zeros(nx)
        dx[i] = eps
        f_plus = np.asarray(plant.dynamics(x0 + dx, u0, t), dtype=float)
        f_minus = np.asarray(plant.dynamics(x0 - dx, u0, t), dtype=float)
        A[:, i] = (f_plus - f_minus) / (2 * eps)

    B = np.empty((nx, nu))
    for j in range(nu):
        du = np.zeros(nu)
        du[j] = eps
        f_plus = np.asarray(plant.dynamics(x0, u0 + du, t), dtype=float)
        f_minus = np.asarray(plant.dynamics(x0, u0 - du, t), dtype=float)
        B[:, j] = (f_plus - f_minus) / (2 * eps)

    return A, B
