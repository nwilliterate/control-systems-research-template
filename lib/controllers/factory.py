"""Build a sim-facing controller from config.

Every controller class has its own natural ``compute(...)`` signature, but the
simulation loop (:func:`lib.sim.simulate.simulate`) wants a single uniform callable
``controller(t, x) -> u`` acting on the full plant state. This factory reads
``config.controller.type`` and returns that uniform callable, so experiments select
a controller from YAML instead of editing code.

The robot's stacked state is ``x = [q, v]``; the robot controllers (PID,
computed-torque) work in ``(q, v)`` and are wrapped here to split ``x`` internally,
while ``lqr`` is already a state-feedback law on ``x``. So every returned callable
shares the plant-agnostic ``(t, x) -> u`` contract.

Supported types: ``pid``, ``computed_torque``, ``lqr``, ``none``.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from lib.controllers.computed_torque import ComputedTorque
from lib.controllers.lqr import LQR
from lib.controllers.pid import PID
from lib.dynamics.robot_plant import RobotPlant

Controller = Callable[[float, np.ndarray], np.ndarray]


def make_controller(cfg, plant: RobotPlant, q_des: np.ndarray,
                    dt: float) -> Controller:
    """Return a uniform ``controller(t, x) -> u`` selected by ``cfg.controller.type``.

    Parameters
    ----------
    cfg : loaded config (see lib.utils.config); reads ``cfg.controller``.
    plant : RobotPlant wrapping the RobotModel (provides ``split`` and ``robot``).
    q_des : (nv,) desired joint positions [rad].
    dt : control step [s] (PID integration step).

    Returns
    -------
    controller : callable mapping (t, x=[q,v]) to a joint-torque vector (nv,).
    """
    q_des = np.asarray(q_des, dtype=float)
    ctype = cfg.controller.type
    robot = plant.robot

    if ctype == "none":
        nv = plant.nv
        return lambda t, x: np.zeros(nv)

    if ctype == "pid":
        p = cfg.controller.pid
        pid = PID(kp=p.kp, ki=p.ki, kd=p.kd, u_max=p.u_max)
        return lambda t, x: pid.compute(*plant.split(x), q_des, dt)

    if ctype == "computed_torque":
        c = cfg.controller.computed_torque
        ct = ComputedTorque(robot, kp=c.kp, kd=c.kd)
        return lambda t, x: ct.compute(*plant.split(x), q_des)

    if ctype == "lqr":
        # Linearize about the rest setpoint and use gravity as feedforward so the
        # LQR output is a true joint torque: tau = g(q_des) - K (x - x_ref).
        from lib.dynamics.forward_dynamics import gravity
        from lib.systems.linearize import linearize_plant

        nv = plant.nv
        v_des = np.zeros(nv)
        x_ref = np.concatenate([q_des, v_des])
        tau0 = gravity(robot, q_des)
        A, B = linearize_plant(plant, x_ref, tau0)
        Q = np.diag(np.asarray(cfg.controller.lqr.Q_diag, dtype=float))
        R = np.diag(np.asarray(cfg.controller.lqr.R_diag, dtype=float))
        lqr = LQR(A, B, Q, R, x_ref=x_ref)
        return lambda t, x: tau0 + lqr.compute(np.asarray(x, dtype=float))

    raise ValueError(
        f"unknown controller.type {ctype!r} (use pid | computed_torque | lqr | none)"
    )
