"""Public package interface."""

from importlib.metadata import version

from .parse import Relaxation, read_outcar, read_selective_dynamics
from .plot import plot_convergence

__version__ = version("relaxation-converge")

__all__ = [
    "Relaxation",
    "__version__",
    "plot_convergence",
    "read_outcar",
    "read_selective_dynamics",
]
