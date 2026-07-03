---
description: Scaffold a paired experiment (run_NN_*.py + exp_NN_*.md) deterministically
argument-hint: NN slug ["Human Title"]
allowed-tools: Bash(python scripts/new_experiment.py:*)
---

Scaffold a new study by running the portable scaffolder — do not create the files by
hand, so the code/write-up pairing and naming stay consistent.

Run:

```
python scripts/new_experiment.py $ARGUMENTS
```

This copies `experiments/template_experiment.py` -> `experiments/run_NN_slug.py` and
`docs/experiments/_experiment_template.md` -> `docs/experiments/exp_NN_slug.md`
(same NN pairs them), filling in the number, slug, and title. It refuses to
overwrite existing files.

After it succeeds, report the two created paths and the printed next steps. Do not
start editing the experiment unless the user asks.
