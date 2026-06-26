# docs/paper/ — Manuscript / Report

Once results accumulate, draft the paper or report here.

## Contents
- `paper.tex` — **IEEEtran LaTeX template** (ICRA/IROS/RA-L/T-RO style).
- `build.ps1` / `build.sh` — build scripts (latexmk preferred, pdflatex+bibtex fallback).
- `figures/` — paper-specific figures (experiment figures come from `results/figures/`).
- `outline.md` — paper outline (per-section key message + supporting experiments).
- Citations: `../../references/references.bib` (the repo-wide BibTeX file).

## Build (LaTeX → PDF)
Requires MiKTeX or TeX Live. Pick any one:
```powershell
# Windows PowerShell
cd docs/paper; ./build.ps1            # build -> paper.pdf
./build.ps1 clean                     # remove aux files
```
```bash
# bash (Git-Bash / macOS / Linux)
cd docs/paper && ./build.sh
./build.sh clean
```
```bash
# From the project root via the Makefile
make paper
make paper-clean
```
> Build artifacts (`*.aux`, `*.pdf`, ...) are git-ignored; commit only
> `paper.tex` / `references.bib`.
> Venue format: switch `conference` ↔ `journal` in the first line of `paper.tex`
> (`\documentclass[conference]{IEEEtran}`); T-RO/TASE use `journal`.
> To insert an experiment figure, run the experiment code, then uncomment the
> `\includegraphics` block in `paper.tex`.

## ARS integration (optional)
With the academic-research-skills plugin:
- `/ars-outline` — detailed outline + evidence mapping
- `/ars-full` — full research → write → review → revise pipeline
- `/ars-abstract` — bilingual abstract + keywords
- `/ars-format-convert` — convert to LaTeX / DOCX / PDF / Markdown
- `/ars-reviewer` — simulated peer review
