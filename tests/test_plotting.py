"""Unit tests for lib.utils.plotting (pure numpy + matplotlib Agg, no Pinocchio)."""

import matplotlib
matplotlib.use("Agg")  # headless backend; no display required
import matplotlib.pyplot as plt
import numpy as np
import pytest

from lib.utils.plotting import plot_trajectory


def test_row_major_input_plots_one_line_per_channel():
    """(N, n) input -> n lines."""
    t = np.linspace(0, 1, 50)
    x = np.random.rand(50, 3)
    fig = plot_trajectory(t, x, labels=["a", "b", "c"])
    assert len(fig.axes[0].lines) == 3
    plt.close(fig)


def test_transposed_input_is_reoriented():
    """(n, N) input (n != N) is transposed to (N, n)."""
    t = np.linspace(0, 1, 50)
    x = np.random.rand(3, 50)
    fig = plot_trajectory(t, x)
    assert len(fig.axes[0].lines) == 3
    plt.close(fig)


def test_mismatched_shape_raises():
    """An array with no axis matching len(t) is rejected, not mis-plotted."""
    t = np.linspace(0, 1, 50)
    x = np.random.rand(7, 9)
    with pytest.raises(ValueError):
        plot_trajectory(t, x)
