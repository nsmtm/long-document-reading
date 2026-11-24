# Trial run 2026-11-18 (run 20261118-12, second pass)

Execution trial by a fresh agent with no context beyond the skill itself, on synthetic material in /tmp/ldr_trial (A: normal numbered read with a Japanese journal list; B: partial scope pp.2-3; C: undeclared custom list heading; D: the four R-P05 tools). The trial agent edited no skill files.

gate-hash: 8c96b95c71cefab324d474fadaa02bd23292208a38d9f039456db1449e9d9d71
gate-result: accepted

## Results

- A: gate passed end to end (generator exit 0, declared list count matched, coverage statement generated with no gaps or overlaps).
- B: gate passed against the declared scope; the coverage statement initially counted the out-of-scope page as a gap (see findings).
- C: undeclared heading produced a warning sheet (exit 2) and the gate failed it; after declaring the heading in the split plan, generator and gate both passed.
- D: folio restoration (including the gap-refusal case, exit 2), byte comparison (identical 0 / different 1), name candidates, and the coverage statement all ran as the body describes.

## Findings and dispositions (2026-11-18)

- Fixed: make_coverage_statement.py computed gaps over the whole anchor span, ignoring the declared scope. It now reads the scope line and computes gaps relative to the scope; re-verified on the trial's scenario B artifacts (gaps: none).
- Fixed: a heading outside the candidate vocabulary （出典） was not named as a candidate. list_detect.py now also names a non-heading line immediately followed by a numbered entry run as a candidate; re-verified on scenario C (the heading is named, with the dismissal route).
- Fixed: prepare_numbered_lists.py did not read the split plan's declared headings and exited 0 with no list found. It now accepts --plan and exits 2 when no numbered list is detected; re-verified on scenario C.
- Fixed (minor): extract_name_candidates.py role vocabulary lacked 責任者； added.
- Held: make_split_plan.py emits a placeholder template that needs hand completion before the gate passes. By design (the template is a starting record); the body's split-plan bullet describes the fields to record. Revisit if a future trial stalls on it.
- Declined: the worksheet passage window includes preceding lines (up to 3) and anchor/marker lines. That is the documented window design; the trial judged pairs successfully with it.
- Held: the qa tools have no --help; their docstrings are the usage record. Noted for a future wording pass.
- Name-candidate noise (role words and contact-block tokens appearing as candidates) is by design: the script enumerates candidates and the user rules on each.
