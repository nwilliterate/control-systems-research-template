"""Unit tests for the state-space core (lib/systems) — all pure-numpy, no Pinocchio.

Covers the LTI StateSpace plant, exact c2d discretization (against the analytic
double-integrator result), generic linearization (against a known LTI), and the
example plants.
"""

import numpy as np

from lib.systems import StateSpace, c2d, linearize_plant, examples


def test_state_space_dynamics_and_output():
    """StateSpace returns A x + B u and a full-state default output y = x."""
    A = np.array([[0.0, 1.0], [-2.0, -3.0]])
    B = np.array([[0.0], [1.0]])
    ss = StateSpace(A, B)
    assert ss.nx == 2 and ss.nu == 1 and ss.ny == 2
    x, u = np.array([1.0, 2.0]), np.array([0.5])
    assert np.allclose(ss.dynamics(x, u), A @ x + B @ u)
    assert np.allclose(ss.output(x, u), x)  # default C = I, D = 0


def test_state_space_custom_output():
    """A custom C/D produces y = C x + D u."""
    ss = StateSpace([[0.0, 1.0], [0.0, 0.0]], [[0.0], [1.0]],
                    C=[[1.0, 0.0]], D=[[0.0]])
    assert ss.ny == 1
    assert np.allclose(ss.output([3.0, 4.0], [0.0]), [3.0])


def test_c2d_zoh_matches_double_integrator_analytic():
    """Exact ZOH of the double integrator: Ad=[[1,dt],[0,1]], Bd=[dt^2/2, dt]."""
    di = examples.double_integrator()
    dt = 0.1
    Ad, Bd = c2d(di.A, di.B, dt)
    assert np.allclose(Ad, [[1.0, dt], [0.0, 1.0]])
    assert np.allclose(Bd.ravel(), [dt**2 / 2.0, dt])


def test_c2d_euler_is_first_order():
    """Forward-Euler c2d gives Ad = I + A dt, Bd = B dt."""
    di = examples.double_integrator()
    dt = 0.05
    Ad, Bd = c2d(di.A, di.B, dt, method="euler")
    assert np.allclose(Ad, np.eye(2) + di.A * dt)
    assert np.allclose(Bd, di.B * dt)


def test_linearize_plant_recovers_lti():
    """Linearizing an LTI plant returns its own (A, B)."""
    msd = examples.mass_spring_damper(m=2.0, k=3.0, c=0.5)
    A, B = linearize_plant(msd, np.zeros(2), np.zeros(1))
    assert np.allclose(A, msd.A, atol=1e-6)
    assert np.allclose(B, msd.B, atol=1e-6)


def test_double_integrator_controllable():
    """The double integrator is controllable; a decoupled 0-input mode is not."""
    assert examples.double_integrator().is_controllable()
    uncontrollable = StateSpace([[1.0, 0.0], [0.0, 2.0]], [[1.0], [0.0]])
    assert not uncontrollable.is_controllable()


def test_cartpole_upright_is_unstable():
    """Linearizing the cart-pole about the upright gives a positive real eigenvalue."""
    cp = examples.CartPole()
    A, B = linearize_plant(cp, np.zeros(4), np.zeros(1))
    assert A.shape == (4, 4) and B.shape == (4, 1)
    assert np.max(np.real(np.linalg.eigvals(A))) > 0.0  # inverted -> unstable
