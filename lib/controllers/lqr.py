"""Linear-Quadratic Regulator (LQR) gain computation and controller.

Designs an optimal state-feedback gain K for the linear system  x' = A x + B u
minimizing  J = ∫ (x^T Q x + u^T R u) dt.  The control law is  u = -K (x - x_ref).

Uses :func:`scipy.linalg.solve_continuous_are` so it works without Pinocchio.
For classical control workflows you may also use ``control.lqr`` from
python-control; both are equivalent.
"""

from __future__ import annotations

import numpy as np
from scipy.linalg import solve_continuous_are


def lqr_gain(A: np.ndarray, B: np.ndarray, Q: np.ndarray,
             R: np.ndarray) -> np.ndarray:
    """Continuous-time infinite-horizon LQR gain.

    Parameters
    ----------
    A : (n, n) state matrix.
    B : (n, m) input matrix.
    Q : (n, n) state-cost weight (symmetric PSD).
    R : (m, m) input-cost weight (symmetric PD).

    Returns
    -------
    K : (m, n) optimal feedback gain such that  u = -K x.
    """
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    Q = np.asarray(Q, dtype=float)
    R = np.asarray(R, dtype=float)

    P = solve_continuous_are(A, B, Q, R)        # Riccati solution
    K = np.linalg.solve(R, B.T @ P)             # K = R^{-1} B^T P
    return K


class LQR:
    """State-feedback LQR controller  u = -K (x - x_ref).

    Parameters
    ----------
    A, B, Q, R : array_like
        Linear model and cost weights (see :func:`lqr_gain`).
    x_ref : array_like, shape (n,), optional
        Reference state to regulate to (default: origin).
    """

    def __init__(self, A, B, Q, R, x_ref=None) -> None:
        self.K = lqr_gain(A, B, Q, R)
        n = self.K.shape[1]
        self.x_ref = np.zeros(n) if x_ref is None else np.asarray(x_ref, dtype=float)

    def compute(self, x: np.ndarray) -> np.ndarray:
        """Return the control input for state ``x`` (shape (n,)).

        Returns
        -------
        u : (m,) control input.
        """
        x = np.asarray(x, dtype=float)
        return -self.K @ (x - self.x_ref)
