"""Adapter that presents a :class:`RobotModel` as a generic :class:`Plant`.

This is the bridge between the robot-specific dynamics (Pinocchio) and the
plant-agnostic core: the robot is *one* plant among many. With its stacked state
``x = [q, v]`` and input ``u = tau`` it satisfies the same ``dynamics(x, u, t)``
contract as a linear :class:`~lib.systems.state_space.StateSpace` or the cart-pole,
so the simulator and the state-feedback controllers treat it identically.

Pinocchio is only touched through the wrapped :class:`RobotModel` (lazily imported),
so importing this module never requires Pinocchio.
"""

from __future__ import annotations

import numpy as np

from lib.systems.plant import Plant
from .forward_dynamics import state_derivative
from .robot_model import RobotModel


class RobotPlant(Plant):
    """A :class:`RobotModel` exposed through the :class:`Plant` interface.

    Parameters
    ----------
    robot : RobotModel
        The rigid-body model (requires ``nq == nv``: revolute/prismatic joints).

    Attributes
    ----------
    nx : int
        State dimension ``nq + nv`` (stacked ``x = [q, v]``).
    nu : int
        Input dimension ``nv`` (joint torques ``u = tau``).
    nq, nv : int
        Configuration and velocity dimensions of the underlying robot.
    """

    def __init__(self, robot: RobotModel) -> None:
        self.robot = robot
        self.nq = robot.nq
        self.nv = robot.nv
        self.nx = robot.nq + robot.nv
        self.nu = robot.nv

    def dynamics(self, x: np.ndarray, u: np.ndarray, t: float = 0.0) -> np.ndarray:
        """Stacked state derivative ``[v, qdd]`` for state ``x=[q,v]`` and torque ``u``.

        Delegates to :func:`lib.dynamics.forward_dynamics.state_derivative`.
        """
        return state_derivative(self.robot, np.asarray(x, dtype=float),
                                np.asarray(u, dtype=float))

    def split(self, x: np.ndarray):
        """Return ``(q, v)`` from a stacked state ``x = [q, v]``."""
        x = np.asarray(x, dtype=float)
        return x[:self.nq], x[self.nq:]
