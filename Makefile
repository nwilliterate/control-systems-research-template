# Experiment entrypoints (MATLAB-script convenience targets).
# NOTE: these targets assume a Unix-like shell (Git-Bash, WSL, macOS, Linux):
# they use rm/touch and call ./build.sh. On native Windows without `make`, run the
# commands directly — e.g. `python main.py`, `pytest -q`, `cd docs/paper; ./build.ps1`.
.PHONY: help sync lock test verify demo run01 new-experiment paper paper-clean clean

help:
	@echo "make sync            - install deps into .venv with uv (add --extra dynamics for Pinocchio)"
	@echo "make lock            - refresh uv.lock"
	@echo "make test            - run unit tests (pytest)"
	@echo "make verify          - full verification gate (pytest + import-guard + advisory ruff)"
	@echo "make demo            - run main.py end-to-end demo"
	@echo "make run01           - run experiments/run_01_free_simulation.py"
	@echo "make new-experiment NN=02 SLUG=lqr_cartpole [TITLE=\"...\"] - scaffold paired study"
	@echo "make paper           - build docs/paper/paper.pdf (LaTeX)"
	@echo "make paper-clean     - remove LaTeX build artifacts"
	@echo "make clean           - remove caches and generated results"

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

# Portable verification gate — same script the Claude Stop hook runs.
verify:
	python scripts/verify.py

# Scaffold a paired experiment: make new-experiment NN=02 SLUG=lqr_cartpole TITLE="LQR cart-pole"
new-experiment:
	python scripts/new_experiment.py $(NN) $(SLUG) $(if $(TITLE),"$(TITLE)",)

demo:
	python main.py

run01:
	python -m experiments.run_01_free_simulation

clean:
	rm -rf __pycache__ .pytest_cache **/__pycache__
	rm -rf results/figures/* results/data/*
	@touch results/figures/.gitkeep results/data/.gitkeep
