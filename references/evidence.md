# Evidence base for long_document_reading

The dated trial narratives behind the body's rules, moved out of SKILL.md on 2026-11-18 (review run 20261118-12, proposal R-P02, decided by the user the same day). The body keeps each rule, a short reason, and a pointer to the section here; the narratives themselves are kept, not deleted, so a later revision can still trace why a rule stands. Short single-clause field notes ("as a 2026-11-07 field test showed") stay in the body as the short reasons they are; this file carries the multi-sentence narratives.

## §1 Correspondence is in scope by default (Interview)

A 2026-11-11 trial's split plan declared correspondence out of scope as unrequested, and the one off citation in the test document stayed undetected for the sixth consecutive trial. Hence the body's rule: correspondence leaves the scope only when the requester explicitly excludes it, never by a reader's inference from silence.

## §2 Judge pairs by content, on the worksheet (Structure map)

- A 2026-11-10 trial recorded both sides correctly — the citing passages and the list entries — yet still missed the numbering offset, because the two records were never compared. Hence: judge each pair by content, on the sheet that places them side by side.
- A 2026-11-12 trial spent hours on improvised re-verification scripts while the sheet already held everything the judgment needed. Hence: no new extraction or recounting scripts for the judgment; when the sheet's material cannot settle a pair, record that insufficiency as the ground for the pair.
- A 2026-11-13 trial showed two of twenty-one pairs were cross-chapter pairings — a sampled passage from the following chapter's body, which sits before that chapter's own list — exposed by chapter attribution, not by the number. Hence: confirm the citing passage's chapter before judging the pair.

## §3 Harness limit resolution and the Goose trigger (Survive the harness)

A harness resolves its effective limit from its own overrides first, then from runtime discovery against the serving endpoint, then from model metadata, then from a default; the display can show the default while the endpoint's smaller served window governs the trigger. In a 2026-11-09 trial with Goose defaults (trigger = the smaller of four fifths of the effective limit and an absolute cap of 225,000 tokens), a served window of 65,536 fired compaction near 52,000 tokens even when the display read 128,000. The follow-up investigation (2026-11-10) is recorded in references/sources.md.

## §4 The worksheet as a gate deliverable (Completion gate)

Across six trials of this skill's test document, the one off citation was missed on every first pass — once under a plan that had scoped the check out as unrequested — and surfaced only when the citing passages and the list entries were placed side by side on a generated sheet. Hence the gate requires the generated worksheet among the deliverables, with a verdict and a one-line reason on every sampled pair, and requires the completion report to state the evidence base (distinct documents and lists), because repeated trials of one test document are a single evidence base, not several independent ones.
