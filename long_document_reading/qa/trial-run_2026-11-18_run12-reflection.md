# Trial run — execution type (2026-11-18, review run 20261118-12 reflection)

A fresh agent with no context beyond the skill itself ran the changed
tools end to end on synthetic fixtures (no real document content).
Scenarios and results:

1. inventory_pdf.py on a synthetic PDF carrying MSIP_Label custom keys:
   `sensitivity_label_present: yes`, exit 0. On a plain PDF: `no`,
   exit 0. (R-07)
2. verify_masking.py --counts-only on a masked copy with placeholders
   of several kinds across three pages: originals 0 hits, patterns
   0 hits, placeholders recounted by kind with pages (NAME 6, ORG 4,
   PLACE 3, 名前 1; total 14), exit 0. (R-08)
3. make_split_plan.py with --start-time=…: the specified start time was
   recorded unchanged, exit 0. (R-01)
4. correspondence_worksheet_notes.py on a copy with no Notes heading:
   warning printed, no sheet written, exit 2, no traceback. (R-13)
5. correspondence_worksheet_mla.py on a copy with no page anchors:
   warning printed and a warning block inserted in the sheet, exit 2.
   (R-13)
6. Normal case, correspondence_worksheet_notes.py on a small valid
   copy: sheet generated with all three sampled pairs matched, exit 0.
7. Question check on the body: the split-plan procedure, the
   text/Markdown sensitivity declaration, and the page anchor format
   were each located and quoted from the current wording as written.

Finding and disposition:

- make_split_plan.py --start-time in the space-separated form
  (`--start-time VALUE`) was silently ignored and the current time
  recorded instead; only the `=` form worked. Disposition: fixed the
  same day (both forms accepted), and the same silent-ignore pattern
  in verify_masking.py's --targets / --placeholder was fixed with it.
  Re-verified by the author: space form now records the specified
  start time, and a space-form --placeholder regex is honoured.

gate-hash: 6de717b20b5a9dde18ac6ef5f41a3a76c31c85900801fe3f4342c12d18fe70c7
gate-result: accepted
