"""Unit tests for lib.utils.io (pure numpy, no Pinocchio)."""

import numpy as np

from lib.utils import io


def test_save_load_roundtrip(tmp_path, monkeypatch):
    """Arrays survive a save -> load cycle without loss."""
    monkeypatch.setattr(io, "project_root", lambda: tmp_path)
    t = np.linspace(0, 1, 100)
    q = np.arange(200, dtype=float).reshape(100, 2)
    path = io.save_results("trial", t=t, q=q)
    loaded = io.load_results(path)
    np.testing.assert_array_equal(loaded["t"], t)
    np.testing.assert_array_equal(loaded["q"], q)


def test_save_results_auto_appends_npz(tmp_path, monkeypatch):
    monkeypatch.setattr(io, "project_root", lambda: tmp_path)
    path = io.save_results("sim", x=np.array([1.0]))
    assert path.suffix == ".npz"


def test_results_dir_creates_run_id_subdir(tmp_path, monkeypatch):
    monkeypatch.setattr(io, "project_root", lambda: tmp_path)
    d = io.results_dir("run_42")
    assert d.exists()
    assert d.name == "run_42"


def test_run_id_isolates_files(tmp_path, monkeypatch):
    monkeypatch.setattr(io, "project_root", lambda: tmp_path)
    p1 = io.save_results("data", run_id="run_a", x=np.array([1.0]))
    p2 = io.save_results("data", run_id="run_b", x=np.array([2.0]))
    assert p1 != p2
    assert io.load_results(p1)["x"][0] == 1.0
    assert io.load_results(p2)["x"][0] == 2.0
