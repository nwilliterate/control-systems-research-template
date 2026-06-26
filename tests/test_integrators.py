"""Unit tests for the Runge-Kutta integrators (pure numpy, no Pinocchio)."""

import numpy as np
import pytest

from lib.integrators.runge_kutta import rk4, rk4_step, rk45, rk45_step


def test_rk4_matches_exponential_decay():
    """dx/dt = -x has the analytic solution x(t) = x0 * exp(-t)."""
    f = lambda t, x: -x
    x0 = np.array([1.0])
    t, x = rk4(f, x0, 0.0, 5.0, 0.01)

    analytic = x0 * np.exp(-t)
    assert np.allclose(x[:, 0], analytic, atol=1e-6)


def test_rk4_harmonic_oscillator_energy():
    """Undamped oscillator x'' = -x conserves energy reasonably over time."""
    # State [pos, vel]; f = [vel, -pos].
    f = lambda t, s: np.array([s[1], -s[0]])
    s0 = np.array([1.0, 0.0])
    t, s = rk4(f, s0, 0.0, 10.0, 1e-3)

    energy = 0.5 * (s[:, 0] ** 2 + s[:, 1] ** 2)
    # RK4 with small steps keeps energy nearly constant.
    assert np.max(np.abs(energy - energy[0])) < 1e-3


def test_rk4_step_is_fourth_order():
    """Local truncation error of one RK4 step scales like O(dt^5)."""
    f = lambda t, x: -x
    x0 = np.array([1.0])
    errs = []
    for dt in (0.1, 0.05):
        x1 = rk4_step(f, 0.0, x0, dt)
        errs.append(abs(x1[0] - np.exp(-dt)))
    # Halving dt should cut the local error by ~2^5 = 32x.
    assert errs[0] / errs[1] > 16.0


def test_rk45_step_error_estimate_is_nonzero_and_order_consistent():
    """Error estimate must be positive and track the true error (not a no-op)."""
    f = lambda t, x: -x  # analytic solution exp(-t)
    x0 = np.array([1.0])
    x_next, err = rk45_step(f, 0.0, x0, 0.1)
    true_error = abs(x_next[0] - np.exp(-0.1))
    assert err.shape == x0.shape
    assert np.all(err > 0.0), "error estimate is zero -> cannot adapt step size"
    assert err[0] < 1e-7, f"error estimate {err[0]:.2e} implausibly large for dt=0.1"
    # 5th-order solution is more accurate than the 4th/5th difference estimate.
    assert true_error < 10 * err[0]


def test_rk45_step_error_shrinks_with_step():
    """Halving dt must shrink the error estimate by roughly 2^6 (5th-order pair)."""
    f = lambda t, x: -x
    x0 = np.array([1.0])
    _, e1 = rk45_step(f, 0.0, x0, 0.1)
    _, e2 = rk45_step(f, 0.0, x0, 0.05)
    assert e1[0] / e2[0] > 30.0  # ~2^6 = 64, allow margin


def test_rk45_adaptive_matches_analytic_decay():
    """Adaptive rk45 driver integrates dx/dt=-x accurately and ends at t_final."""
    f = lambda t, x: -x
    t, x = rk45(f, np.array([1.0]), 0.0, 5.0, dt0=0.5, rtol=1e-8, atol=1e-10)
    assert t[-1] == pytest.approx(5.0)
    assert x[-1, 0] == pytest.approx(np.exp(-5.0), abs=1e-6)
    assert len(t) == len(x)


def test_rk4_rejects_bad_arguments():
    """rk4 validates dt > 0 and t_final >= t0."""
    f = lambda t, x: -x
    with pytest.raises(ValueError):
        rk4(f, np.array([1.0]), 0.0, 1.0, 0.0)
    with pytest.raises(ValueError):
        rk4(f, np.array([1.0]), 1.0, 0.0, 0.1)


def test_rk4_time_vector_matches_trajectory_length():
    """len(t) == len(x) and the grid reaches t_final."""
    f = lambda t, x: -x
    t, x = rk4(f, np.array([1.0]), 0.0, 1.0, 0.1)
    assert len(t) == len(x)
    assert t[-1] >= 1.0 - 1e-9
