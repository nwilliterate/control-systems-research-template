"""Kinematics helpers (frame placement and Jacobians) via Pinocchio.

Provides the geometric/analytic Jacobian needed for task-space (operational-space)
control studies. One job per file (m-file style). Pinocchio is reached only through
``robot._pin`` so importing this module never requires Pinocchio.
"""

from __future__ import annotations

import numpy as np

from .robot_model import RobotModel


def frame_jacobian(robot: RobotModel, q: np.ndarray, frame_name: str,
                   reference: str = "local_world_aligned") -> np.ndarray:
    """Spatial Jacobian of a frame.

    Parameters
    ----------
    robot : RobotModel
    q : (nq,) joint positions [rad].
    frame_name : name of the operational frame in the URDF.
    reference : 'local', 'world', or 'local_world_aligned' (default) — the frame in
        which the 6xnv Jacobian is expressed.

    Returns
    -------
    J : (6, nv) spatial Jacobian [linear (3); angular (3)] mapping joint velocities
        to the frame's spatial velocity.
    """
    pin = robot._pin
    q = np.asarray(q, dtype=float)

    frame_id = robot.model.getFrameId(frame_name)
    ref_map = {
        "local": pin.ReferenceFrame.LOCAL,
        "world": pin.ReferenceFrame.WORLD,
        "local_world_aligned": pin.ReferenceFrame.LOCAL_WORLD_ALIGNED,
    }
    if reference not in ref_map:
        raise ValueError(f"unknown reference {reference!r}; use {list(ref_map)}")

    pin.computeJointJacobians(robot.model, robot.data, q)
    pin.updateFramePlacements(robot.model, robot.data)
    return pin.getFrameJacobian(robot.model, robot.data, frame_id, ref_map[reference])


def frame_position(robot: RobotModel, q: np.ndarray, frame_name: str) -> np.ndarray:
    """Cartesian position [m] of a frame's origin in the world frame.

    Returns
    -------
    p : (3,) world-frame position of the named frame.
    """
    pin = robot._pin
    q = np.asarray(q, dtype=float)
    frame_id = robot.model.getFrameId(frame_name)
    pin.forwardKinematics(robot.model, robot.data, q)
    pin.updateFramePlacements(robot.model, robot.data)
    return np.array(robot.data.oMf[frame_id].translation)
