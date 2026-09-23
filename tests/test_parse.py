"""Tests for the OUTCAR and POSCAR readers."""

from pathlib import Path

import numpy as np
import pytest

from relaxation_converge import read_outcar, read_selective_dynamics
from relaxation_converge.parse import Relaxation

from .conftest import FORCES, OutcarFactory


def test_read_outcar_extracts_energies_forces_and_criteria(
    write_outcar: OutcarFactory,
) -> None:
    """Every completed ionic step is read along with EDIFF and EDIFFG."""
    relax = read_outcar(write_outcar())

    assert relax.nsteps == 3
    np.testing.assert_array_equal(relax.steps, [1, 2, 3])
    np.testing.assert_allclose(relax.energies, [-10.0, -10.4, -10.41])
    np.testing.assert_allclose(relax.energies_sigma0, [-10.001, -10.401, -10.411])
    assert relax.forces.shape == (3, 2, 3)
    assert relax.ediff == pytest.approx(1e-6)
    assert relax.ediffg == pytest.approx(-0.02)


def test_force_and_energy_summaries(write_outcar: OutcarFactory) -> None:
    """Max, RMS and energy-change summaries follow their definitions."""
    relax = read_outcar(write_outcar())

    np.testing.assert_allclose(relax.max_forces(), [0.5, 0.2, 0.01])
    np.testing.assert_allclose(relax.rms_forces()[0], np.sqrt((0.25 + 0.09) / 2))
    np.testing.assert_allclose(relax.energy_changes(), [0.4, 0.01])


def test_mask_excludes_fixed_components(write_outcar: OutcarFactory) -> None:
    """Forces on fixed degrees of freedom do not count."""
    relax = read_outcar(write_outcar())
    mask = np.array([[False, False, False], [True, True, True]])

    np.testing.assert_allclose(relax.max_forces(mask), [0.3, 0.2, 0.005])


def test_unfinished_last_step_is_dropped(write_outcar: OutcarFactory) -> None:
    """Forces without a following energy block are ignored."""
    tail = FORCES.format(f0=1.0, f1=1.0)
    assert read_outcar(write_outcar(tail=tail)).nsteps == 3


def test_truncated_force_block_stops_reading(write_outcar: OutcarFactory) -> None:
    """A force block cut off mid-write ends parsing cleanly."""
    tail = "\n".join(FORCES.format(f0=1.0, f1=1.0).splitlines()[:3])
    assert read_outcar(write_outcar(tail=tail)).nsteps == 3


def test_truncated_energy_block_stops_reading(write_outcar: OutcarFactory) -> None:
    """An energy block cut off mid-write ends parsing cleanly."""
    header = "  FREE ENERGIE OF THE ION-ELECTRON SYSTEM (eV)\n"
    tail = FORCES.format(f0=1.0, f1=1.0) + header
    assert read_outcar(write_outcar(tail=tail)).nsteps == 3


def test_missing_criteria_are_none(write_outcar: OutcarFactory) -> None:
    """Files without EDIFF/EDIFFG still parse."""
    relax = read_outcar(write_outcar(header="   NIONS =      2\n"))
    assert relax.ediff is None
    assert relax.ediffg is None
    assert relax.is_converged() is None


def test_empty_outcar_raises(write_outcar: OutcarFactory) -> None:
    """A run with no completed steps is an error."""
    with pytest.raises(ValueError, match="no completed ionic steps"):
        read_outcar(write_outcar(steps=[]))


def test_forces_before_nions_raises(write_outcar: OutcarFactory) -> None:
    """A malformed file without NIONS is reported."""
    with pytest.raises(ValueError, match="before NIONS"):
        read_outcar(write_outcar(header=""))


@pytest.mark.parametrize(
    ("ediffg", "expected"),
    [(-0.02, True), (-0.001, False), (0.05, True), (0.001, False)],
)
def test_is_converged(ediffg: float, expected: bool) -> None:
    """Force (negative) and energy (positive) criteria are both honored."""
    relax = Relaxation(
        energies=np.array([-10.0, -10.4, -10.41]),
        energies_sigma0=np.zeros(3),
        forces=np.full((3, 1, 3), 0.005),
        ediffg=ediffg,
    )
    assert relax.is_converged() is expected


def test_single_step_energy_criterion_is_not_converged() -> None:
    """An energy criterion needs at least two steps to compare."""
    relax = Relaxation(
        energies=np.array([-1.0]),
        energies_sigma0=np.array([-1.0]),
        forces=np.zeros((1, 1, 3)),
        ediffg=0.1,
    )
    assert relax.is_converged() is False


POSCAR = """\
comment
1.0
  5.0 0.0 0.0
  0.0 5.0 0.0
  0.0 0.0 5.0
{species}  2
Selective dynamics
Direct
  0.0 0.0 0.0 F F F
  0.5 0.5 0.5 T T F
"""


@pytest.mark.parametrize("species", ["Si\n", ""])
def test_read_selective_dynamics(tmp_path: Path, species: str) -> None:
    """Flags are read with and without a species-name line."""
    path = tmp_path / "POSCAR"
    path.write_text(POSCAR.format(species=species))

    mask = read_selective_dynamics(path)

    assert mask is not None
    np.testing.assert_array_equal(mask, [[False] * 3, [True, True, False]])


def test_poscar_without_selective_dynamics(tmp_path: Path) -> None:
    """Plain POSCARs have no mask."""
    path = tmp_path / "POSCAR"
    text = POSCAR.format(species="Si\n").replace("Selective dynamics\n", "")
    path.write_text(text)

    assert read_selective_dynamics(path) is None
