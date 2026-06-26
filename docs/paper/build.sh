#!/usr/bin/env bash
# Build paper.pdf from paper.tex (bash / macOS / Linux / Git-Bash).
# Prefers latexmk; falls back to pdflatex + bibtex. Usage:
#   ./build.sh          build paper.pdf
#   ./build.sh clean    remove LaTeX aux files (and PDF)
set -euo pipefail
cd "$(dirname "$0")"
MAIN=paper

if [ "${1:-}" = "clean" ]; then
  if command -v latexmk >/dev/null 2>&1; then latexmk -C "$MAIN.tex" || true; fi
  rm -f "$MAIN".{aux,bbl,blg,log,out,fls,fdb_latexmk,pdf}
  echo "Cleaned build artifacts."
  exit 0
fi

if command -v latexmk >/dev/null 2>&1; then
  latexmk -pdf -bibtex -interaction=nonstopmode -halt-on-error "$MAIN.tex"
elif command -v pdflatex >/dev/null 2>&1; then
  pdflatex -interaction=nonstopmode -halt-on-error "$MAIN.tex"
  command -v bibtex >/dev/null 2>&1 && bibtex "$MAIN" || true
  pdflatex -interaction=nonstopmode -halt-on-error "$MAIN.tex"
  pdflatex -interaction=nonstopmode -halt-on-error "$MAIN.tex"
else
  echo "No LaTeX toolchain found (install MiKTeX or TeX Live)." >&2
  exit 1
fi
echo "Built $MAIN.pdf"
