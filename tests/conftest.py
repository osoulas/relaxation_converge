"""Synthetic VASP files shared by the tests."""

from collections.abc import Callable
from pathlib import Path

import pytest

type OutcarFactory = Callable[..., Path]

HEADER = """\
 vasp.6.4.2 18Apr23 (build Jan 01 2024) complex
   number of dos      NEDOS =    301   number of ions     NIONS =      2
   EDIFF  = 0.1E-05   stopping-criterion for ELM
   EDIFFG = {ediffg}   stopping-criterion for IOM
"""

FORCES = """\
 POSITION                                       TOTAL-FORCE (eV/Angst)
 -----------------------------------------------------------------------------------
      0.00000      0.00000      0.00000         {f0:.6f}      0.000000      0.000000
      1.00000      1.00000      1.00000         0.000000      {f1:.6f}      0.000000
 -----------------------------------------------------------------------------------
"""

ENERGY = """\
  FREE ENERGIE OF THE ION-ELECTRON SYSTEM (eV)
  ---------------------------------------------------
  free  energy   TOTEN  =       {e:.8f} eV

  energy  without entropy=      {e:.8f}  energy(sigma->0) =      {s:.8f}
"""

# (force on atom 0 along x, force on atom 1 along y, energy)
STEPS = [(0.5, 0.3, -10.0), (0.1, 0.2, -10.4), (0.01, 0.005, -10.41)]


@pytest.fixture
def write_outcar(tmp_path: Path) -> OutcarFactory:
    """Return a factory writing an OUTCAR with the given steps and EDIFFG."""

    def factory(
        steps: list[tuple[float, float, float]] = STEPS,
        ediffg: str = "-.2E-01",
        tail: str = "",
        header: str = HEADER,
    ) -> Path:
        text = header.format(ediffg=ediffg)
        for f0, f1, e in steps:
            text += FORCES.format(f0=f0, f1=f1)
            text += ENERGY.format(e=e, s=e - 0.001)
        path = tmp_path / "OUTCAR"
        path.write_text(text + tail)
        return path

    return factory
