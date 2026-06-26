"""The :class:`Plant` abstraction — a controllable dynamical system.

A plant exposes its state/input dimensions and a continuous-time state equation

    x' = f(x, u, t)

plus an optional output map ``y = h(x, u, t)`` (defaulting to full-state output
``y = x``). The robot, a linear state-space model, a cart-pole — all subclass this,
so :func:`lib.sim.simulate.simulate` and the state-feedback controllers work the
same way on every one.

Pure NumPy: this module never imports Pinocchio.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class Plant(ABC):
    """Abstract continuous-time plant ``x' = f(x, u, t)``.

    Subclasses must set the integer attributes ``nx`` (state dimension) and ``nu``
    (input dimension) and implement :meth:`dynamics`. Override :meth:`output` for a
    non-trivial measurement map; the default returns the full state.

    Conventions (control-faithful symbols)
    --------------------------------------
    x : (nx,) state vector.
    u : (nu,) control input.
    y : (ny,) measured output (``ny == nx`` by default).
    t : float, time [s] — present for time-varying plants; autonomous plants ignore it.
    """

    nx: int
    nu: int

    @abstractmethod
    def dynamics(self, x: np.ndarray, u: np.ndarray, t: float = 0.0) -> np.ndarray:
        """Continuous-time state derivative ``x' = f(x, u, t)``.

        Parameters
        ----------
        x : (nx,) state.
        u : (nu,) input.
        t : float, time [s] (ignored by autonomous plants).

        Returns
        -------
        xdot : (nx,) state derivative.
        """
        raise NotImplementedError

    def output(self, x: np.ndarray, u: np.ndarray, t: float = 0.0) -> np.ndarray:
        """Measurement map ``y = h(x, u, t)``. Default: full-state output ``y = x``.

        Returns
        -------
        y : (ny,) output (``ny == nx`` for the default).
        """
        return np.asarray(x, dtype=float)

    @property
    def ny(self) -> int:
        """Output dimension (``nx`` unless :meth:`output` is overridden)."""
        return self.nx

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"{type(self).__name__}(nx={self.nx}, nu={self.nu})"
