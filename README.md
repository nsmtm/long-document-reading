# Reading Long Documents

Read a long document end to end — tens of pages or more than a single
read can hold — as a PDF, a Word file, or text or Markdown, and prove
the read is complete against the declared scope.

The skill inventories the document, interviews the reader for scope,
readers and masking, pilots the conversion to a page-anchored reading
copy, reads in structural units with notes, and closes with a
reconciled coverage statement and a mechanical completion gate.

## When to use it

Use it when completeness itself is the deliverable: counting and
reconciling items where an omission is an error, verifying an
extraction or a summary another agent produced, or checking that a
document agrees with itself as a whole (contract terms, required-item
coverage). Skip it when a question can be answered by search — search
returns what it finds and cannot prove a total or an absence.

## Prerequisites

- `poppler` tools: `pdfinfo`, `pdftotext`, `pdffonts`, `pdfimages`,
  `pdfdetach`.
- Python 3 for the scripts in `qa/`.
- Optional converters, obtained separately: Docling, Marker, MinerU,
  MarkItDown, PyMuPDF4LLM. See `references/converters.md` for entry
  points and verification status.

## Install

Copy this folder into your agent's skills directory (for example,
Claude Code: `.claude/skills/` or `~/.claude/skills/`), then load the
skill by name (`long_document_reading`) and follow `SKILL.md`.

## How a read runs

1. Inventory the document (`pdfinfo` first; sensitivity is declared
   by the user before any sampling).
2. Interview: decision or deliverable, scope (full read or named page
   ranges), who may read the original and who sees only a masked copy.
3. Decide masking on evidence; security-sensitive files take the
   restricted path and only permitted readers see the original.
4. Convert a pilot (one chapter or up to five pages) first, then the
   whole document, keeping a page anchor (`# Page N`) for every page.
5. Build the structure map, split into structural units, read unit by
   unit with notes written after each unit.
6. Pass the completion gate (`qa/check_gate.py`): coverage reconciled
   with no gap and no overlap, a notes entry for every unit, and
   citation correspondence judged on the worksheet where the
   correspondence ruling stands.

In the references and trial records, "Mochi" names the coordinating
agent in the house's own trials; "Copilot" names the default permitted
reader for the masking route — any reader the interview's rulings name
as permitted can fill that role. Per-read rulings live in the work
folder's `rulings.md`, never in this skill.

## Layout

- `SKILL.md` — the method.
- `skill.yaml` — name, description, category.
- `references/` — the phase references read at their step
  (`conversion.md`, `masking.md`), converter entries (`converters.md`),
  the masking bridge (`bridge.md`), citation correspondence
  (`correspondence.md`), trial evidence (`evidence.md`), sources and
  licences (`sources.md`).
- `qa/` — the bundled scripts (gate check, coverage statement, split
  plan, correspondence worksheet generators, masking verification)
  and the trial records behind the rules.

## Licence

MIT — see `LICENSE`. One bundled script,
`qa/extract_superscript_citations.py`, imports PyMuPDF (AGPL-3.0,
Artifex): the script itself is original code, the library is obtained
separately by the user and is not redistributed here, and running that
script means using the library under its AGPL-3.0 terms. A measured
MIT-licensed fallback (pdfplumber) is described in
`references/correspondence.md`; it is not bundled. Attribution for
borrowed methods (pdf-reading, deep-read, Presidio, converter survey)
is gathered in `references/sources.md`, section "Licences and
attribution".

## Status

Field-tested: a 116-page ground-truth document read end to end with
coverage 116 of 116 and reference counts matching exactly (186), plus
cross-agent trials (Codex, Antigravity, Goose with local models).
Details and the dated trial narratives are in `references/sources.md`
and `references/evidence.md`.
