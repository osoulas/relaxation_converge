"""Public package interface."""

from importlib.metadata import version

from .main import line, print_hello

__version__ = version("template-python")

__all__ = ["__version__", "line", "print_hello"]
