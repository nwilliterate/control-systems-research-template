"""State-space systems toolbox — the plant-agnostic core of the template.

A *plant* is anything with a state ``x``, an input ``u``, and a continuous-time
state equation ``x' = f(x, u, t)``. The robot is just one plant
(:class:`lib.dynamics.robot_plant.RobotPlant`); linear systems, a cart-pole, a
mass-spring-damper, etc. are others. Controllers and the simulator are written
against this abstraction, so the same closed-loop machinery drives every plant.

Everything here is pure NumPy/SciPy (no Pinocchio), so it imports and runs on any
machine.
"""

from .plant import Plant
from .state_space import StateSpace
from .discretize import c2d
from .linearize import linearize_plant
from . import examples

__all__ = ["Plant", "StateSpace", "c2d", "linearize_plant", "examples"]
