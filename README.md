# template-python

A compact starting point for a modern, typed Python package. It uses
setuptools and `pyproject.toml` packaging, Ruff, mypy, pytest with full branch
coverage, pre-commit, and GitHub Actions.

The example package exposes a tiny NumPy API and a command-line entry point so
the template works end to end before you replace the sample code.

## Requirements

- Python 3.14 or newer
- pip 25.1 or newer (for dependency groups)

## Quick start

Create an isolated environment and install the package with its development
tools:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --group dev -e .
```

On Windows PowerShell, activate the environment with
`.venv\Scripts\Activate.ps1` instead.

Run the example:

```bash
template-python Ada
python -m template_python Ada
```

Or use the library:

```python
from template_python import line, print_hello

print_hello("Ada")
samples = line(-1.0, 1.0, num=5)
print(samples)
```

## Development

Run the complete local checks:

```bash
ruff check .
ruff format --check .
mypy
pytest
python -m build
python -m twine check dist/*
```

Ruff can apply safe lint and formatting changes with:

```bash
ruff check --fix .
ruff format .
```

Install the Git hooks once, then pre-commit will run the fast checks before
each commit:

```bash
pre-commit install
pre-commit run --all-files
```

If you prefer Conda, `build_tools/environment.yml` creates the base environment:

```bash
conda env create -f build_tools/environment.yml
conda activate template-python
python -m pip install --group dev -e .
```

## Project layout

```text
.
├── .github/workflows/ci.yml   # automated quality and packaging checks
├── build_tools/               # optional Conda setup
├── template_python/           # installable package
├── tests/                     # behavior-focused tests
└── pyproject.toml              # project metadata and tool configuration
```

## Use this template

After creating a repository from this template:

1. Rename the `template-python` distribution, `template_python` import package,
   and console command.
2. Update the description, author, repository URLs, and license metadata.
3. Choose and test the Python versions your project supports.
4. Replace the example API and tests while keeping the quality gates green.
5. Set a real release version and configure trusted publishing only when the
   package is ready to publish.

## License

Released under the [MIT License](LICENSE).
