"""Experiment 02 — LQR regulation of a mass-spring-damper (no robot).

Demonstrates the plant-agnostic core: StateSpace + lqr_gain + StateFeedback +
simulate all work without Pinocchio. The mass-spring-damper is regulated from a
displaced initial condition back to the origin.

Run in Spyder cell-by-cell or
    python -m experiments.run_02_state_space_lqr
from the project root.
"""

# %% Imports
import numpy as np

from lib.systems.examples import mass_spring_damper
from lib.controllers.lqr import lqr_gain
from lib.controllers.state_feedback import StateFeedback
from lib.sim.simulate import simulate
from lib.utils.plotting import plot_trajectory, save_figure
from lib.utils.io import save_results

# %% Build the plant
# mass-spring-damper: m x'' + c x' + k x = u, state x = [position, velocity]
# Parameters: m=1 kg, k=1 N/m, c=0.2 N·s/m
plant = mass_spring_damper(m=1.0, k=1.0, c=0.2)
print(f"Plant: {plant}")
print(f"  A =\n{plant.A}")
print(f"  B =\n{plant.B}")
print(f"  Controllable: {plant.is_controllable()}")

# %% Design LQR gain
# Q penalises position and velocity equally; R penalises input lightly.
Q = np.diag([10.0, 1.0])   # state cost weights [position, velocity]
R = np.array([[1.0]])       # input cost weight

K = lqr_gain(plant.A, plant.B, Q, R)
print(f"\nLQR gain K = {K}")

controller = StateFeedback(K)   # u = -K x  (regulates to origin)

# %% Simulate regulation from x0 = [1.0 m, 0.0 m/s]
x0 = np.array([1.0, 0.0])   # initial displacement 1 m, zero velocity
t_final = 10.0               # [s]
dt = 0.01                    # [s]

t, x, u = simulate(plant, controller, x0, t_final, dt, integrator="rk4")
print(f"\nSimulation: {len(t)} steps,  t in [{t[0]:.2f}, {t[-1]:.2f}] s")
print(f"Final state x(t_final) = {x[-1]}")

# %% Plot state trajectory
fig_x = plot_trajectory(
    t, x,
    labels=["position [m]", "velocity [m/s]"],
    ylabel="state",
    title="LQR regulation — mass-spring-damper",
)
path_x = save_figure(fig_x, "states.png", subdir="run_02")
print(f"Saved state figure: {path_x}")

# %% Plot control input
fig_u = plot_trajectory(
    t[:-1], u,
    labels=["force [N]"],
    ylabel="input u [N]",
    title="LQR control input — mass-spring-damper",
)
path_u = save_figure(fig_u, "input.png", subdir="run_02")
print(f"Saved input figure: {path_u}")

# %% Save results
data_path = save_results("lqr_regulation", run_id="run_02", t=t, x=x, u=u)
print(f"Saved data: {data_path}")
print("run_02 complete.")
