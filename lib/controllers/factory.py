"""Build a sim-facing controller from config.

Every controller class has its own natural ``compute(...)`` signature, but the
simulation loop (:func:`lib.sim.simulate.simulate`) wants a single uniform callable
``controller(t, q, v) -> tau``. This factory reads ``config.controller.type`` and
returns that uniform callable, so experiments select a controller from YAML instead
of editing code.

Supported types: ``pid``, ``computed_torque``, ``lqr``, ``none``.
The ``lqr`` path linearizes the robot about the setpoint (see
:mod:`lib.dynamics.linearize`) and adds the gravity torque as feedforward, so its
output is a genuine joint torque that shares the same loop as the others.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from lib.controllers.computed_torque import ComputedTorque
from lib.controllers.lqr import LQR
from lib.controllers.pid import PID
from lib.dynamics.robot_model import RobotModel

Controller = Callable[[float, np.ndarray, np.ndarray], np.ndarray]


def make_controller(cfg, robot: RobotModel, q_des: np.ndarray,
                    dt: float) -> Controller:
    """Return a uniform ``controller(t, q, v) -> tau`` selected by ``cfg.controller.type``.

    Parameters
    ----------
    cfg : loaded config (see lib.utils.config); reads ``cfg.controller``.
    robot : RobotModel (needed for model-based controllers).
    q_des : (nv,) desired joint positions [rad].
    dt : control step [s] (PID integration step).

    Returns
    -------
    controller : callable mapping (t, q, v) to a joint-torque vector (nv,).
    """
    q_des = np.asarray(q_des, dtype=float)
    ctype = cfg.controller.type

    if ctype == "none":
        nv = robot.nv
        return lambda t, q, v: np.zeros(nv)

    if ctype == "pid":
        p = cfg.controller.pid
        pid = PID(kp=p.kp, ki=p.ki, kd=p.kd, u_max=p.u_max)
        return lambda t, q, v: pid.compute(q, v, q_des, dt)

    if ctype == "computed_torque":
        c = cfg.controller.computed_torque
        ct = ComputedTorque(robot, kp=c.kp, kd=c.kd)
        return lambda t, q, v: ct.compute(q, v, q_des)

    if ctype == "lqr":
        # Linearize about the rest setpoint and use gravity as feedforward so the
        # LQR output is a true joint torque: tau = g(q_des) - K (x - x_ref).
        from lib.dynamics.forward_dynamics import gravity
        from lib.dynamics.linearize import linearize

        nv = robot.nv
        v_des = np.zeros(nv)
        tau0 = gravity(robot, q_des)
        A, B = linearize(robot, q_des, v_des, tau0)
        Q = np.diag(np.asarray(cfg.controller.lqr.Q_diag, dtype=float))
        R = np.diag(np.asarray(cfg.controller.lqr.R_diag, dtype=float))
        x_ref = np.concatenate([q_des, v_des])
        lqr = LQR(A, B, Q, R, x_ref=x_ref)
        return lambda t, q, v: tau0 + lqr.compute(np.concatenate([q, v]))

    raise ValueError(
        f"unknown controller.type {ctype!r} (use pid | computed_torque | lqr | none)"
    )
