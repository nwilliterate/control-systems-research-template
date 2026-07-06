# AGENTS.md - AI agent entrypoint

This is the first file every AI coding agent (Claude Code, Codex, Cursor,
Copilot, Gemini, etc.) and human collaborator reads before working in this
control-systems research repository. Detailed guidance lives under
`docs/agents/`.

## Required reading

- The single source of coding and research-code rules is
  `docs/agents/coding_rules.md`.
- For every coding task, read and follow `docs/agents/coding_rules.md` first.
- For persona and communication style, also read
  `docs/agents/personality.md`.
- `docs/agents/design.md` is the global project design guide.
- `docs/agents/progress.md` is the running work log. After completing any
  coding task or substantial research-documentation task, update it with:
  - what was done,
  - current status/result, including verification that did or did not run,
  - next planned goals or remaining follow-up work.

## Precedence

- If any style or process conflict occurs, `docs/agents/coding_rules.md` takes
  precedence inside this repository.
- Then use `docs/agents/design.md` for architectural direction.
- Then use `docs/agents/personality.md` for communication and collaboration
  style.
- Do not add or assume new style rules unless the user explicitly requests
  them.

## Operating rules

- Do not start implementation or directly modify files unless the user has
  explicitly asked for a change.
- Keep reusable logic in `lib/`; scripts such as `main.py` and
  `experiments/*` should only orchestrate.
- Preserve the project philosophy: MATLAB/Spyder-style Python, clear physical
  units and array shapes, and physical correctness over cleverness.
- If you identify a better approach than the one proposed by the user,
  recommend it clearly: explain the key difference, the trade-offs, and why the
  recommended option is preferable.

`CLAUDE.md` is only a pointer to this file and the `docs/agents/` documents.
