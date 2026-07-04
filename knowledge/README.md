# knowledge/ — Source-grounded knowledge store

A **machine-checkable** knowledge layer for this repo. It is the counterpart to
`docs/literature/` (human prose reading notes): here every fact is a small, atomic,
**source-grounded** file that an agent or human can query, verify, and update — and
that CI rejects if it cannot be traced back to a real source.

> Why this exists: AI makes mistakes. A durable knowledge base must be anchored to
> books and journals, not to a model's memory. So no atom is accepted without a
> citation into `references/references.bib` and (for quotes) the verbatim source text.

## The rule: one claim per file, always traceable

Each `claims/<id>.md` holds exactly **one claim** with YAML front matter. Copy
`claims/_template.md`, or scaffold it deterministically:

```bash
python scripts/new_claim.py lqr-riccati --cite anderson1990optimal --page 47
#   -> knowledge/claims/lqr-riccati.md   (fails CI until you paste the real quote)
```

Then verify:

```bash
python scripts/verify_knowledge.py      # or: make verify-knowledge
```

### Front-matter fields

| field           | required            | meaning                                                     |
|-----------------|---------------------|-------------------------------------------------------------|
| `id`            | always              | slug; **must equal the filename** (minus `.md`)             |
| `type`          | always              | `extracted` (quoted from a source) or `inferred` (reasoned) |
| `status`        | always              | `active` or `superseded`                                    |
| `cite`          | `extracted`         | BibTeX key that **must exist** in `references/references.bib`|
| `page`          | `extracted`         | source page number                                          |
| `sha256`        | recommended         | first 12+ hex of the source PDF's hash (staleness guard)    |
| `confidence`    | recommended         | `high` / `medium` / `low`                                   |
| `derived_from`  | `inferred`          | non-empty list of claim ids or bib keys it rests on         |
| `supersedes`    | on updates          | id of the claim this replaces                               |
| `superseded_by` | on retired claims   | set on the OLD claim when a newer one replaces it           |
| `contradicts`   | optional            | ids of claims that disagree                                 |
| `updated`       | always              | `YYYY-MM-DD`                                                 |

`extracted` claims **must** carry a verbatim quote (a `>` blockquote). The verifier
rejects the scaffold's `«PASTE VERBATIM QUOTE HERE»` sentinel, so a freshly generated
atom stays red until a human/agent pastes the exact source text — that is the point.

### Illustrative atom (not a committed claim — see `claims/_template.md` for the real skeleton)

```markdown
---
id: lqr-riccati
type: extracted
status: active
cite: anderson1990optimal
page: 47
sha256: a3f9c1d0b21e
confidence: high
updated: 2026-07-04
---

**Claim:** LQR gives the optimal control for a quadratic cost via the algebraic Riccati equation.

> "the optimal control minimizing the quadratic cost is u = -Kx, where K = R^{-1} B^T P
> and P solves the algebraic Riccati equation..."

**Applies to:** `lib/controllers/lqr.py`
```

## Updating knowledge (don't overwrite — supersede)

Books get revised; journals get rebutted. To change a fact, **add a new atom and
retire the old one** so the history and any disagreement survive:

1. Scaffold the new atom; set `supersedes: <old-id>`.
2. On the old atom set `status: superseded` and `superseded_by: <new-id>`.
3. If two sources genuinely disagree, keep both `active` and link them with
   `contradicts:` — the store records the debate instead of hiding it.

The verifier enforces that these links are reciprocal and point at real files.

## Connecting PDFs

- Register the source once in `references/references.bib` (BibTeX key = `cite`).
- Keep the PDF under `references/pdfs/` and record it in `references/pdfs/manifest.yaml`
  (`cite`, `sha256`, `source_url`). The PDFs themselves are git-ignored (large / often
  copyrighted); the manifest + hash are committed so anyone can confirm they hold the
  same edition. Put the atom's `sha256` = the manifest hash and CI can flag a claim as
  stale if the source ever changes.
- `page` + the verbatim `quote` let a human open the PDF and confirm the fact in seconds.

## Relationship to the rest of the repo

- `references/references.bib` — the **WHAT** (bibliographic identity). No duplication:
  atoms reference a key, they don't restate author/title/year.
- `docs/literature/note_*.md` — human prose per paper. Free-form, for reading/thinking.
- `knowledge/claims/*.md` — the **atomic, verifiable facts** agents read and write.

With the `academic-research-skills` plugin, `/ars-citation-check` cross-checks the bib,
and `/ars-mark-read` records that a human actually read a source (vs. an AI merely citing it).
