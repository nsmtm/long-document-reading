# Conversion and preparation (from the pilot to the final reading copy)

Read this before converting, once SKILL.md's "Convert a pilot first" has settled that conversion is needed. Moved out of SKILL.md; the rules are unchanged. Converter entry points: [the converter reference](converters.md). Per-style correspondence tools: [the correspondence reference](correspondence.md). Masking steps: [the masking reference](masking.md).

- **Convert inside the reading agent** when no masking is required. Outside routes exist for the masking exception and for handovers, not for ordinary conversion.
- **Pilot first:** one chapter or up to five pages. Check heading structure, reading order, tables and elapsed time before converting the whole document.
  - Give the pilot a time budget of three minutes by default, measured from the converter launch. Stop a pilot that overruns it, switch tools instead of waiting, and record the budget used.
  - Measure the reading cost from the pilot as tokens per page multiplied by the page count. Treat the effective context window as well below the advertised one.
- **Choose the converter by the inventory:**
  - a structure-preserving converter such as Docling when headings and tables matter;
  - a fast layout-aware converter such as PyMuPDF4LLM for born-digital text;
  - an OCR-capable converter such as Marker or MinerU when scans are mixed in;
  - a plain text extraction such as `pdftotext -layout` when only the sequence of lines matters. MarkItDown on PDFs belongs to this lightweight class, not the structure-preserving one.

  Verify the chosen converter is available and check its help output before running it. Entry points and their verification status: [the converter reference](converters.md).
- **Multi-column documents.**
  - Never use `-layout` on one: it joins the columns line by line. There the default extraction reads the columns in sequence.
  - Never take an extractor's raw block or content-stream order as the reading order: a PDF carries positioned glyphs, not a reading sequence. pdftotext's own block analysis reads the columns in the right sequence (the left column to its end, then the right), and may still merge an isolated line across the gutter.
  - When a copy's order is broken beyond such isolated merges, escalate to a layout-aware converter such as Docling, at the cost of a heavy install and minutes of processing per article. Obtain it as an external tool the user fetches, not as something bundled with this skill.
- **Page anchors.** Require the reading copy to keep a page anchor for every page, such as a page heading line in the form `# Page N` (one or two leading `#`, the word `Page`, and the page number: the form the gate check reads), so citations and coverage checks can point back to the source.
  - When a delivered copy lacks them but keeps its printed folio numbers, restore them deterministically with qa/restore_page_anchors.py, which splits at the folio lines. Rely on the result only after the script's check that the folio sequence is complete and in order passes.
- **The form of the copy.**
  - Treat page-anchored plain text as a full reading copy. Structured Markdown is optional: add it only when heading fidelity matters and a deterministic converter produces it, because every gate in this skill needs page anchors and searchability, not markup.
  - Accept a Markdown file as the delivered copy when another agent produces it, as on the masking route: the token cost is a wash, and a file the user can open and hand on lowers the human cost. Require its body text to stay unformatted and unreflowed under the page-anchor headings, so drift stays visible and countable.
  - Record which converter produced the reading copy, the command used, and what it dropped, such as tables flattened or figure text lost.
- **Prepare the finished copy for the correspondence check** before its identity is recorded in the split plan. Preparation rewrites the copy, and a later rewrite invalidates the recorded identity and the notes' line ranges.
  1. Detect the citation style.
  2. Mark each unit that owns a list with a `# Chapter` / `# Part` / `# Section` line.
  3. Indent flush-left numbered lists with qa/prepare_numbered_lists.py.
  4. For superscript citations, rebuild the copy with qa/extract_superscript_citations.py, followed by the same indenting step.

  The unit markers placed here precede the structure map, so treat them as provisional. When the map settles a different unit boundary, re-mark the units, re-record the identity, and regenerate the worksheet before any judging starts.
- **Generate the correspondence worksheet** from the prepared copy with the generator for the detected style, kept in this skill's qa material (correspondence_worksheet.py for numbered lists, with companions for author-year, notes, and MLA). Place it in the work folder before any judging starts. Per-style details and example invocations: [the correspondence reference](correspondence.md).
- **Record the copy's identity only when the copy is final,** after every step that rewrites it: preparation for the correspondence check and, when the decision was to mask, masking, its verification, and any repair. A rewrite after the recording invalidates the recorded identity and the notes' line ranges.
  - Generate the correspondence worksheet, and every other artifact that will travel with a masked copy, from that final copy only. Regenerate from the final copy anything generated earlier, and delete the earlier version as an unmasked derivative.
  - This invariant, not a fixed step order, is the rule. On routes where a masked copy arrives before preparation (the Copilot route, the restricted path), preparation rewrites a verified copy: run the masking verification once more after preparation, before recording the identity.
  - On the local-masking path the invariant takes this shape: prepare, apply masking, verify and repair, record the identity, then generate the worksheet.
