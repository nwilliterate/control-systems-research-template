---
description: Scaffold a source-grounded knowledge atom (knowledge/claims/<id>.md) deterministically
argument-hint: id ["Claim text"] --cite key --page N   (or --inferred --from a,b)
allowed-tools: Bash(python scripts/new_claim.py:*)
---

Capture a durable, source-grounded fact as a knowledge atom — do not hand-write the
front matter, so the provenance fields (cite/page/type) stay consistent and checkable.

Run:

```
python scripts/new_claim.py $ARGUMENTS
```

This writes `knowledge/claims/<id>.md` from the template with the required provenance
fields filled. For an **extracted** claim it leaves a `«PASTE VERBATIM QUOTE HERE»`
sentinel that `scripts/verify_knowledge.py` rejects — so the atom stays red until the
exact source text is pasted in. It refuses to overwrite an existing claim.

After it succeeds:
1. If extracted, open the file and replace the sentinel with the **verbatim** quote from
   the cited page (`--cite` must be a key in `references/references.bib`).
2. Run `python scripts/verify_knowledge.py` and report the result. Do not claim the fact
   is stored until the verifier passes.
