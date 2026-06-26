"""Unit tests for PID and LQR controllers (pure numpy, no Pinocchio)."""

import numpy as np
import pytest

from lib.controllers.lqr import LQR, lqr_gain
from lib.controllers.pid import PID
from lib.integrators.runge_kutta import rk4


def test_pid_drives_error_to_zero():
    """A PID on a double integrator should regulate position to the setpoint."""
    pid = PID(kp=[10.0], ki=[1.0], kd=[6.0], u_max=np.inf)
    q, v = np.array([0.0]), np.array([0.0])
    q_des = np.array([1.0])
    dt = 0.01
    for _ in range(2000):
        tau = pid.compute(q, v, q_des, dt)
        # plant: unit-mass double integrator  a = tau
        v = v + tau * dt
        q = q + v * dt
    assert abs(q[0] - q_des[0]) < 1e-2


def test_pid_saturation_respected():
    """Output never exceeds u_max."""
    pid = PID(kp=[1000.0], ki=[0.0], kd=[0.0], u_max=5.0)
    tau = pid.compute(np.array([0.0]), np.array([0.0]), np.array([10.0]), 0.01)
    assert abs(tau[0]) <= 5.0 + 1e-9


def test_pid_integral_accumulates_proportional_to_time():
    """Integral grows as error * cumulative dt when not saturating."""
    pid = PID(kp=[0.0], ki=[1.0], kd=[0.0], u_max=np.inf)
    dt, steps = 0.01, 50
    for _ in range(steps):
        pid.compute(np.array([0.0]), np.array([0.0]), np.array([1.0]), dt)
    assert pid._integral[0] == pytest.approx(1.0 * steps * dt)


def test_pid_reset_clears_integral():
    """reset() zeroes the accumulator after it has been populated."""
    pid = PID(kp=[0.0], ki=[1.0], kd=[0.0], u_max=np.inf)
    for _ in range(10):
        pid.compute(np.array([0.0]), np.array([0.0]), np.array([1.0]), 0.01)
    assert pid._integral[0] != 0.0
    pid.reset()
    assert np.all(pid._integral == 0.0)


def test_pid_antiwindup_is_per_joint():
    """A saturated joint freezes its integral while a non-saturated joint keeps integrating."""
    # Joint 0 saturates hard (huge error vs small u_max); joint 1 stays linear.
    pid = PID(kp=[1000.0, 1.0], ki=[1.0, 1.0], kd=[0.0, 0.0], u_max=5.0)
    q = np.array([0.0, 0.0])
    v = np.array([0.0, 0.0])
    q_des = np.array([10.0, 0.001])  # joint 0 way off (saturates), joint 1 tiny error
    dt = 0.01
    for _ in range(20):
        pid.compute(q, v, q_des, dt)
    # Joint 1 integrated (non-zero); joint 0 froze near zero (first step only).
    assert pid._integral[1] > 0.0
    assert pid._integral[0] <= pid._integral[1] + 1e-12  # joint 0 did not run away


def test_lqr_gain_stabilizes_double_integrator():
    """LQR closed loop  x' = (A - B K) x  must be Hurwitz (stable)."""
    A = np.array([[0.0, 1.0], [0.0, 0.0]])
    B = np.array([[0.0], [1.0]])
    Q = np.diag([10.0, 1.0])
    R = np.array([[1.0]])
    K = lqr_gain(A, B, Q, R)

    eig = np.linalg.eigvals(A - B @ K)
    assert np.all(eig.real < 0.0)


def test_lqr_controller_regulates_state():
    """Closed-loop LQR simulation converges to the origin."""
    A = np.array([[0.0, 1.0], [0.0, 0.0]])
    B = np.array([[0.0], [1.0]])
    ctrl = LQR(A, B, Q=np.diag([10.0, 1.0]), R=np.array([[1.0]]))

    f = lambda t, x: A @ x + (B @ ctrl.compute(x))
    t, x = rk4(f, np.array([1.0, 0.0]), 0.0, 15.0, 1e-2)
    assert np.linalg.norm(x[-1]) < 1e-2


def test_lqr_x_ref_offset_regulates_to_nonzero_reference():
    """LQR with x_ref must regulate to x_ref, not the origin (uses x - x_ref)."""
    A = np.array([[0.0, 1.0], [0.0, 0.0]])
    B = np.array([[0.0], [1.0]])
    x_ref = np.array([2.0, 0.0])
    ctrl = LQR(A, B, Q=np.diag([10.0, 1.0]), R=np.array([[1.0]]), x_ref=x_ref)
    f = lambda t, x: A @ x + (B @ ctrl.compute(x))
    t, x = rk4(f, np.array([0.0, 0.0]), 0.0, 20.0, 1e-2)
    assert np.linalg.norm(x[-1] - x_ref) < 0.1
