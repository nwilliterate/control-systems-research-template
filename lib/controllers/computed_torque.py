"""Computed-torque (inverse-dynamics) controller.

Model-based control law that linearizes the robot dynamics via feedback:

    tau = M(q) ( qdd_des + Kd (v_des - v) + Kp (q_des - q) ) + C(q,v) v + g(q)

With perfect model knowledge this yields decoupled, linear error dynamics
``e'' + Kd e' + Kp e = 0`` per joint. Depends on :mod:`lib.dynamics`.
"""

from __future__ import annotations

import numpy as np

from lib.dynamics.forward_dynamics import mass_matrix, nonlinear_effects
from lib.dynamics.robot_model import RobotModel


class ComputedTorque:
    """Computed-torque controller for a :class:`RobotModel`.

    Parameters
    ----------
    robot : RobotModel
    kp, kd : array_like, shape (nv,)
        Position and velocity error gains (choose Kd ~ 2*sqrt(Kp) for critical
        damping of the resulting linear error dynamics).
    """

    def __init__(self, robot: RobotModel, kp, kd) -> None:
        self.robot = robot
        self.kp = np.asarray(kp, dtype=float)
        self.kd = np.asarray(kd, dtype=float)

    def compute(self, q: np.ndarray, v: np.ndarray, q_des: np.ndarray,
                v_des: np.ndarray | None = None,
                a_des: np.ndarray | None = None) -> np.ndarray:
        """Return the model-based joint torque.

        Parameters
        ----------
        q, v   : (nv,) measured state.
        q_des  : (nv,) desired positions.
        v_des  : (nv,) desired velocities, default zeros.
        a_des  : (nv,) desired accelerations (feedforward), default zeros.

        Returns
        -------
        tau : (nv,) joint torques [N*m].
        """
        q = np.asarray(q, dtype=float)
        v = np.asarray(v, dtype=float)
        q_des = np.asarray(q_des, dtype=float)
        v_des = np.zeros_like(q) if v_des is None else np.asarray(v_des, dtype=float)
        a_des = np.zeros_like(q) if a_des is None else np.asarray(a_des, dtype=float)

        a_cmd = a_des + self.kd * (v_des - v) + self.kp * (q_des - q)
        M = mass_matrix(self.robot, q)
        b = nonlinear_effects(self.robot, q, v)  # C(q,v) v + g(q)
        return M @ a_cmd + b
