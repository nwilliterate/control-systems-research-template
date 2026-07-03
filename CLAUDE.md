# CLAUDE.md

This project keeps a **single source of truth** for AI collaboration rules in
**[`AGENTS.md`](./AGENTS.md)** — a vendor-neutral file that any AI tool (Claude Code,
Codex, Cursor, Copilot, Gemini, …) or human can read.

**Read [`AGENTS.md`](./AGENTS.md) now and follow it.** It covers the project overview,
directory map, coding style & naming, the hard rules, the research workflow, adding a
new plant, the verification harness, build/test commands, and the definition of done.

Claude Code specifics (the `control-verifier` subagent, the verification/scaffolding
hooks, the permissions allowlist, and the `/new-experiment` command) live under
`.claude/` and are summarized in the **"Agent harness"** section of `AGENTS.md`.
