"""Tests for the public API and command-line interface."""

from importlib.metadata import version

import numpy as np
import pytest

from template_python import __version__, line, print_hello
from template_python.__main__ import build_parser, main


def test_version_matches_distribution_metadata() -> None:
    """The runtime version stays in sync with package metadata."""
    assert __version__ == version("template-python")


def test_print_hello_uses_default_name(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The default greeting preserves the original public behavior."""
    print_hello()
    assert capsys.readouterr().out == "Hello, World!\n"


def test_print_hello_accepts_a_name(capsys: pytest.CaptureFixture[str]) -> None:
    """Callers can customize the greeting."""
    print_hello("Ada")
    assert capsys.readouterr().out == "Hello, Ada!\n"


def test_line_preserves_default_shape_and_endpoints() -> None:
    """The example NumPy API keeps its original defaults."""
    values = line()

    assert values.shape == (100,)
    assert values.dtype == np.float64
    assert values[0] == 0.0
    assert values[-1] == 1.0


def test_line_accepts_custom_bounds_and_size() -> None:
    """The example API is useful beyond its defaults."""
    np.testing.assert_allclose(line(-1.0, 1.0, num=3), [-1.0, 0.0, 1.0])


def test_parser_describes_the_cli() -> None:
    """The parser advertises the command's purpose."""
    assert build_parser().description == "Print a friendly greeting."


def test_cli_prints_a_greeting(capsys: pytest.CaptureFixture[str]) -> None:
    """The console entry point delegates to the public API."""
    assert main(["Grace"]) == 0
    assert capsys.readouterr().out == "Hello, Grace!\n"
