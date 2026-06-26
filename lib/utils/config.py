"""Load ``config/params.yaml`` into a dot-accessible object.

Keeps the MATLAB habit of one parameter file: edit YAML, never hard-code.
"""

from __future__ import annotations

from pathlib import Path

import yaml


class Config(dict):
    """A dict that also supports attribute access, recursively.

    ``cfg.simulation.dt`` and ``cfg["simulation"]["dt"]`` are equivalent. Dicts nested
    inside lists are wrapped too, so ``cfg.items_list[0].field`` works.

    Note: keys that collide with real ``dict`` methods (``items``, ``keys``,
    ``values``, ``update``, ...) are reserved — access them with ``cfg["items"]``,
    not ``cfg.items``. Use plain config key names to avoid the clash.
    """

    @staticmethod
    def _wrap(value):
        if isinstance(value, dict):
            return Config(value)
        if isinstance(value, list):
            return [Config(v) if isinstance(v, dict) else v for v in value]
        return value

    def __getattr__(self, name):
        try:
            value = self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc
        return Config._wrap(value)


def project_root() -> Path:
    """Return the project root (two levels up from this file: lib/utils → root)."""
    return Path(__file__).resolve().parents[2]


def load_config(path: str | Path = "config/params.yaml") -> Config:
    """Load a YAML config file.

    Parameters
    ----------
    path : str | Path
        Path to the YAML file. Relative paths resolve from the project root.

    Returns
    -------
    cfg : Config
        Parsed configuration with attribute access.
    """
    path = Path(path)
    if not path.is_absolute():
        path = project_root() / path
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return Config(data or {})  # empty YAML -> {} rather than None
