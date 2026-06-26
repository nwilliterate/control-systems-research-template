"""End-to-end demo: load a robot, apply a controller, simulate, plot.

Kept intentionally short and readable (the MATLAB-script habit): every non-trivial
step delegates to ``lib/``. The controller, integrator, and output flags are all
chosen in ``config/params.yaml`` — edit there, not here. Run with ``python main.py``.
"""

import numpy as np

from lib.controllers.factory import make_controller
from lib.dynamics.robot_model import RobotModel
from lib.sim.simulate import simulate
from lib.utils.config import load_config, project_root
from lib.utils.io import save_results
from lib.utils.plotting import plot_trajectory, save_figure


def main() -> None:
    cfg = load_config()

    # 1. Plant: load the robot model from URDF.
    robot = RobotModel(project_root() / cfg.robot.urdf, gravity=cfg.robot.gravity)

    # 2. Controller: selected by config (pid | computed_torque | lqr | none).
    q_des = np.asarray(cfg.reference.q_des, dtype=float)
    controller = make_controller(cfg, robot, q_des, dt=cfg.simulation.dt)

    # 3. Simulate the closed loop (zero-order hold, integrator from config).
    x0 = np.concatenate([cfg.initial_state.q, cfg.initial_state.v])
    t, x, tau = simulate(robot, controller, x0, cfg.simulation.t_final,
                         cfg.simulation.dt, integrator=cfg.simulation.integrator)

    # 4. Plot joint positions; save figure/data per the output flags.
    fig = plot_trajectory(t, x[:, :robot.nq],
                          labels=[f"q{i+1}" for i in range(robot.nq)],
                          ylabel="joint position [rad]",
                          title=f"{cfg.controller.type} regulation")
    if cfg.output.save_figures:
        save_figure(fig, "main_joint_positions.png")
    if cfg.output.save_data:
        save_results("main", t=t, x=x, tau=tau)
    print(f"Done. Final q = {x[-1, :robot.nq]}, target = {q_des}")


if __name__ == "__main__":
    main()
