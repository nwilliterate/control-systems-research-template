"""Build a sim-facing ``controller(t, x) -> u`` for the configured plant.

Two regimes share one uniform output:

- **Robot plant** -> delegate to :func:`lib.controllers.factory.make_controller`
  (pid / computed_torque / lqr / none, in joint space).
- **State-space plant** -> design an LQR on the plant linearized about the setpoint
  and apply it as a :class:`~lib.controllers.state_feedback.StateFeedback` law.

This keeps ``main.py`` plant-agnostic: it just calls :func:`build_controller`.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from lib.controllers.lqr import lqr_gain
from lib.controllers.state_feedback import StateFeedback
from lib.systems.linearize import linearize_plant
from lib.systems.plant import Plant

Controller = Callable[[float, np.ndarray], np.ndarray]


def build_controller(cfg, plant: Plant, dt: float) -> Controller:
    """Return a ``(t, x) -> u`` controller for ``plant`` per ``cfg.controller``.

    Parameters
    ----------
    cfg : loaded config.
    plant : the plant to control (RobotPlant or a state-space Plant).
    dt : control step [s].
    """
    # Robot plant: keep the joint-space factory (needs RobotPlant features).
    from lib.dynamics.robot_plant import RobotPlant

    if isinstance(plant, RobotPlant):
        from lib.controllers.factory import make_controller

        q_des = np.asarray(cfg.reference.q_des, dtype=float)
        return make_controller(cfg, plant, q_des, dt)

    # State-space plant: LQR about the setpoint -> static state feedback.
    x_ref = np.asarray(cfg.reference.x_des, dtype=float)
    A, B = linearize_plant(plant, x_ref, np.zeros(plant.nu))
    Q = np.diag(np.asarray(cfg.controller.state_lqr.Q_diag, dtype=float))
    R = np.diag(np.asarray(cfg.controller.state_lqr.R_diag, dtype=float))
    K = lqr_gain(A, B, Q, R)
    return StateFeedback(K, x_ref=x_ref)
