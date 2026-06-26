"""Continuous-to-discrete (c2d) conversion of an LTI state-space model.

Exact zero-order-hold discretization of  x' = A x + B u  over a sample period dt:

    x[k+1] = Ad x[k] + Bd u[k],   with   [Ad  Bd] = expm( [[A, B], [0, 0]] * dt ).

This is the matrix-exponential ("Van Loan") trick: stacking A and B into one
augmented matrix and taking a single ``scipy.linalg.expm`` gives both Ad and Bd
exactly (not a forward-Euler approximation). Pure SciPy — no Pinocchio.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np
from scipy.linalg import expm


def c2d(A, B, dt: float, method: str = "zoh") -> Tuple[np.ndarray, np.ndarray]:
    """Discretize ``x' = A x + B u`` to ``x[k+1] = Ad x[k] + Bd u[k]``.

    Parameters
    ----------
    A : (n, n) continuous state matrix.
    B : (n, m) continuous input matrix.
    dt : sample period [s] (> 0).
    method : 'zoh' (exact zero-order hold, default) or 'euler' (forward Euler,
             ``Ad = I + A dt``, ``Bd = B dt`` — first-order accurate).

    Returns
    -------
    Ad : (n, n) discrete state matrix.
    Bd : (n, m) discrete input matrix.
    """
    A = np.atleast_2d(np.asarray(A, dtype=float))
    B = np.atleast_2d(np.asarray(B, dtype=float))
    n, m = A.shape[0], B.shape[1]
    if A.shape != (n, n):
        raise ValueError(f"A must be square, got {A.shape}")
    if B.shape[0] != n:
        raise ValueError(f"B must have {n} rows, got {B.shape}")
    if dt <= 0:
        raise ValueError("dt must be positive")

    if method == "euler":
        return np.eye(n) + A * dt, B * dt
    if method == "zoh":
        # Van Loan: expm of the augmented block matrix yields [Ad, Bd] in the top rows.
        M = np.zeros((n + m, n + m))
        M[:n, :n] = A
        M[:n, n:] = B
        Md = expm(M * dt)
        return Md[:n, :n], Md[:n, n:]
    raise ValueError(f"unknown method {method!r} (use 'zoh' or 'euler')")
