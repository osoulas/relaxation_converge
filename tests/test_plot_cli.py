"""Tests for plotting and the command-line interface."""

from importlib.metadata import version
from pathlib import Path

import pytest

from relaxation_converge import (
    __version__,
    plot_convergence,
    read_outcar,
    terminal_plot,
)
from relaxation_converge.__main__ import build_parser, main

from .conftest import OutcarFactory


def test_version_matches_distribution_metadata() -> None:
    """The runtime version stays in sync with package metadata."""
    assert __version__ == version("relaxation-converge")


@pytest.mark.parametrize("ediffg", ["-.2E-01", "0.1E-02"])
def test_plot_has_three_panels_and_threshold(
    write_outcar: OutcarFactory, ediffg: str
) -> None:
    """The figure shows energy, energy change and force panels."""
    fig = plot_convergence(read_outcar(write_outcar(ediffg=ediffg)), title="run")

    _, ax_de, ax_f = fig.axes
    assert ax_de.get_yscale() == ax_f.get_yscale() == "log"
    threshold_axis = ax_f if ediffg.startswith("-") else ax_de
    legend = threshold_axis.get_legend()
    assert legend is not None
    labels = [t.get_text() for t in legend.get_texts()]
    assert any("EDIFFG" in label for label in labels)
    assert fig.get_suptitle() == "run"


def test_plot_single_step_without_criteria(write_outcar: OutcarFactory) -> None:
    """A one-step run without EDIFFG still plots."""
    relax = read_outcar(write_outcar(steps=[(0.1, 0.1, -1.0)], header=" NIONS = 2\n"))
    fig = plot_convergence(relax)
    assert len(fig.axes) == 3
    assert fig.get_suptitle() == ""


def test_parser_defaults() -> None:
    """The CLI defaults to ./OUTCAR and does not save an image."""
    args = build_parser().parse_args([])
    assert args.outcar == Path("OUTCAR")
    assert args.save is None
    assert args.poscar is None
    assert args.height == 60


def test_cli_prints_summary_and_saves_plot(
    write_outcar: OutcarFactory,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """--save FILE writes the image as well as the terminal output."""
    output = tmp_path / "out.png"
    assert main([str(write_outcar()), "--save", str(output)]) == 0

    out = capsys.readouterr().out
    assert "Converged: yes" in out
    assert "-10.410000" in out
    assert "Ionic step" in out
    assert output.stat().st_size > 0


def test_save_without_file_uses_default_name(
    write_outcar: OutcarFactory,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A bare -s saves convergence.png in the working directory."""
    outcar = write_outcar()
    monkeypatch.chdir(tmp_path)
    assert main([str(outcar), "-s"]) == 0
    assert (tmp_path / "convergence.png").exists()


def test_cli_accepts_poscar_mask(
    write_outcar: OutcarFactory,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Fixed atoms from a POSCAR are excluded from the force check."""
    poscar = tmp_path / "POSCAR"
    poscar.write_text(
        "c\n1.0\n1 0 0\n0 1 0\n0 0 1\nSi\n2\nSelective dynamics\nDirect\n"
        "0 0 0 F F F\n0.5 0.5 0.5 T T T\n"
    )
    assert main([str(write_outcar()), "-p", str(poscar)]) == 0
    assert "0.0050" in capsys.readouterr().out


@pytest.mark.parametrize(("ediffg", "color"), [("-.2E-01", True), ("0.1E-02", False)])
def test_terminal_plot_renders_panels(
    write_outcar: OutcarFactory, ediffg: str, color: bool
) -> None:
    """The text plot shows all three panels and the EDIFFG threshold."""
    relax = read_outcar(write_outcar(ediffg=ediffg))
    text = terminal_plot(relax, width=80, height=45, color=color)

    assert "E_final = -10.410000 eV" in text
    assert "EDIFFG" in text
    assert "Ionic step" in text
    assert ("\x1b[" in text) is color


def test_terminal_plot_single_step(write_outcar: OutcarFactory) -> None:
    """A one-step run without EDIFFG still renders."""
    relax = read_outcar(write_outcar(steps=[(0.1, 0.1, -1.0)], header=" NIONS = 2\n"))
    assert "EDIFFG" not in terminal_plot(relax, width=60, height=30, color=False)


def test_cli_plots_in_terminal_by_default(
    write_outcar: OutcarFactory,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Without --save the plot is printed and no image is written."""
    outcar = write_outcar()
    monkeypatch.chdir(tmp_path)
    assert main([str(outcar), "--no-color", "--height", "75"]) == 0

    out = capsys.readouterr().out
    assert "Ionic step" in out
    assert len(out.splitlines()) >= 75
    assert not list(tmp_path.glob("*.png"))
