"""Consistent plotting helpers (the project's single plotting house style).

All figures should be produced through this module so studies look uniform and
land in ``results/figures``. Mirrors the MATLAB habit of a shared plotting style.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np

from .config import project_root

# House style — applied on import. Tweak here, not in every script.
plt.rcParams.update({
    "figure.figsize": (8, 5),
    "axes.grid": True,
    "grid.alpha": 0.3,
    "lines.linewidth": 1.8,
    "font.size": 11,
    "legend.frameon": False,
})


def plot_trajectory(t: np.ndarray, x: np.ndarray,
                    labels: Optional[Sequence[str]] = None,
                    ylabel: str = "state", title: str = "") -> plt.Figure:
    """Plot a multi-channel time trajectory.

    Parameters
    ----------
    t      : (N,) time vector [s].
    x      : (N, n) trajectory; each column is one channel. A transposed (n, N)
             array is accepted only when it is unambiguous (n != N); for a square
             input pass the canonical (N, n) shape.
    labels : optional list of n channel names for the legend.
    ylabel : y-axis label.
    title  : axes title.

    Returns
    -------
    fig : the Matplotlib figure (caller may further customize/save).
    """
    t = np.asarray(t)
    x = np.atleast_2d(np.asarray(x))
    # Orient to (N, n). Only auto-transpose when the first axis clearly isn't time
    # and the second clearly is (avoids silently mis-orienting a square array).
    if x.shape[0] != t.shape[0] and x.shape[1] == t.shape[0]:
        x = x.T
    if x.shape[0] != t.shape[0]:
        raise ValueError(
            f"x has no axis matching len(t)={t.shape[0]}; got x.shape={x.shape}. "
            "Pass x as (N, n) with N == len(t)."
        )

    fig, ax = plt.subplots()
    n = x.shape[1]
    for i in range(n):
        label = labels[i] if labels is not None and i < len(labels) else f"ch{i}"
        ax.plot(t, x[:, i], label=label)
    ax.set_xlabel("time [s]")
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.legend(loc="best")
    fig.tight_layout()
    return fig


def save_figure(fig: plt.Figure, name: str, subdir: str = "",
                dpi: int = 150) -> Path:
    """Save a figure under ``results/figures`` (created if needed).

    Parameters
    ----------
    fig    : the figure to save.
    name   : file name, e.g. ``"joint_positions.png"``.
    subdir : optional subfolder under results/figures (e.g. a run id).
    dpi    : resolution.

    Returns
    -------
    path : the full path written.
    """
    out_dir = project_root() / "results" / "figures" / subdir
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    return path
