"""Readers for VASP relaxation output (OUTCAR and POSCAR/CONTCAR)."""

from dataclasses import dataclass
from os import PathLike
from pathlib import Path

import numpy as np
import numpy.typing as npt

type StrPath = str | PathLike[str]

_FORCE_HEADER = "TOTAL-FORCE (eV/Angst)"
_ENERGY_HEADER = "FREE ENERGIE OF THE ION-ELECTRON SYSTEM"


@dataclass(frozen=True)
class Relaxation:
    """Per-ionic-step data from a VASP relaxation.

    Attributes:
        energies: Free energy TOTEN of each ionic step in eV, shape ``(nsteps,)``.
        energies_sigma0: Energy extrapolated to sigma -> 0 in eV, ``(nsteps,)``.
        forces: Cartesian forces in eV/Angstrom, shape ``(nsteps, nions, 3)``.
        ediff: Electronic convergence criterion EDIFF, if found.
        ediffg: Ionic convergence criterion EDIFFG, if found. Negative values
            are force criteria in eV/Angstrom, positive values energy criteria.
    """

    energies: npt.NDArray[np.float64]
    energies_sigma0: npt.NDArray[np.float64]
    forces: npt.NDArray[np.float64]
    ediff: float | None = None
    ediffg: float | None = None

    @property
    def nsteps(self) -> int:
        """Number of completed ionic steps."""
        return int(self.energies.shape[0])

    @property
    def steps(self) -> npt.NDArray[np.int64]:
        """One-based ionic step numbers."""
        return np.arange(1, self.nsteps + 1, dtype=np.int64)

    def force_norms(
        self, mask: npt.NDArray[np.bool_] | None = None
    ) -> npt.NDArray[np.float64]:
        """Return the force magnitude on every atom, shape ``(nsteps, nions)``.

        Args:
            mask: Optional ``(nions, 3)`` array, True where a Cartesian
                component is free to move. Fixed components are ignored.
        """
        forces = self.forces if mask is None else np.where(mask, self.forces, 0.0)
        return np.asarray(np.linalg.norm(forces, axis=2), dtype=np.float64)

    def max_forces(
        self, mask: npt.NDArray[np.bool_] | None = None
    ) -> npt.NDArray[np.float64]:
        """Return the largest atomic force magnitude per ionic step."""
        return np.asarray(self.force_norms(mask).max(axis=1), dtype=np.float64)

    def rms_forces(
        self, mask: npt.NDArray[np.bool_] | None = None
    ) -> npt.NDArray[np.float64]:
        """Return the root-mean-square atomic force magnitude per ionic step."""
        norms = self.force_norms(mask)
        return np.asarray(np.sqrt((norms**2).mean(axis=1)), dtype=np.float64)

    def energy_changes(self) -> npt.NDArray[np.float64]:
        """Return ``|E_i - E_{i-1}|`` for steps 2..n, shape ``(nsteps - 1,)``."""
        return np.asarray(np.abs(np.diff(self.energies)), dtype=np.float64)

    def is_converged(self, mask: npt.NDArray[np.bool_] | None = None) -> bool | None:
        """Report whether the final step meets EDIFFG, or None if unknown."""
        if self.ediffg is None or self.nsteps == 0:
            return None
        if self.ediffg < 0:
            return bool(self.max_forces(mask)[-1] < abs(self.ediffg))
        if self.nsteps < 2:
            return False
        return bool(self.energy_changes()[-1] < self.ediffg)


def _parse_tag(line: str, tag: str) -> float | None:
    """Extract ``TAG = value`` from an OUTCAR parameter line."""
    head, _, tail = line.partition("=")
    if head.strip() != tag:
        return None
    return float(tail.split()[0].rstrip(";"))


def read_outcar(path: StrPath) -> Relaxation:
    """Read energies, forces and convergence criteria from an OUTCAR.

    An unfinished final ionic step (forces without an energy, or vice versa)
    is dropped so that every returned step has both.

    Args:
        path: Path to the OUTCAR file.

    Raises:
        ValueError: If the file contains no ionic steps.
    """
    lines = Path(path).read_text(errors="replace").splitlines()

    nions: int | None = None
    ediff: float | None = None
    ediffg: float | None = None
    forces: list[npt.NDArray[np.float64]] = []
    energies: list[float] = []
    energies_sigma0: list[float] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        if nions is None and "NIONS =" in line:
            nions = int(line.split("NIONS =")[1].split()[0])
        elif ediff is None and (value := _parse_tag(line, "EDIFF")) is not None:
            ediff = value
        elif ediffg is None and (value := _parse_tag(line, "EDIFFG")) is not None:
            ediffg = value
        elif _FORCE_HEADER in line:
            if nions is None:
                raise ValueError(f"{path}: force block found before NIONS")
            block = lines[i + 2 : i + 2 + nions]
            if len(block) < nions:
                break
            forces.append(
                np.array([row.split()[3:6] for row in block], dtype=np.float64)
            )
            i += 2 + nions
            continue
        elif _ENERGY_HEADER in line:
            block = lines[i + 1 : i + 6]
            toten = next((r for r in block if "TOTEN" in r), None)
            sigma0 = next((r for r in block if "sigma->0" in r), None)
            if toten is None or sigma0 is None:
                break
            energies.append(float(toten.split("=")[1].split()[0]))
            energies_sigma0.append(float(sigma0.split("=")[-1].split()[0]))
        i += 1

    nsteps = min(len(forces), len(energies))
    if nsteps == 0:
        raise ValueError(f"{path}: no completed ionic steps found")

    return Relaxation(
        energies=np.array(energies[:nsteps], dtype=np.float64),
        energies_sigma0=np.array(energies_sigma0[:nsteps], dtype=np.float64),
        forces=np.stack(forces[:nsteps]),
        ediff=ediff,
        ediffg=ediffg,
    )


def read_selective_dynamics(path: StrPath) -> npt.NDArray[np.bool_] | None:
    """Read the selective-dynamics mask from a POSCAR or CONTCAR.

    Args:
        path: Path to the POSCAR/CONTCAR file.

    Returns:
        A ``(nions, 3)`` boolean array that is True where a component may
        move, or None if the file does not use selective dynamics.
    """
    lines = Path(path).read_text().splitlines()
    # Line 5 holds species names (VASP 5+) or directly the ion counts.
    row = 5 if lines[5].split()[0].isdigit() else 6
    nions = sum(int(n) for n in lines[row].split())
    row += 1
    if not lines[row].strip().lower().startswith("s"):
        return None
    start = row + 2
    flags = [line.split()[3:6] for line in lines[start : start + nions]]
    mask: npt.NDArray[np.bool_] = np.array(flags, dtype=str) == "T"
    return mask
