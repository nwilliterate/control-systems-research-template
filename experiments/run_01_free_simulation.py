"""Experiment 01 — free (uncontrolled) double-pendulum simulation.

Demonstrates the full loop with zero torque: chaotic free response of the double
pendulum, integrated with RK4 via lib.sim.simulate. Run in Spyder cell-by-cell or
``python -m experiments.run_01_free_simulation`` from the project root.
Requires Pinocchio (see environment.yml).
"""

# %% Imports & configuration
import numpy as np

from lib.dynamics.robot_model import RobotModel
from lib.sim.simulate import simulate
from lib.utils.config import load_config, project_root
from lib.utils.io import save_results
from lib.utils.plotting import plot_trajectory, save_figure

cfg = load_config()

# %% Build the plant; controller applies zero torque (free response)
robot = RobotModel(project_root() / cfg.robot.urdf, gravity=cfg.robot.gravity)
free_controller = lambda t, q, v: np.zeros(robot.nv)

# %% Simulate the free response
x0 = np.concatenate([cfg.initial_state.q, cfg.initial_state.v])
t, x, tau = simulate(robot, free_controller, x0, cfg.simulation.t_final,
                     cfg.simulation.dt, integrator=cfg.simulation.integrator)

# %% Plot & save
fig = plot_trajectory(
    t, x[:, : robot.nq],
    labels=[f"q{i+1}" for i in range(robot.nq)],
    ylabel="joint position [rad]",
    title="Free response of the double pendulum",
)
save_figure(fig, "free_response.png", subdir="run_01")
save_results("free_response", run_id="run_01", t=t, x=x)
print("Saved run_01 free-response trajectory.")
