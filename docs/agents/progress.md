# Progress

Newest entries go first. Each completed coding task or substantial
research-documentation task should record what changed, the current result, and
the next planned goal.

## 2026-07-05

- What was done: Added the `docs/agents` structure adapted from the
  `pa_control` workflow for this control-systems research template. Moved the
  detailed repository rules into `docs/agents/coding_rules.md`, added
  project-specific `design.md`, `personality.md`, and this progress log, and
  converted root `AGENTS.md` into the agent entrypoint/router.
- Current status/result: The agent instruction surface is now split by concern
  while preserving the existing MATLAB/Spyder-style Python, physical
  correctness, experiment pairing, knowledge-store, and verification rules.
  Verification passed with `uv run python scripts/verify.py`: 41 pytest tests
  passed, the Pinocchio import guard passed, and ruff was skipped because it is
  not installed.
- Next planned goals: Keep `docs/agents/progress.md` updated after future
  coding or substantial research-documentation slices, and update
  `docs/agents/design.md` whenever project architecture or workflow boundaries
  change.
