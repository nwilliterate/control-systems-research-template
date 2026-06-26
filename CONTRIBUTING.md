# Contributing

Thanks for your interest. This repository is a **template** for control-systems
research; contributions that keep it small, readable, and reusable are welcome.

## Ground rules
- Follow the coding rules in [`CLAUDE.md`](./CLAUDE.md) / [`AGENTS.md`](./AGENTS.md):
  reusable logic in `lib/` (one job per file), concise `main.py`, all parameters in
  `config/params.yaml`, docstrings with units and array shapes.
- Keep the pure-numpy parts importable **without** Pinocchio (lazy imports).
- Add a test for any pure-numpy routine; Pinocchio-dependent tests must be
  import-guarded (`pytest.importorskip("pinocchio")`).

## Dev setup
```bash
uv sync                               # recommended: core + dev tools (pytest) into .venv
uv sync --extra dynamics              #   add Pinocchio on Linux/macOS
# or full Pinocchio env everywhere (required on Windows):
conda env create -f environment.yml
conda activate control-systems
# or pure-numpy parts only:
pip install -r requirements.txt
```

## Before opening a PR
```bash
uv run pytest -q   # must pass (Pinocchio tests skip if it isn't installed)
                   # with conda/pip: just `pytest -q`
```
- Keep diffs focused; one logical change per PR.
- Update the relevant docs (`README.md`, `docs/`) if behavior or structure changes.

## Reporting issues
Use the issue templates (bug report / feature request). Include the OS, Python
version, and whether Pinocchio is installed.
