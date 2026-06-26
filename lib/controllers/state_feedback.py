"""Static state-feedback controller  u = -K (x - x_ref).

The plant-agnostic generalization of the control law every modern-control method
produces: LQR (:mod:`lib.controllers.lqr`) and pole placement
(:mod:`lib.controllers.pole_placement`) both compute a gain ``K`` and then apply it
through this same law. Pure NumPy — works on any state ``x``.
"""

from __future__ import annotations

import numpy as np


class StateFeedback:
    """State-feedback law ``u = -K (x - x_ref)`` for a given gain ``K``.

    Parameters
    ----------
    K : (nu, nx) feedback gain.
    x_ref : (nx,), optional reference state to regulate to (default: origin).
    u_ref : (nu,), optional feedforward input added to the feedback (default: zeros).
    """

    def __init__(self, K, x_ref=None, u_ref=None) -> None:
        self.K = np.atleast_2d(np.asarray(K, dtype=float))
        nu, nx = self.K.shape
        self.x_ref = np.zeros(nx) if x_ref is None else np.asarray(x_ref, dtype=float)
        self.u_ref = np.zeros(nu) if u_ref is None else np.asarray(u_ref, dtype=float)

    def compute(self, x: np.ndarray) -> np.ndarray:
        """Return ``u = u_ref - K (x - x_ref)`` for state ``x`` (shape (nx,))."""
        x = np.asarray(x, dtype=float)
        return self.u_ref - self.K @ (x - self.x_ref)

    def __call__(self, t: float, x: np.ndarray) -> np.ndarray:
        """Sim-facing ``(t, x) -> u`` adapter (time-invariant law)."""
        return self.compute(x)
