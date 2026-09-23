"""Convergence plots for VASP relaxations."""

import numpy as np
import numpy.typing as npt
from matplotlib.figure import Figure

from .parse import Relaxation

_THRESHOLD_COLOR = "tab:red"


def plot_convergence(
    relaxation: Relaxation,
    mask: npt.NDArray[np.bool_] | None = None,
    title: str | None = None,
) -> Figure:
    """Plot energy, energy change and force convergence against ionic step.

    Panels, top to bottom: energy relative to the final step, the absolute
    energy change between steps, and the maximum and RMS atomic forces.
    EDIFFG is drawn on the energy-change panel when positive and on the
    force panel when negative.

    Args:
        relaxation: Parsed relaxation data.
        mask: Optional selective-dynamics mask; fixed components are ignored.
        title: Optional figure title.

    Returns:
        The Matplotlib figure; save it with ``fig.savefig(path)``.
    """
    steps = relaxation.steps
    energies = relaxation.energies
    ediffg = relaxation.ediffg

    fig = Figure(figsize=(6.0, 7.5), layout="constrained")
    ax_e, ax_de, ax_f = fig.subplots(3, 1, sharex=True)

    ax_e.plot(steps, energies - energies[-1], marker="o", markersize=3)
    ax_e.set_ylabel(r"$E - E_\mathrm{final}$ (eV)")
    ax_e.text(
        0.98,
        0.95,
        rf"$E_\mathrm{{final}}$ = {energies[-1]:.6f} eV",
        transform=ax_e.transAxes,
        ha="right",
        va="top",
    )

    changes = relaxation.energy_changes()
    if changes.size:
        ax_de.semilogy(steps[1:], changes, marker="o", markersize=3)
    if ediffg is not None and ediffg > 0:
        ax_de.axhline(
            ediffg, color=_THRESHOLD_COLOR, ls="--", label=f"EDIFFG = {ediffg:g} eV"
        )
        ax_de.legend(loc="upper right")
    ax_de.set_ylabel(r"$|\Delta E|$ (eV)")

    ax_f.semilogy(steps, relaxation.max_forces(mask), "o-", ms=3, label="max")
    ax_f.semilogy(steps, relaxation.rms_forces(mask), "s-", ms=3, label="RMS")
    if ediffg is not None and ediffg < 0:
        ax_f.axhline(
            -ediffg,
            color=_THRESHOLD_COLOR,
            ls="--",
            label=f"|EDIFFG| = {-ediffg:g} eV/Å",
        )
    ax_f.legend(loc="upper right")
    ax_f.set_ylabel("Force (eV/Å)")
    ax_f.set_xlabel("Ionic step")
    ax_f.xaxis.get_major_locator().set_params(integer=True)

    if title:
        fig.suptitle(title)
    return fig
