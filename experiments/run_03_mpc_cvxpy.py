"""Experiment 03 — MPC regulation of a double integrator with input saturation.

Demonstrates LinearMPC (cvxpy) applied to the simplest controllable plant. The
input bound u_max visibly saturates the applied force during the initial phase,
showing constrained optimisation in action. Run in Spyder cell-by-cell or
    python -m experiments.run_03_mpc_cvxpy
from the project root. Requires cvxpy (pip install cvxpy).
"""

# %% Imports
import numpy as np

from lib.systems.examples import double_integrator
from lib.controllers.mpc import LinearMPC
from lib.sim.simulate import simulate
from lib.utils.plotting import plot_trajectory, save_figure
from lib.utils.io import save_results

# %% Build the plant
# double integrator: x'' = u, state x = [position, velocity]
plant = double_integrator()
print(f"Plant: {plant}")
print(f"  A =\n{plant.A}")
print(f"  B =\n{plant.B}")
print(f"  Controllable: {plant.is_controllable()}")

# %% Design MPC controller
dt = 0.1          # [s] control sample period
horizon = 20      # prediction horizon steps
u_max = 1.0       # [N] symmetric input bound — will saturate at the start

Q = np.diag([1.0, 0.1])    # state cost [position, velocity]
R = np.array([[0.01]])      # input cost
Qf = np.diag([10.0, 1.0])  # terminal weight (heavier to pull state to zero)

mpc = LinearMPC(
    plant.A, plant.B,
    dt=dt,
    horizon=horizon,
    Q=Q, R=R, Qf=Qf,
    u_max=u_max,
)
print(f"\nMPC: horizon={horizon}, dt={dt} s, u_max=±{u_max}")

# %% Simulate from x0 = [1.0 m, 0.0 m/s]
x0 = np.array([1.0, 0.0])
t_final = 8.0   # [s]

t, x, u = simulate(plant, mpc, x0, t_final, dt, integrator="rk4")
print(f"\nSimulation: {len(t)} steps,  t in [{t[0]:.2f}, {t[-1]:.2f}] s")
print(f"Final state x(t_final) = {x[-1]}")
print(f"Input range: [{u.min():.3f}, {u.max():.3f}] N  (bound = ±{u_max})")
sat_steps = int(np.sum(np.abs(u) >= 0.99 * u_max))
print(f"Steps at saturation (|u| >= 0.99·u_max): {sat_steps}/{len(u)}")

# %% Plot state trajectory
fig_x = plot_trajectory(
    t, x,
    labels=["position [m]", "velocity [m/s]"],
    ylabel="state",
    title="MPC regulation — double integrator",
)
path_x = save_figure(fig_x, "states.png", subdir="run_03")
print(f"Saved state figure: {path_x}")

# %% Plot control input (shows saturation)
fig_u = plot_trajectory(
    t[:-1], u,
    labels=["force [N]"],
    ylabel="input u [N]",
    title=f"MPC input — double integrator (bound ±{u_max} N)",
)
# draw the saturation lines on the input figure
ax = fig_u.axes[0]
ax.axhline(u_max,  color="r", linestyle="--", linewidth=1.2, label=f"+u_max={u_max}")
ax.axhline(-u_max, color="r", linestyle="--", linewidth=1.2, label=f"-u_max={-u_max}")
ax.legend(loc="best")
fig_u.tight_layout()

path_u = save_figure(fig_u, "input.png", subdir="run_03")
print(f"Saved input figure: {path_u}")

# %% Save results
data_path = save_results("mpc_regulation", run_id="run_03", t=t, x=x, u=u)
print(f"Saved data: {data_path}")
print("run_03 complete.")
