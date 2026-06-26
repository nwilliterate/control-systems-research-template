# docs/ — Research Documentation

A research-writing space kept **separate** from the code (`experiments/`, `lib/`).
Put research methodology, experiment write-ups, literature notes, and paper drafts
here.

> Principle: **code lives in `experiments/`, writing lives in `docs/`.** Each
> experiment script `run_NN` is paired with a write-up `docs/experiments/exp_NN_*.md`.

## Folder layout

| Folder | Purpose | Start file |
|---|---|---|
| `methodology/` | Research methodology — problem formulation, assumptions, modeling, controller design, metrics | `methodology_template.md` |
| `experiments/` | One write-up per experiment (hypothesis → setup → results → discussion) | `_experiment_template.md` |
| `literature/` | Paper reading notes, prior-work summaries | `reading_notes_template.md` |
| `paper/` | Manuscript/report drafts, outline, figure list | `outline.md` |
| `research_notes.md` | Dated running log (short memos) | — |
| `../references/` | Cited PDFs, `references.bib` | `references.bib` |

## Standard workflow (one new experiment)

1. **Fix the method** → if needed, record the design/assumptions in `methodology/`.
2. **Write the code** → copy `experiments/template_experiment.py` to
   `experiments/run_NN_description.py` (import only from `lib/`).
3. **Create the write-up** → copy `docs/experiments/_experiment_template.md` to
   `docs/experiments/exp_NN_description.md`; use the same number `NN` to pair it
   with the code.
4. **Run & record results** → figures go to `results/figures/run_NN/`, data to
   `results/data/run_NN/` (handled by `lib/utils`). Link them from the write-up.
5. **Discussion / next steps** → summarize in the write-up's Discussion; add a
   one-line note to the top of `research_notes.md`.
6. **Toward a paper** → once results accumulate, draft in `paper/`
   (the ARS skills `/ars-outline`, `/ars-full`, etc. can assist).

## Numbering convention (code ↔ doc pairing)

```
experiments/run_01_free_simulation.py   <->   docs/experiments/exp_01_free_simulation.md
experiments/run_02_lqr_balancing.py     <->   docs/experiments/exp_02_lqr_balancing.md
```

Using the same `NN` for code and write-up keeps a clean 1:1 trace.
