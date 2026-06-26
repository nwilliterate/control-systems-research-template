"""Runge-Kutta integrators for first-order ODE systems  dx/dt = f(t, x).

The robot state is stacked as  x = [q, v]  (positions then velocities), so a
second-order mechanical system is integrated as a first-order ODE by providing
``f(t, x) = [v, qdd(q, v, tau)]``.

Functions
---------
rk4_step  : one fixed-step classical RK4 update.
rk4       : fixed-step RK4 integration over a time grid.
rk45_step : one adaptive Dormand-Prince (RK45) step with error estimate.

All arrays are ``numpy.ndarray`` (float64).
"""

from __future__ import annotations

from typing import Callable, Tuple

import numpy as np

# Type alias: the right-hand side f(t, x) -> dx/dt
RHS = Callable[[float, np.ndarray], np.ndarray]


def rk4_step(f: RHS, t: float, x: np.ndarray, dt: float) -> np.ndarray:
    """Advance the state one classical 4th-order Runge-Kutta step.

    Parameters
    ----------
    f  : callable, ``f(t, x) -> dx/dt`` with x shape (n,), returns shape (n,).
    t  : current time [s].
    x  : current state, shape (n,).
    dt : time step [s].

    Returns
    -------
    x_next : state at ``t + dt``, shape (n,).
    """
    k1 = f(t, x)
    k2 = f(t + 0.5 * dt, x + 0.5 * dt * k1)
    k3 = f(t + 0.5 * dt, x + 0.5 * dt * k2)
    k4 = f(t + dt, x + dt * k3)
    return x + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def rk4(f: RHS, x0: np.ndarray, t0: float, t_final: float,
        dt: float) -> Tuple[np.ndarray, np.ndarray]:
    """Fixed-step RK4 integration of ``dx/dt = f(t, x)``.

    Parameters
    ----------
    f       : callable, ``f(t, x) -> dx/dt``.
    x0      : initial state, shape (n,).
    t0      : start time [s].
    t_final : end time [s].
    dt      : fixed step [s].

    Returns
    -------
    t_hist : time grid, shape (N+1,), equal to ``t0 + dt*arange(N+1)``.
    x_hist : state trajectory, shape (N+1, n) where row k is the state at t_hist[k].

    Notes
    -----
    The grid uses a fixed step, so ``t_hist[-1]`` is the smallest ``t0 + N*dt`` that
    reaches or exceeds ``t_final`` and may slightly overshoot when ``t_final - t0``
    is not an integer multiple of ``dt``.
    """
    if dt <= 0:
        raise ValueError("dt must be positive")
    if t_final < t0:
        raise ValueError("t_final must be >= t0")

    x0 = np.asarray(x0, dtype=float).ravel()
    n_steps = int(np.ceil((t_final - t0) / dt - 1e-9))
    t_hist = t0 + dt * np.arange(n_steps + 1)
    x_hist = np.empty((n_steps + 1, x0.size), dtype=float)

    x_hist[0] = x0
    for k in range(n_steps):
        x_hist[k + 1] = rk4_step(f, t_hist[k], x_hist[k], dt)
    return t_hist, x_hist


# --- Adaptive Dormand-Prince (RK45) -----------------------------------------
# Butcher tableau coefficients for the Dormand-Prince 5(4) pair.
_C = np.array([0.0, 1 / 5, 3 / 10, 4 / 5, 8 / 9, 1.0, 1.0])
_A = [
    [],
    [1 / 5],
    [3 / 40, 9 / 40],
    [44 / 45, -56 / 15, 32 / 9],
    [19372 / 6561, -25360 / 2187, 64448 / 6561, -212 / 729],
    [9017 / 3168, -355 / 33, 46732 / 5247, 49 / 176, -5103 / 18656],
    [35 / 384, 0.0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84],
]
# 5th-order solution weights (b) and 4th-order error-estimate weights (b*).
_B5 = np.array([35 / 384, 0.0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84, 0.0])
_B4 = np.array([5179 / 57600, 0.0, 7571 / 16695, 393 / 640,
                -92097 / 339200, 187 / 2100, 1 / 40])


def rk45_step(f: RHS, t: float, x: np.ndarray,
              dt: float) -> Tuple[np.ndarray, np.ndarray]:
    """One adaptive Dormand-Prince RK45 step.

    Returns both the 5th-order solution and a local error estimate so a caller
    can implement step-size control. For most studies prefer :func:`rk4` (simple,
    deterministic) or ``scipy.integrate.solve_ivp(method="RK45")`` for production.

    Parameters
    ----------
    f, t, x, dt : see :func:`rk4_step`.

    Returns
    -------
    x_next : 5th-order state estimate at ``t + dt``, shape (n,).
    err    : per-component error estimate (|5th - 4th|), shape (n,).
    """
    n = x.size
    k = np.empty((7, n), dtype=float)
    k[0] = f(t, x)
    for i in range(1, 7):
        xi = x + dt * sum(_A[i][j] * k[j] for j in range(i))
        k[i] = f(t + _C[i] * dt, xi)

    x5 = x + dt * (_B5 @ k)
    x4 = x + dt * (_B4 @ k)
    return x5, np.abs(x5 - x4)


def rk45(f: RHS, x0: np.ndarray, t0: float, t_final: float,
         dt0: float = 1e-2, rtol: float = 1e-6, atol: float = 1e-9,
         dt_min: float = 1e-8, dt_max: float = np.inf
         ) -> Tuple[np.ndarray, np.ndarray]:
    """Adaptive Dormand-Prince (RK45) integration with step-size control.

    Wraps :func:`rk45_step`: accepts a step when the estimated error is within the
    tolerance ``atol + rtol*|x|``, then grows/shrinks ``dt`` for the next step. The
    output grid is non-uniform (the integrator chose the points).

    Parameters
    ----------
    f       : callable ``f(t, x) -> dx/dt``.
    x0      : initial state, shape (n,).
    t0, t_final : start/end time [s].
    dt0     : initial step guess [s].
    rtol, atol : relative/absolute error tolerances.
    dt_min, dt_max : bounds on the adaptive step.

    Returns
    -------
    t_hist : (M,) non-uniform time grid, ending exactly at ``t_final``.
    x_hist : (M, n) state trajectory.
    """
    if dt0 <= 0:
        raise ValueError("dt0 must be positive")
    if t_final < t0:
        raise ValueError("t_final must be >= t0")

    x0 = np.asarray(x0, dtype=float).ravel()
    t, x, dt = t0, x0, min(dt0, dt_max)
    t_hist, x_hist = [t0], [x0]

    while t < t_final:
        dt = min(dt, t_final - t)
        x_new, err = rk45_step(f, t, x, dt)
        scale = atol + rtol * np.maximum(np.abs(x), np.abs(x_new))
        err_norm = np.sqrt(np.mean((err / scale) ** 2))

        if err_norm <= 1.0 or dt <= dt_min:
            t += dt
            x = x_new
            t_hist.append(t)
            x_hist.append(x)
        # 5th-order step-size update (0.9 safety factor), clamped for stability.
        factor = 0.9 * (err_norm ** -0.2) if err_norm > 0 else 5.0
        dt = float(np.clip(dt * np.clip(factor, 0.2, 5.0), dt_min, dt_max))

    return np.array(t_hist), np.array(x_hist)
