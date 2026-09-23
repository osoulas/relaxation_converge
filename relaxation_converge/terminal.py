"""Text-mode convergence plots drawn with plotext."""

import math
import shutil

import numpy as np
import numpy.typing as npt
import plotext as plt

from .parse import Relaxation

# plotext's own log scale misplaces extra series and mutates shared state, so
# log panels plot log10 values on a linear axis with relabelled ticks.
_FLOOR = 1e-12


def terminal_plot(
    relaxation: Relaxation,
    mask: npt.NDArray[np.bool_] | None = None,
    width: int | None = None,
    height: int = 60,
    color: bool = True,
) -> str:
    """Render the energy and force convergence panels as terminal text.

    Args:
        relaxation: Parsed relaxation data.
        mask: Optional selective-dynamics mask; fixed components are ignored.
        width: Plot width in characters; defaults to the terminal width.
        height: Total plot height in lines, shared by the three panels. It
            may exceed the terminal height; scroll up to see the top.
        color: Emit ANSI colors. Disable when piping to a file.

    Returns:
        The rendered plot, ready to print.
    """
    steps = relaxation.steps.tolist()
    energies = relaxation.energies
    changes = relaxation.energy_changes()
    ediffg = relaxation.ediffg

    plt.main()  # clear_figure() only clears the active subplot
    plt.clear_figure()
    plt.subplots(3, 1)
    plt.limitsize(False, False)
    plt.plotsize(width or shutil.get_terminal_size().columns, height)
    plt.theme("pro" if color else "clear")

    plt.subplot(1, 1)
    plt.plot(
        steps,
        (energies - energies[-1]).tolist(),
        marker="braille",
        label="E - E_final",
    )
    plt.title(f"E - E_final (eV)    E_final = {energies[-1]:.6f} eV")

    plt.subplot(2, 1)
    title = "|dE| (eV, log)"
    if changes.size:
        series = [changes]
        plt.plot(steps[1:], _log10(changes), marker="braille", label="|dE|")
        if ediffg is not None and ediffg > 0:
            series.append(np.array([ediffg]))
            _threshold(steps[1:], ediffg, label=f"EDIFFG = {ediffg:g} eV")
        _log_ticks(np.concatenate(series))
    plt.title(title)

    plt.subplot(3, 1)
    fmax = relaxation.max_forces(mask)
    series = [fmax]
    plt.plot(steps, _log10(fmax), marker="braille", label="Maximum force")
    title = "Force (eV/A, log)"
    if ediffg is not None and ediffg < 0:
        series.append(np.array([-ediffg]))
        _threshold(steps, -ediffg, label=f"|EDIFFG| = {-ediffg:g} eV/A")
    _log_ticks(np.concatenate(series))
    plt.title(title)
    plt.xlabel("Ionic step")

    text: str = plt.build()
    return text if color else str(plt.uncolorize(text))


def _log10(values: npt.NDArray[np.float64]) -> list[float]:
    """Return log10 of values, flooring zeros so they stay plottable."""
    logs: list[float] = np.log10(np.maximum(values, _FLOOR)).tolist()
    return logs


def _threshold(steps: list[int], value: float, label: str) -> None:
    """Draw a horizontal threshold line on the current log panel."""
    plt.plot(
        steps,
        [math.log10(value)] * len(steps),
        color="red",
        marker="-",
        label=label,
    )


def _log_ticks(values: npt.NDArray[np.float64]) -> None:
    """Label the current panel's y axis with powers of ten spanning values."""
    logs = np.log10(np.maximum(values, _FLOOR))
    low, high = math.floor(logs.min()), math.ceil(logs.max())
    exponents = list(range(low, max(high, low + 1) + 1))
    plt.yticks(exponents, [f"1e{k}" for k in exponents])
