"""End-to-end demo: build a plant, apply a controller, simulate, plot.

Kept intentionally short and readable (the MATLAB-script habit): every non-trivial
step delegates to ``lib/``. The plant, controller, integrator, and output flags are
all chosen in ``config/params.yaml`` — edit there, not here. The robot is just one
plant; set ``plant.type`` to ``double_integrator`` / ``mass_spring_damper`` /
``cart_pole`` to run a state-space example with no Pinocchio. Run ``python main.py``.
"""

import numpy as np

from lib.controllers.build import build_controller
from lib.sim.simulate import simulate
from lib.systems.build import build_plant
from lib.utils.config import load_config
from lib.utils.io import save_results
from lib.utils.plotting import plot_trajectory, save_figure


def initial_state(cfg, plant) -> np.ndarray:
    """Initial state ``x0`` from config: [q, v] for the robot, else ``initial_state.x``."""
    if cfg.plant.type == "robot":
        return np.concatenate([cfg.initial_state.q, cfg.initial_state.v])
    return np.asarray(cfg.initial_state.x, dtype=float)


def main() -> None:
    cfg = load_config()

    # 1. Plant + controller, both selected by config.
    plant = build_plant(cfg)
    controller = build_controller(cfg, plant, dt=cfg.simulation.dt)

    # 2. Simulate the closed loop (zero-order hold, integrator from config).
    x0 = initial_state(cfg, plant)
    t, x, u = simulate(plant, controller, x0, cfg.simulation.t_final,
                       cfg.simulation.dt, integrator=cfg.simulation.integrator)

    # 3. Plot the first half of the state (positions); save figure/data per config.
    npos = plant.nx // 2 or plant.nx
    fig = plot_trajectory(t, x[:, :npos],
                          labels=[f"x{i+1}" for i in range(npos)],
                          ylabel="state",
                          title=f"{cfg.plant.type} / {cfg.controller.type}")
    if cfg.output.save_figures:
        save_figure(fig, "main_state.png")
    if cfg.output.save_data:
        save_results("main", t=t, x=x, u=u)
    print(f"Done. plant={cfg.plant.type}, final x = {np.round(x[-1], 4)}")


if __name__ == "__main__":
    main()
