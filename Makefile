# Experiment entrypoints (MATLAB-script convenience targets).
# NOTE: these targets assume a Unix-like shell (Git-Bash, WSL, macOS, Linux):
# they use rm/touch and call ./build.sh. On native Windows without `make`, run the
# commands directly — e.g. `python main.py`, `pytest -q`, `cd docs/paper; ./build.ps1`.
.PHONY: help sync lock test demo run01 paper paper-clean clean

help:
	@echo "make sync        - install deps into .venv with uv (add --extra dynamics for Pinocchio)"
	@echo "make lock        - refresh uv.lock"
	@echo "make test        - run unit tests (pytest)"
	@echo "make demo        - run main.py end-to-end demo"
	@echo "make run01       - run experiments/run_01_free_simulation.py"
	@echo "make paper       - build docs/paper/paper.pdf (LaTeX)"
	@echo "make paper-clean - remove LaTeX build artifacts"
	@echo "make clean       - remove caches and generated results"

sync:
	uv sync

lock:
	uv lock

paper:
	cd docs/paper && ./build.sh

paper-clean:
	cd docs/paper && ./build.sh clean

test:
	pytest -q

demo:
	python main.py

run01:
	python -m experiments.run_01_free_simulation

clean:
	rm -rf __pycache__ .pytest_cache **/__pycache__
	rm -rf results/figures/* results/data/*
	@touch results/figures/.gitkeep results/data/.gitkeep
