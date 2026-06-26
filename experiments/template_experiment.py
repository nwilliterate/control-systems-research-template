"""Template experiment — copy me to start a new study.

Copy to ``experiments/run_NN_short_description.py`` and edit. Written as Spyder
cells (``# %%``): in Spyder press Ctrl+Enter to run one cell, like a MATLAB
section. Import everything reusable from ``lib`` — do not define algorithms here.

Also create the paired write-up ``docs/experiments/exp_NN_short_description.md``
(copy ``docs/experiments/_experiment_template.md``) to record the study.
"""

# %% Imports & configuration
import numpy as np

from lib.utils.config import load_config, project_root
from lib.utils.plotting import plot_trajectory, save_figure
from lib.utils.io import save_results

cfg = load_config()
print("Loaded config:", dict(cfg.simulation))

# %% Set up the study (plant + controller)
# from lib.dynamics.robot_model import RobotModel
# robot = RobotModel(project_root() / cfg.robot.urdf, gravity=cfg.robot.gravity)
# ... build your controller here ...

# %% Run / simulate
# from lib.integrators.runge_kutta import rk4
# t, x = rk4(f, x0, 0.0, cfg.simulation.t_final, cfg.simulation.dt)

# %% Plot & save results
# fig = plot_trajectory(t, x, ylabel="state", title="My study")
# save_figure(fig, "my_study.png", subdir="run_NN")
# save_results("my_study", run_id="run_NN", t=t, x=x)

print("Edit this template cell-by-cell in Spyder.")
