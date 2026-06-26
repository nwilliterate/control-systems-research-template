"""Integration tests for the simulate loop + controller factory.

These require Pinocchio (they build a RobotModel from the URDF), so the whole module
is skipped when Pinocchio is unavailable — preserving the pure-numpy test guarantee.
"""

import numpy as np
import pytest

pytest.importorskip("pinocchio", reason="Pinocchio not installed (conda-forge)")

from lib.controllers.factory import make_controller
from lib.dynamics.robot_model import RobotModel
from lib.dynamics.robot_plant import RobotPlant
from lib.sim.simulate import simulate
from lib.utils.config import load_config, project_root


@pytest.fixture(scope="module")
def plant_and_cfg():
    cfg = load_config("config/params.yaml")
    robot = RobotModel(project_root() / cfg.robot.urdf, gravity=cfg.robot.gravity)
    return RobotPlant(robot), cfg


def test_simulate_shapes_and_zero_input(plant_and_cfg):
    """simulate returns consistent (t, x, u) shapes; zero input -> zero u."""
    plant, cfg = plant_and_cfg
    x0 = np.concatenate([cfg.initial_state.q, cfg.initial_state.v])
    none_ctrl = lambda t, x: np.zeros(plant.nu)
    t, x, u = simulate(plant, none_ctrl, x0, 0.5, cfg.simulation.dt)
    assert x.shape == (len(t), plant.nx)
    assert u.shape == (len(t) - 1, plant.nu)
    assert np.allclose(u, 0.0)


@pytest.mark.parametrize("ctype", ["computed_torque", "lqr", "pid"])
def test_controllers_regulate_to_setpoint(plant_and_cfg, ctype):
    """Each config-selected controller drives the double pendulum toward q_des."""
    plant, _ = plant_and_cfg
    cfg = load_config("config/params.yaml")  # fresh, mutable copy
    cfg["controller"]["type"] = ctype

    q_des = np.zeros(plant.nv)
    ctrl = make_controller(cfg, plant, q_des, dt=cfg.simulation.dt)
    x0 = np.concatenate([[0.3, -0.2], [0.0, 0.0]])
    t, x, u = simulate(plant, ctrl, x0, 4.0, cfg.simulation.dt)
    final_q_err = np.linalg.norm(x[-1, : plant.nq] - q_des)
    assert final_q_err < 0.2, f"{ctype} did not regulate (err={final_q_err:.3f})"
