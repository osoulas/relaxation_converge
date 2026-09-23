# relaxation-converge

`relaxation-converge` reads a VASP `OUTCAR` from an ionic relaxation and
summarizes how the energy and forces change at each step. It reports whether
the final step meets the `EDIFFG` criterion when that setting is present, and
plots the convergence in your terminal. You can also save a publication-ready
PNG plot.

## Install

Requires Python 3.14 or newer.

```bash
python -m pip install relaxation-converge
```

To install from a local checkout with development tools, create and activate a
virtual environment, then run:

```bash
python -m pip install --upgrade pip
python -m pip install --group dev -e .
```

## Use the command line

Run the command in a directory containing `OUTCAR`:

```bash
relaxation-converge
```

Or provide the path explicitly:

```bash
relaxation-converge path/to/OUTCAR
```

The command prints a per-step table with energy, energy change, and maximum
atomic force, followed by the convergence status and a three-panel terminal
plot. To save the plot as `convergence.png` as well, use `--save`:

```bash
relaxation-converge OUTCAR --save
```

Choose another output path with `--save FILE`. Useful options:

| Option | Purpose |
| --- | --- |
| `-p`, `--poscar FILE` | Read `POSCAR` or `CONTCAR` selective-dynamics flags and ignore fixed Cartesian components when calculating forces. |
| `-s`, `--save [FILE]` | Save a PNG plot; defaults to `convergence.png` when no file is given. |
| `--height LINES` | Set the terminal plot height (default: 60). |
| `--no-color` | Print a plain-text plot, useful when piping output. |

For example, analyze a calculation with constrained atoms and save the figure:

```bash
relaxation-converge run/OUTCAR --poscar run/CONTCAR --save run/convergence.png
```

The plot shows energy relative to the final step, absolute energy change, and
maximum atomic force. If `EDIFFG` is set, its energy or force threshold
appears on the corresponding panel. A positive `EDIFFG` is treated as an
energy-change criterion; a negative value is treated as a force criterion. If
`EDIFFG` is absent, convergence is reported as unknown.

## Use as a Python library

```python
from relaxation_converge import (
    plot_convergence,
    read_outcar,
    read_selective_dynamics,
)

relaxation = read_outcar("OUTCAR")
mask = read_selective_dynamics("CONTCAR")

print(f"Ionic steps: {relaxation.nsteps}")
print(f"Converged: {relaxation.is_converged(mask)}")
print(f"Final maximum force: {relaxation.max_forces(mask)[-1]:.4f} eV/Å")

figure = plot_convergence(relaxation, mask, title="VASP relaxation")
figure.savefig("convergence.png", dpi=150)
```

`read_outcar` returns a `Relaxation` object containing the per-step free
energies, sigma-to-zero energies, and Cartesian forces. It also reads `EDIFF`
and `EDIFFG` when present. Incomplete final ionic steps are omitted so each
returned step has both energy and force data.

## Development

Install the development dependencies from the repository root:

```bash
python -m pip install --group dev -e .
```

Run checks with:

```bash
ruff check .
ruff format --check .
mypy
pytest
```

To build and check a release distribution:

```bash
python -m build
python -m twine check dist/*
```

An optional Conda environment is defined in [`build_tools/environment.yml`](build_tools/environment.yml).

## License and credits

Released under the [MIT License](LICENSE).

Made by Oskar, George, and Jacob.
