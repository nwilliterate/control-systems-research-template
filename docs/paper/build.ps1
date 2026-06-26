# Build paper.pdf from paper.tex (Windows PowerShell).
# Prefers latexmk; falls back to pdflatex + bibtex. Usage:
#   ./build.ps1          build paper.pdf
#   ./build.ps1 clean    remove LaTeX aux files (and PDF)
#
# NOTE: we deliberately do NOT set $ErrorActionPreference='Stop'. latexmk and
# pdflatex write normal progress to stderr; under 'Stop' PowerShell would treat
# that as a terminating error and abort mid-build. We check $LASTEXITCODE instead.
Set-Location -Path $PSScriptRoot
$main = "paper"

function Have($name) { return [bool](Get-Command $name -ErrorAction SilentlyContinue) }
function Check($code, $msg) { if ($code -ne 0) { Write-Host "ERROR: $msg (exit $code)"; exit $code } }

if ($args -contains "clean") {
    if (Have latexmk) { latexmk -C "$main.tex" | Out-Null }
    Get-ChildItem -Path . -Include "$main.aux","$main.bbl","$main.blg","$main.log","$main.out","$main.fls","$main.fdb_latexmk","$main.pdf" -File -ErrorAction SilentlyContinue | Remove-Item -Force
    Write-Host "Cleaned build artifacts."
    exit 0
}

if (Have latexmk) {
    latexmk -pdf -bibtex -interaction=nonstopmode "$main.tex"
    Check $LASTEXITCODE "latexmk build failed"
} elseif (Have pdflatex) {
    pdflatex -interaction=nonstopmode "$main.tex";  Check $LASTEXITCODE "pdflatex pass 1 failed"
    if (Have bibtex) { bibtex $main }
    pdflatex -interaction=nonstopmode "$main.tex";  Check $LASTEXITCODE "pdflatex pass 2 failed"
    pdflatex -interaction=nonstopmode "$main.tex";  Check $LASTEXITCODE "pdflatex pass 3 failed"
} else {
    Write-Host "ERROR: No LaTeX toolchain found (install MiKTeX or TeX Live)."
    exit 1
}
Write-Host "Built $main.pdf"
