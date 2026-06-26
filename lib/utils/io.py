"""Save and load experiment results reproducibly under ``results/data``.

Each run can write to its own ``run_id`` subfolder so studies don't overwrite each
other. The ``run_id`` is supplied by the caller (e.g. ``"run_01"`` or a timestamp
string); it is kept out of the library so behavior stays deterministic and testable.
Reusing the same ``run_id`` overwrites that run's files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np

from .config import project_root


def results_dir(run_id: Optional[str] = None) -> Path:
    """Return (and create) the data output directory for a run.

    Parameters
    ----------
    run_id : optional subfolder name (e.g. a timestamp ``"2026-06-26_14-30"``).
             When None, returns ``results/data`` itself.
    """
    base = project_root() / "results" / "data"
    out = base / run_id if run_id else base
    out.mkdir(parents=True, exist_ok=True)
    return out


def save_results(name: str, run_id: Optional[str] = None, **arrays) -> Path:
    """Save named numpy arrays to a ``.npz`` file.

    Example
    -------
    >>> save_results("sim", run_id="run_01", t=t, q=q, tau=tau)

    Parameters
    ----------
    name   : base file name (``.npz`` appended if missing).
    run_id : optional run subfolder.
    arrays : keyword arrays to store.

    Returns
    -------
    path : the written ``.npz`` path.
    """
    out_dir = results_dir(run_id)
    if not name.endswith(".npz"):
        name += ".npz"
    path = out_dir / name
    np.savez(path, **arrays)
    return path


def load_results(path: str | Path) -> dict:
    """Load a ``.npz`` results file into a plain dict of arrays."""
    with np.load(Path(path)) as data:
        return {key: data[key] for key in data.files}
