# QA trial: the correspondence gate, first field test

Date: 2026-11-11
Reader: Codex CLI 0.167.0 (standalone build), run non-interactively in the
hosting VM, fetching this skill fresh from the skills reception.
Brief: identical in shape to the earlier trials — read the whole document,
verify per-chapter reference counts and the correspondence between in-text
citations and list entries. The declared scope named citation correspondence,
so the completion gate required the correspondence worksheet.
Document: a small synthetic report (8 pages, two lists of 12 and 5), carrying
the two counting traps of the 2026-11-10 trial plus a planted correspondence
trap: the body cites (5) and (12) correctly, but a theory paragraph after the
first list describes the follow-up-survey paper (entry 11) while citing (12).

## Outcome

Passed, in about three minutes.

- Counts exact: 12 and 5, total 17, taken from the reader's own counting
  script. Both counting traps handled and named in the completion report
  (a numbered heading before the list not counted; a digit-led wrapped line
  not counted as an entry).
- The worksheet was among the deliverables. The reader ran the generator
  kept in this skill's qa material and, the citation occurrences being few,
  listed all three with a verdict and a one-line reason each.
- The planted offset was caught without any external pointer: the theory
  paragraph's (12) was judged a mismatch against entry 12 ("Long term
  outcomes") because the passage describes follow-up-survey methods, with
  entry 11 ("Follow up survey") named as the closer title. The reader
  declined to assert the intended number from the text alone, which the
  evaluator accepted — detection and the candidate referent are what the
  gate exists to produce.
- The two correct citations were not falsely flagged.

## What this establishes

The gate form of the correspondence check — a generated worksheet as a
required deliverable, with a recorded verdict per sampled pair — catches
the one-off citation that five earlier trials of the main test document
missed on every first pass when the check rested on reading and intention.
The enumeration belongs to a tool; the judgement, exercised on the sheet,
belongs to the reader.
