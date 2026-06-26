"""Unit tests for the plant-agnostic state-space controllers.

StateFeedback and pole placement are pure-numpy/SciPy; the MPC test is skipped when
cvxpy is unavailable. Each test asserts a meaningful closed-loop property rather than
just "it runs".
"""

import numpy as np
import pytest

from lib.controllers.state_feedback import StateFeedback
from lib.controllers.pole_placement import pole_placement, place_gain
from lib.sim.simulate import simulate
from lib.systems import examples


def test_state_feedback_law():
    """u = u_ref - K (x - x_ref)."""
    K = np.array([[2.0, 3.0]])
    sf = StateFeedback(K, x_ref=np.array([1.0, 0.0]))
    # At the reference the feedback is zero.
    assert np.allclose(sf.compute([1.0, 0.0]), [0.0])
    # Away from it, u = -K (x - x_ref).
    assert np.allclose(sf.compute([2.0, 1.0]), -(K @ np.array([1.0, 1.0])))
    # Callable (t, x) -> u adapter.
    assert np.allclose(sf(0.0, [2.0, 1.0]), sf.compute([2.0, 1.0]))


def test_pole_placement_places_eigenvalues():
    """place_gain yields A - B K with the requested spectrum."""
    di = examples.double_integrator()
    desired = [-2.0, -3.0]
    K = place_gain(di.A, di.B, desired)
    cl_poles = np.sort(np.linalg.eigvals(di.A - di.B @ K).real)
    assert np.allclose(cl_poles, np.sort(desired), atol=1e-6)


def test_pole_placement_stabilizes_double_integrator():
    """A pole-placed feedback drives the double integrator to the origin."""
    di = examples.double_integrator()
    ctrl = pole_placement(di.A, di.B, [-2.0, -3.0])
    t, x, u = simulate(di, ctrl, np.array([1.0, 0.5]), 6.0, 0.01)
    assert np.allclose(x[-1], 0.0, atol=1e-2)


def test_linear_mpc_regulates_and_respects_bounds():
    """cvxpy MPC drives the state toward the origin while honoring |u| <= u_max."""
    pytest.importorskip("cvxpy", reason="cvxpy not installed")
    from lib.controllers.mpc import LinearMPC

    di = examples.double_integrator()
    u_max = 1.0
    mpc = LinearMPC(di.A, di.B, dt=0.1, horizon=20,
                    Q=np.diag([10.0, 1.0]), R=np.array([[0.1]]), u_max=u_max)
    t, x, u = simulate(di, mpc, np.array([1.0, 0.0]), 6.0, 0.1)
    # Input bound respected up to the QP solver's feasibility tolerance.
    assert np.max(np.abs(u)) <= u_max + 1e-3      # input constraint respected
    assert np.linalg.norm(x[-1]) < 0.1            # regulated toward origin
