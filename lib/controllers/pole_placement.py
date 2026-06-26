"""Pole-placement (Ackermann / eigenstructure) state-feedback design.

Given a controllable LTI pair ``(A, B)`` and a set of desired closed-loop poles,
computes the gain ``K`` such that ``eig(A - B K)`` equals the requested poles, then
wraps it in a :class:`~lib.controllers.state_feedback.StateFeedback` law.

Uses ``python-control``'s :func:`control.place` (backed by **slycot** for the robust
MIMO algorithm) when available, falling back to ``scipy.signal.place_poles``. Pure
NumPy state — no Pinocchio.
"""

from __future__ import annotations

import numpy as np

from .state_feedback import StateFeedback


def place_gain(A, B, poles) -> np.ndarray:
    """Compute a state-feedback gain ``K`` placing ``eig(A - B K)`` at ``poles``.

    Parameters
    ----------
    A : (n, n) state matrix.
    B : (n, m) input matrix.
    poles : sequence of n desired closed-loop eigenvalues.

    Returns
    -------
    K : (m, n) gain such that ``A - B K`` has the requested spectrum.

    Notes
    -----
    Tries ``control.place`` first (robust MIMO placement via slycot); if
    python-control/slycot is unavailable it falls back to
    ``scipy.signal.place_poles``. Both require ``(A, B)`` controllable and at most
    one desired pole repeated more than ``rank(B)`` times.
    """
    A = np.atleast_2d(np.asarray(A, dtype=float))
    B = np.atleast_2d(np.asarray(B, dtype=float))
    poles = np.asarray(poles)

    try:
        import control

        return np.atleast_2d(np.asarray(control.place(A, B, poles), dtype=float))
    except Exception:
        from scipy.signal import place_poles

        return np.atleast_2d(place_poles(A, B, poles).gain_matrix)


def pole_placement(A, B, poles, x_ref=None, u_ref=None) -> StateFeedback:
    """Design a :class:`StateFeedback` that places the closed-loop poles.

    Parameters
    ----------
    A, B : LTI system matrices.
    poles : desired closed-loop eigenvalues.
    x_ref, u_ref : optional reference state / feedforward (see StateFeedback).

    Returns
    -------
    StateFeedback with the placement gain ``K``.
    """
    K = place_gain(A, B, poles)
    return StateFeedback(K, x_ref=x_ref, u_ref=u_ref)
