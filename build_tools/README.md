# Conda environment

From the repository root, create and activate the optional Conda environment:

```bash
conda env create -f build_tools/environment.yml
conda activate relaxation-converge
python -m pip install --group dev -e .
```

The project metadata and development dependencies remain centralized in the
root `pyproject.toml`.
