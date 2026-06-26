"""Unit test for lib.dynamics.linearize finite-difference math.

Verifies the linearization recovers (A, B) of a KNOWN linear system without needing
Pinocchio, by monkeypatching state_derivative with an analytic linear RHS.
"""

import numpy as np

from lib.dynamics import linearize as lin_mod


class _FakeRobot:
    nq = 2
    nv = 2


def test_linearize_recovers_known_linear_system(monkeypatch):
    """For xdot = A x + B tau, linearize must return A and B (finite differences)."""
    A_true = np.array([[0.0, 1.0, 0.0, 0.0],
                       [-3.0, -0.5, 1.0, 0.0],
                       [0.0, 0.0, 0.0, 1.0],
                       [0.5, 0.0, -2.0, -0.3]])
    B_true = np.array([[0.0, 0.0],
                       [1.0, 0.0],
                       [0.0, 0.0],
                       [0.0, 1.0]])

    def fake_state_derivative(robot, x, tau):
        return A_true @ x + B_true @ tau

    monkeypatch.setattr(lin_mod, "state_derivative", fake_state_derivative)

    A, B = lin_mod.linearize(_FakeRobot(), np.zeros(2), np.zeros(2), np.zeros(2))
    np.testing.assert_allclose(A, A_true, atol=1e-6)
    np.testing.assert_allclose(B, B_true, atol=1e-6)
