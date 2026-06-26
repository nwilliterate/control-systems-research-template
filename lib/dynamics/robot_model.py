"""Load a URDF robot and expose its Pinocchio model/data.

One class, one job (m-file style): :class:`RobotModel` is a thin, readable wrapper
around Pinocchio so experiment scripts never touch the Pinocchio C++ API directly.

Pinocchio is imported lazily so importing this file never fails on a machine
without Pinocchio; the error is raised only when you actually build a model.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence

import numpy as np


def _import_pinocchio():
    """Import pinocchio with a helpful message if it is missing."""
    try:
        import pinocchio as pin
        return pin
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError(
            "Pinocchio is required for lib.dynamics. Install it with conda:\n"
            "    conda install -c conda-forge pinocchio\n"
            "(see environment.yml). Pure-numpy code does not need Pinocchio."
        ) from exc


class RobotModel:
    """Rigid-body model of a robot loaded from a URDF.

    Parameters
    ----------
    urdf_path : str | Path
        Path to the robot's URDF file.
    gravity : sequence of float, optional
        Gravity vector [m/s^2] in the world frame. Defaults to (0, 0, -9.81).

    Attributes
    ----------
    model, data : pinocchio Model / Data
        The underlying Pinocchio objects (for advanced use).
    nq : int
        Configuration-space dimension (joint positions).
    nv : int
        Velocity-space dimension (joint velocities). For revolute/prismatic
        robots ``nq == nv``.
    """

    def __init__(self, urdf_path, gravity: Optional[Sequence[float]] = None) -> None:
        pin = _import_pinocchio()
        self._pin = pin

        urdf_path = str(Path(urdf_path))
        self.model = pin.buildModelFromUrdf(urdf_path)
        if gravity is not None:
            self.model.gravity.linear = np.asarray(gravity, dtype=float)
        self.data = self.model.createData()

        self.nq = self.model.nq
        self.nv = self.model.nv

    # -- convenience constructors ------------------------------------------
    def neutral(self) -> np.ndarray:
        """Return the neutral configuration q, shape (nq,)."""
        return self._pin.neutral(self.model)

    def random_configuration(self) -> np.ndarray:
        """Return a random valid configuration q, shape (nq,)."""
        return self._pin.randomConfiguration(self.model)

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"RobotModel(name={self.model.name!r}, nq={self.nq}, nv={self.nv})"
