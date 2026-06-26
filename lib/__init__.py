"""Reusable toolbox for control-systems research.

The core abstraction is the state-space ``Plant`` (``lib.systems``); the robot
(``lib.dynamics``) is one plant among many. Import building blocks from the
submodules, e.g.::

    from lib.systems import StateSpace, examples
    from lib.integrators.runge_kutta import rk4_step
    from lib.controllers.state_feedback import StateFeedback
    from lib.dynamics.robot_plant import RobotPlant   # robot plant (needs Pinocchio)

Keep experiment scripts and ``main.py`` thin; put reusable logic here.
"""
