"""Linear time-invariant (LTI) state-space plant.

Implements the textbook continuous-time model

    x' = A x + B u
    y  = C x + D u

as a concrete :class:`lib.systems.plant.Plant`, so an LTI system drops straight into
the same simulator and controllers as the robot. ``C`` defaults to the identity
(full-state output) and ``D`` to zero. Interop helpers convert to/from
``python-control`` state-space objects.

Pure NumPy/SciPy — no Pinocchio.
"""

from __future__ import annotations

import numpy as np

from .plant import Plant


class StateSpace(Plant):
    """Continuous-time LTI plant ``x' = A x + B u``, ``y = C x + D u``.

    Parameters
    ----------
    A : (nx, nx) state matrix.
    B : (nx, nu) input matrix.
    C : (ny, nx), optional output matrix. Default: identity (``y = x``).
    D : (ny, nu), optional feedthrough matrix. Default: zeros.

    Attributes
    ----------
    A, B, C, D : ndarray
        The system matrices (float64).
    nx, nu, ny : int
        State, input, and output dimensions.
    """

    def __init__(self, A, B, C=None, D=None) -> None:
        self.A = np.atleast_2d(np.asarray(A, dtype=float))
        self.B = np.atleast_2d(np.asarray(B, dtype=float))

        nx = self.A.shape[0]
        if self.A.shape != (nx, nx):
            raise ValueError(f"A must be square, got {self.A.shape}")
        if self.B.shape[0] != nx:
            raise ValueError(f"B must have {nx} rows, got {self.B.shape}")
        nu = self.B.shape[1]

        self.C = np.eye(nx) if C is None else np.atleast_2d(np.asarray(C, dtype=float))
        if self.C.shape[1] != nx:
            raise ValueError(f"C must have {nx} columns, got {self.C.shape}")
        ny = self.C.shape[0]
        self.D = np.zeros((ny, nu)) if D is None else np.atleast_2d(np.asarray(D, dtype=float))
        if self.D.shape != (ny, nu):
            raise ValueError(f"D must be {(ny, nu)}, got {self.D.shape}")

        self.nx = nx
        self.nu = nu
        self._ny = ny

    @property
    def ny(self) -> int:
        return self._ny

    def dynamics(self, x: np.ndarray, u: np.ndarray, t: float = 0.0) -> np.ndarray:
        """Return ``A x + B u`` (shape (nx,)). Time-invariant: ``t`` is ignored."""
        x = np.asarray(x, dtype=float)
        u = np.asarray(u, dtype=float)
        return self.A @ x + self.B @ u

    def output(self, x: np.ndarray, u: np.ndarray, t: float = 0.0) -> np.ndarray:
        """Return ``C x + D u`` (shape (ny,))."""
        x = np.asarray(x, dtype=float)
        u = np.asarray(u, dtype=float)
        return self.C @ x + self.D @ u

    # -- analysis -----------------------------------------------------------
    def controllability(self) -> np.ndarray:
        """Controllability matrix ``[B, AB, A^2 B, ..., A^{nx-1} B]`` (nx, nx*nu)."""
        cols = [self.B]
        for _ in range(1, self.nx):
            cols.append(self.A @ cols[-1])
        return np.hstack(cols)

    def is_controllable(self, tol: float = 1e-9) -> bool:
        """True iff the controllability matrix has full row rank ``nx``."""
        return np.linalg.matrix_rank(self.controllability(), tol=tol) == self.nx

    # -- python-control interop --------------------------------------------
    def to_control(self):
        """Return an equivalent ``control.StateSpace`` (requires python-control)."""
        import control

        return control.ss(self.A, self.B, self.C, self.D)

    @classmethod
    def from_control(cls, sys) -> "StateSpace":
        """Build a :class:`StateSpace` from a ``control.StateSpace`` object."""
        return cls(sys.A, sys.B, sys.C, sys.D)
