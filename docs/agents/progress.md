# Progress

Newest entries go first. Each completed coding task or substantial
research-documentation task should record what changed, the current result, and
the next planned goal.

## 2026-07-06

- What was done: Ran an integration review of the new `docs/agents/` structure
  against `main` and applied the resulting fixes. Repointed the
  `control-verifier` subagent to `docs/agents/coding_rules.md` for the DoD
  (the router `AGENTS.md` no longer holds it), replaced the duplicated
  directory map in `coding_rules.md` with a pointer to the single owner in
  `README.md`, and dropped ported `pa_control` C++ ceremony (the `m_`/`p_`
  prefix prohibition and the `default` design-guide sentinel).
- Current status/result: The split now preserves every existing project policy
  with no duplicated directory map and no dangling harness pointer. Changes are
  documentation-only; no `lib/` or `scripts/` code was touched.
- Next planned goals: Confirm the branch merges cleanly, then decide whether the
  new progress-log duty and `personality.md` persona stay as permanent policy.

## 2026-07-05

- What was done: Added repository-specific naming rules for directories, files,
  variables, functions, classes, struct-like Python containers, constants,
  private helpers, tests, and control-systems notation exceptions.
- Current status/result: Naming guidance now follows this Python research
  repository's existing `snake_case` / `PascalCase` style and explicitly avoids
  importing `pa_control`'s C++-oriented `m_`, `p_`, and `camelCase` conventions.
- Next planned goals: Keep naming exceptions tied to standard control notation
  and documented units/shapes instead of broad abbreviation use.

- What was done: Added four additional coding-rule groups adapted from the
  `pa_control` rules: helper extraction, comments/docstrings, error handling
  and logging, and small-scope development.
- Current status/result: The imported rules were adjusted for this Python
  research-template structure, preserving the existing `lib/`, `experiments/`,
  units/shapes, and verification workflow instead of bringing over C++/RT or
  apps/modules-specific rules.
- Next planned goals: Keep future coding-rule imports selective so they do not
  conflict with the repository's existing control-systems template conventions.

- What was done: Added repository-specific commit message rules to
  `docs/agents/coding_rules.md` based on the existing history's lightweight
  Conventional Commit pattern (`docs:`, `fix:`, `feat:`, `chore:`, `build:`).
- Current status/result: Commit guidance now matches this repository's observed
  style instead of importing the separate `.gitmessage` / `[header]` / `[desc]`
  workflow from `pa_control`.
- Next planned goals: Use the documented commit message pattern for future
  commits unless the repository adopts a stricter template later.

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
