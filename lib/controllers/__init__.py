"""Controllers for the robot.

Each controller class has its own natural ``compute(...)`` signature (PID needs the
time step and a setpoint; computed-torque needs the model and a setpoint; LQR works
on the full state). To run any of them in the same simulation loop, wrap one with
:func:`lib.controllers.factory.make_controller`, which returns a uniform callable
``controller(t, q, v) -> tau`` selected from ``config.controller.type``.
"""
