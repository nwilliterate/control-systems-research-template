"""Unit tests for lib.utils.config (pure numpy/yaml, no Pinocchio)."""

import pytest

from lib.utils.config import Config, load_config


def test_dot_access_returns_scalar():
    cfg = Config({"sim": {"dt": 0.001}})
    assert cfg.sim.dt == 0.001


def test_list_of_scalars_not_wrapped():
    cfg = Config({"q": [0.5, 0.0]})
    assert isinstance(cfg.q, list)
    assert cfg.q == [0.5, 0.0]


def test_list_of_dicts_is_wrapped():
    cfg = Config({"waypoints": [{"k": 1}, {"k": 2}]})
    assert cfg.waypoints[0].k == 1
    assert cfg.waypoints[1].k == 2


def test_dict_method_names_are_reserved():
    """Keys colliding with dict methods (e.g. 'items') return the method, by design;
    access them via subscript instead."""
    cfg = Config({"items": [{"k": 1}]})
    assert callable(cfg.items)          # the dict method, not the value
    assert cfg["items"][0]["k"] == 1    # subscript reaches the data


def test_missing_key_raises_attribute_error():
    cfg = Config({"a": 1})
    with pytest.raises(AttributeError):
        _ = cfg.nonexistent


def test_load_config_reads_real_params():
    cfg = load_config("config/params.yaml")
    assert cfg.simulation.dt == pytest.approx(0.001)
    assert cfg.controller.type in {"pid", "computed_torque", "lqr", "none"}
