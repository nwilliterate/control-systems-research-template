---
# One claim per file. The filename (minus .md) MUST equal `id`.
# Files starting with "_" (like this template) are ignored by the verifier.
id: _template
# extracted = copied/quoted from a source; inferred = reasoned from sources.
type: extracted            # extracted | inferred
status: active             # active | superseded
cite: featherstone2008rigid   # BibTeX key in references/references.bib (extracted: required)
page: 12                   # source page (extracted: required)
sha256:                    # first 12+ hex of the source PDF's sha256 (recommended)
confidence: high           # high | medium | low
derived_from: []           # inferred: non-empty list of claim ids or bib keys it rests on
supersedes:                # id of the claim this replaces (blank if none)
superseded_by:             # set on the OLD claim when a newer one replaces it
contradicts: []            # ids of claims that disagree with this one
updated: 2026-07-04        # YYYY-MM-DD
---

**Claim:** <one crisp, checkable statement>

> «PASTE VERBATIM QUOTE HERE»

<!-- ^ extracted claims: replace the sentinel with the EXACT source text (required).
     The verifier rejects the sentinel, so this atom stays red until you paste it. -->

**Applies to:** `lib/...`   <!-- where in this repo the fact bites (optional) -->

**Notes:** <derivation for inferred claims; caveats; assumptions>
