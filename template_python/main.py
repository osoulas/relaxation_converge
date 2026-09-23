"""Small example functions for the package template."""

import numpy as np
import numpy.typing as npt


def print_hello(name: str = "World") -> None:
    """Print a friendly greeting.

    Args:
        name: The person or subject to greet.
    """
    print(f"Hello, {name}!")


def line(
    start: float = 0.0,
    stop: float = 1.0,
    num: int = 100,
) -> npt.NDArray[np.float64]:
    """Return evenly spaced values over a closed interval.

    Args:
        start: First value in the sequence.
        stop: Last value in the sequence.
        num: Number of values to generate.

    Returns:
        A one-dimensional array including both interval endpoints.
    """
    return np.linspace(start, stop, num=num, dtype=np.float64)
