# Trial run — publication execution trial (2026-11-24)

- Form: execution trial. Agent: Codex CLI (VM), fresh session, workspace-write sandbox in a scratch folder, given only the skill folder and a synthetic document; the user's interview answers were supplied in the brief.
- Revision under trial: the publication form of the skill — distilled body (clh-20261124-02), the opening generalized [Q3, 2026-11-24], LICENSE (MIT, Copyright (c) 2026 nsmtm), README.md and .gitignore added, the generalization edits (c) #1–#4 applied, qa/__pycache__ removed.
- Material: a synthetic 5-page Markdown requirements document with known ground truth — Chapter 1: 10 items, Chapter 2: 8 item occurrences (REQ-B5 duplicated with different wording, REQ-B7 missing), Chapter 3: 6 items; total 24 occurrences, 23 distinct IDs; one trap (a continuation line beginning "2024.").

gate-hash: 62a3f1d3574ff732821ccd2b23b12c7cfa119be08d764e3d5b21d181912d62b1
- Hash note: the trial ran at folder hash 1ba6140a…; the only change after the run is the sources.md entry recording this publication (references/sources.md, "GitHub publication (2026-11-24)"), which is what the bound hash above covers.
gate-result: accepted

## Results

- Counts reconciled exactly: 10 / 8 / 6, total 24 occurrences (23 distinct IDs). Both anomalies found and reported exactly (duplicate REQ-B5 with differing wording; missing REQ-B7); the "2024." continuation line was not counted.
- The completion gate passed (all five page anchors confirmed; notes for all three units; the shared page-4 chapter boundary resolved by line ranges). Work products: rulings, structure map, split plan, reading notes, coverage statement, completion report.
- Rule-by-rule account: phases applied or skipped as not applicable with reasons (conversion and pilot on a Markdown source; correspondence on a document with no citation apparatus). Two "could not follow literally" points, both properties of the trial setting, not of the text: the masking evidence scan names a PDF route (an equivalent scan was run on the Markdown), and there was no owning-project record in the sandbox to register artifacts with.

- Findings requiring a fix: none.
