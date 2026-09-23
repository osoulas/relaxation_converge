"""Command-line interface: summarize and plot a VASP relaxation."""

import argparse
from collections.abc import Sequence
from pathlib import Path

from .parse import read_outcar, read_selective_dynamics
from .plot import plot_convergence
from .terminal import terminal_plot


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Plot energy and force convergence of a VASP relaxation."
    )
    parser.add_argument(
        "outcar", nargs="?", default="OUTCAR", type=Path, help="OUTCAR file"
    )
    parser.add_argument(
        "-p",
        "--poscar",
        type=Path,
        help="POSCAR/CONTCAR whose selective dynamics flags exclude fixed atoms",
    )
    parser.add_argument(
        "-s",
        "--save",
        nargs="?",
        const=Path("convergence.png"),
        type=Path,
        metavar="FILE",
        help="also save the plot as an image (default FILE: convergence.png)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=60,
        help="terminal plot height in lines (default: 60)",
    )
    parser.add_argument(
        "--no-color", action="store_true", help="plain text terminal plot"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface."""
    args = build_parser().parse_args(argv)
    outcar: Path = args.outcar
    save: Path | None = args.save

    relaxation = read_outcar(outcar)
    mask = read_selective_dynamics(args.poscar) if args.poscar else None

    fmax = relaxation.max_forces(mask)
    print(f"{'step':>5} {'energy (eV)':>16} {'dE (eV)':>12} {'Fmax (eV/A)':>12}")
    for step, energy, force in zip(
        relaxation.steps, relaxation.energies, fmax, strict=True
    ):
        change = "" if step == 1 else f"{energy - relaxation.energies[step - 2]:.3e}"
        print(f"{step:>5} {energy:>16.6f} {change:>12} {force:>12.4f}")

    status = {True: "yes", False: "no", None: "unknown (EDIFFG not found)"}
    print(f"Converged: {status[relaxation.is_converged(mask)]}")

    print(terminal_plot(relaxation, mask, height=args.height, color=not args.no_color))
    if save is not None:
        plot_convergence(relaxation, mask, title=str(outcar)).savefig(save, dpi=150)
        print(f"Saved {save}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
