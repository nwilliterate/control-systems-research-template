# docs/experiments/ — Experiment Log

**One markdown per experiment**, paired with the experiment code
`experiments/run_NN_*.py` by the same number `NN`.

## Rules
- New experiment: copy `_experiment_template.md` → `exp_NN_description.md`.
- Code ↔ doc pairing: `run_NN_*.py` ↔ `exp_NN_*.md` (matching numbers).
- Save result figures/data to `results/figures/run_NN/` and `results/data/run_NN/`,
  then link them from the write-up with relative paths.
- When done, add a one-line summary to the top of `../research_notes.md`.

## Index
| No. | Title | Code | Status |
|---|---|---|---|
| 01 | Double-pendulum free response | `experiments/run_01_free_simulation.py` | example |
| 02 | _(next experiment)_ | | |
