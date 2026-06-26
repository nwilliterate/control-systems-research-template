"""PID joint controller with anti-windup.

Pure numpy — no Pinocchio dependency, so it is fully unit-testable on any machine.
"""

from __future__ import annotations

import numpy as np


class PID:
    """Per-joint PID controller with integral clamping (anti-windup).

    Control law (per joint):  tau = Kp e + Ki ∫e dt + Kd de/dt,
    with the output saturated to +/- ``u_max`` and the integral frozen when the
    output saturates (clamping anti-windup).

    Parameters
    ----------
    kp, ki, kd : array_like, shape (n,)
        Proportional, integral, derivative gains per joint.
    u_max : float, optional
        Symmetric torque saturation [N*m]. ``np.inf`` disables saturation.
    """

    def __init__(self, kp, ki, kd, u_max: float = np.inf) -> None:
        self.kp = np.asarray(kp, dtype=float)
        self.ki = np.asarray(ki, dtype=float)
        self.kd = np.asarray(kd, dtype=float)
        self.u_max = float(u_max)
        self._integral = np.zeros_like(self.kp)

    def reset(self) -> None:
        """Clear the integral accumulator (call before a new run)."""
        self._integral = np.zeros_like(self.kp)

    def compute(self, q: np.ndarray, v: np.ndarray, q_des: np.ndarray,
                dt: float, v_des: np.ndarray | None = None) -> np.ndarray:
        """Return the joint torque for the current step.

        Parameters
        ----------
        q     : (n,) measured positions [rad].
        v     : (n,) measured velocities [rad/s].
        q_des : (n,) desired positions [rad].
        dt    : controller time step [s].
        v_des : (n,) desired velocities [rad/s], default zeros.

        Returns
        -------
        tau : (n,) joint torques [N*m].
        """
        q = np.asarray(q, dtype=float)
        v = np.asarray(v, dtype=float)
        q_des = np.asarray(q_des, dtype=float)
        v_des = np.zeros_like(q) if v_des is None else np.asarray(v_des, dtype=float)

        e = q_des - q
        de = v_des - v

        candidate_integral = self._integral + e * dt
        tau_unsat = self.kp * e + self.ki * candidate_integral + self.kd * de
        tau = np.clip(tau_unsat, -self.u_max, self.u_max)

        # Anti-windup (per-joint): commit the new integral only for joints whose
        # output is within saturation; saturated joints keep their previous value.
        not_saturated = np.abs(tau_unsat) <= self.u_max
        self._integral = np.where(not_saturated, candidate_integral, self._integral)
        return tau
