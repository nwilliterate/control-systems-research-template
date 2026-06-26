"""Simulation loop — drives a controller-in-the-loop forward in time.

Keeps experiment scripts and ``main.py`` thin: they build a robot + controller
and call :func:`lib.sim.simulate.simulate` instead of hand-rolling the closed-loop
ODE.
"""
