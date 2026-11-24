# Correspondence reference for long_document_reading

The per-style detail of the citation-correspondence check: the generators, the preparation tools, and their validation records. The requirement itself — a generated worksheet among the deliverables, every sampled pair judged, every mismatch resolved — lives in the skill body's completion gate. This file carries what a preparer or a reader needs when a document in one of these styles is actually in hand.

## Tools and example invocations

All tools live in this skill's qa material.

- Numbered lists: `python3 qa/correspondence_worksheet.py <copy.md> [out.md] [--plan <split-plan>]`
- Author-year: `python3 qa/correspondence_worksheet_ay.py <copy.md> [out.md] [--plan <split-plan>]`
  (the `--plan` argument carries the split plan's declared extra list headings and dismissed heading-candidate line numbers, so every tool reads them from the one place)
- Chicago notes-bibliography: `python3 qa/correspondence_worksheet_notes.py <copy.md> <entries.json> <entries.txt> [out.md]`
- MLA: `python3 qa/correspondence_worksheet_mla.py <copy.md> <entries.json> <entries.txt> [out.md]`
- Indent flush-left numbered lists: `python3 qa/prepare_numbered_lists.py <copy.md> [out.md]`
- Rebuild a superscript-citation copy from the PDF: `python3 qa/extract_superscript_citations.py <in.pdf> <out.md>`, then run prepare_numbered_lists.py on the output.

A generator that detects no list, no page anchor, or no citation prints a warning and exits with code 2 rather than reporting a clean empty result; an empty sheet is never a pass.

Japanese journal formats are in scope for this check (review run 20261118-12, decision 4; cross-checked in run 20261118-13, which confirmed both findings and added the failure paths below). List detection is shared by every tool through qa/list_detect.py: headings match by whole-line equality after normalisation (spaces — including between characters — emphasis, a leading chapter number, and a trailing colon are stripped, Latin case folded), and the default set is 参考文献, 引用文献, 文献, References, Bibliography, Works Cited. Entry forms are `N.`, `[N]`, `N)`, and `N）` (the space after a full-width parenthesis is optional). Citation forms add enumerations of three or more — (1,3,5) — wave-dash ranges — (2〜4), (2～4) — and the single-parenthesis forms 6) / 7）; superscript `N)` citations are rebuilt into (N) tokens by qa/extract_superscript_citations.py, which now accepts the closing-parenthesis and wave-range superscript spans. A heading-like line that does not become a list — its heading outside the active set, or no entry readable under it — is named in the generator's warning block and exits with code 2, never dropped silently; dismiss a false candidate (a table-of-contents line) by recording its line number under `list_heading_dismissed` in the split plan and passing `--plan` to the generator. Additional headings are declared once in the same place (`list_headings` in the split plan), not handed to each tool separately. As a detector-independent backstop, the split plan can declare per-unit list counts (`lists: N` on a unit line, taken from the structure map), and the gate fails when the detected total disagrees with the declared total. Not yet verified on a real Japanese journal article: the support above is implemented and regression-tested on synthetic copies shaped like the real thing, and the first real article read should be treated as the field validation of these forms.

## Marked units (all styles)

The preparer marks each unit that owns a list — a chapter, part, or section — in the reading copy with a `# Chapter` / `# Part` / `# Section` line, and the generators sample citations only from inside the marked unit that contains the list, because the earlier sampling span, from the previous list to the next list's heading, reached into the following unit's body text and paired its citations with the wrong list. A 2026-11-13 validation on three documents (the trial document, a fresh findings note, and an English chaptered book) confirmed the marked-unit sampling removed the known cross-unit pairs and kept every sampled pair inside its list's unit.

## Numbered lists

The generator also accepts the bracketed surface form — IEEE "[N]" entries and "[N]" citations — unchanged. Range and pair forms ((2–3), (2, 3)) are expanded to their individual numbers, and a citation whose number exceeds the list's size is sampled and shown against a missing entry rather than dropped, because an entry deleted from the list while the text still cites it is the classic offset.

## Author-year

The companion generator pairs by (first author, year) key instead of by number, samples the most-cited key, the first and the middle citation, and up to three citations whose key matches no entry in the list, because in this style the offset failure appears as a citation pointing at no entry — a missing entry, a wrong year, or another unit's citation. On its 2026-11-13 validation document (a 595-page handbook with 37 chapter lists) about nine in ten citation occurrences carried a key that matched an entry in their own chapter's list.

Japanese author-year citations are not supported by the generator; when body lines carry that shape it warns and exits with code 2, stating the gap instead of silently producing a partial sheet.

## Notes-bibliography (Chicago)

The companion generator pairs each sampled note's shortened citations (surname + short title) with bibliography entries, sampling per notes unit — note numbering restarts per chapter — the first citation, the middle note's citation, the most-cited surname, and up to three citations resolving to no entry, because in this style the failure appears as a short form pointing at no entry or at a different work by the same author.

## MLA

The companion generator pairs surname-form citations (Surname page) with Works Cited entries and shows page-only citations with a passage window instead of a pre-filled pair, because in MLA the author is usually named in the sentence and the parenthesis carries the page alone, so that resolution runs through the named author and is the reader's judgement, not a mechanical key. Page-only sampling takes the first, the middle, and the last, plus a spread across the text, with the first/middle/last guaranteed to survive the sample cap.

## List parsing (notes and MLA)

Neither the notes nor the MLA generator parses the reference list itself: a preparer segments the list one entry per line — a repeated-author dash line is its own entry, with the author written in where the dash stands — and parses it with AnyStyle, the established reference parser, whose CSL-JSON output the generators consume, because on the notes generator's 2026-11-13 validation document (a 351-page monograph, 1,404 bibliography entries after dash-splitting) the first hand-rolled pairing merged dash-continued entries into one block and paired short titles with the wrong work by the same author, while the AnyStyle-based pairing resolved the sampled short titles to the right works. On the MLA validation article (45 Works Cited entries) the surname-form pairs resolved correctly and seventy page-only citations were counted for sampling.

## Superscript-number citations (AMA)

Superscript-number citations never survive plain-text extraction, which flattens them into ordinary digits indistinguishable from years and counts, so for those the preparer first rebuilds the reading copy from the PDF with qa/extract_superscript_citations.py: it reads the styled text spans, treats a superscripted digit span as a citation and writes it into the copy as an "(N)" token. List indenting is not part of that tool: run qa/prepare_numbered_lists.py on its output next — it indents continuation lines inside a detected numbered list whose entries run "N." or "[N]", and on a real IEEE two-column article it took the generator from one recognised entry to all 31, while on report-style copies whose lists already indent their continuations it left the sampled pairs unchanged. Both tools count lines far wider than the column they sit in and report them, because an extractor occasionally merges the two lines that share a height across a column gutter into one; check the reported spots before trusting the copy there.

The superscript flag the extraction tool reads is the PDF engine's own detection (PyMuPDF span flags) — the same device the citation-extraction literature uses for this problem. The extraction tool itself, qa/extract_superscript_citations.py, is part of this skill: it is bundled in the qa folder and imports PyMuPDF (AGPL-3.0, Artifex). The script is house-written code; PyMuPDF is an external dependency the user obtains separately (for example by pip) and is not redistributed with this skill, so running the script means using that library under its AGPL-3.0 terms. A measured MIT-licensed alternative (digit characters notably smaller than and raised above the line's body text, via pdfplumber) recovered fewer markers on the validation document (30 of 41 cited numbers against PyMuPDF's 41 of 41); that pdfplumber route is not bundled with this skill and stands as an optional fallback where AGPL is not acceptable. On that document (a JAMA Network Open article with 41 references) the superscript spans yielded exactly the cited numbers 1–41, the list parsed as 41 consecutive entries, and the sampled pairs paired correctly; superscript affiliation numbers in a byline and plain-text lookalikes such as counts in parentheses inside tables also reach the sheet, where the reader judges them like any other sampled pair; the token total therefore exceeds the citation count (55 tokens against 41 citations on the validation document, the article's own citation line among the extras), and a pair sampled from one of these is recorded as an extraction false positive, not as a mismatch in the document.
