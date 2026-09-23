"""Command-line interface for the example package."""

import argparse
from collections.abc import Sequence
from typing import cast

from .main import print_hello


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(description="Print a friendly greeting.")
    parser.add_argument("name", nargs="?", default="World", help="name to greet")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface."""
    arguments = build_parser().parse_args(argv)
    print_hello(cast(str, arguments.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
