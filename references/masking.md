# Masking (the restricted path, the evidence scan, and verification)

Read this when the masking decision comes up, and again before anything masked is sent on. Moved out of SKILL.md; the rules are unchanged. The framing rules stay in SKILL.md, "Decide masking on evidence": two paths never mixed, who is barred is a ruling, holding external transfer while the decision is open, the Copilot default, and skipping verification when nothing was masked. Where masking falls in the preparation order follows the identity invariant in [the conversion reference](conversion.md).

## The restricted path (a flagged file)

- Present only the container facts to a barred reader, such as encryption, label and source. The user decides masking from those facts plus any counts a permitted reader reports.
- When the user decides masking is needed, route the original to a permitted reader for masking by default. The Copilot route in [the bridge reference](bridge.md) is the standing default route. Treat a slow permitted reader as fit for assigned slices rather than whole documents.
- When no permitted reader is available, stop the restricted path and hand the masking back to the user, rather than widening the reader list.
- When the original carries encryption or a sensitivity label, have the user supply a plain copy first: Copilot cannot read such files, as the bridge reference describes.
- Build the structure map, the notes and every later artifact on this path from the masked copy alone, and verify the masked copy by the counts and source checks the gate requires.

## The evidence scan (any other file)

- Extract a throwaway full text locally with `pdftotext -layout <file>.pdf <scan>.txt`, only on a file that passed the security check.
  - Use it only for this scan, never as the reading copy. The scan is read for counts, not for reading order, so the conversion section's multi-column prohibition on `-layout` does not apply to it.
  - Delete it when the masking decision is recorded, whether the decision was to mask or not.
- Count pattern-countable items in the scan by kind, such as email addresses, phone numbers, amounts and dates.
- Estimate names from the title pages and from names the user supplies, and label that figure a floor, not a count: automated name detection is weak for Japanese proper nouns.
- Check whether the document is already masked, by searching the scan for placeholder patterns and for the originals the user supplies.
- Present the scan result with its detection limits stated beside it, the reader list with its rulings, and a recommendation. Then let the user decide masking for this document.

## Apply the masking

- Apply the masking decision to the finished reading copy when the decision was to mask, replacing with consistent placeholders. Keep the mapping table with the user, never with the reading copy.
- Never use a digits-only bracketed form such as [1] or (2) as a placeholder: the correspondence tools read that shape as a citation, and the citation population silently grows.
- Exempt bibliographic information from masking, and leave reference lists untouched even when they contain personal or organization names: citations are public records, and masking them breaks count-based verification.

## Verify before anything is read or sent

- **Every artifact that will be sent on,** not only the reading copy. Run the masking verification (qa/verify_masking.py) over the worksheet, the notes, the structure map and the completion report too, and hold the send until each returns zero hits. An artifact generated from an unmasked copy carries the originals with it even when the copy itself verifies clean.
- **The original search** on the masked reading copy itself, before anything is read or sent: report the replacement counts, and search for each user-supplied sensitive original until it returns zero hits.
  - Match on text normalized with NFKC and stripped of whitespace and line breaks, with a substring match as the default: a whole-token search silently returns zero hits in Japanese. Reserve whole-token matching for originals made of alphanumeric characters.
  - Report hits inside reference lists rather than treating them as failures, and put those hits to the user for a ruling before anything is transferred on.
- **The pattern re-scan** over the masked copy, before anything is read or sent, on the same normalized text the original search uses:
  - phone numbers and email addresses, with zero hits as the expectation;
  - amounts and dates, as zero only when the masking decision named them as targets, and as reported counts otherwise. Reason: a legitimate report carries years and budgets that would fail every time and train a rubber stamp.
  - Exclude no section from the scan, and report every hit with its location: a contact block often sits after the reference list, at the very end of the document.
- **Candidate names** that the replacement table does not cover go to the user before anything is sent on.
  - Extract them independently of the masking agent: by a different reader, or mechanically with qa/extract_name_candidates.py from honorifics, role words, signature blocks and the neighbourhood of phone numbers. A candidate pass by the masking agent shares that agent's blind spots.
  - Hold the send until the user's rulings on the candidates are recorded in the rulings file.
- **Where the residuals sit,** not only how many there are: a masking pass by another agent can silently cover only part of a document, with the misses concentrated in its later chapters.
- **Expect a one-pass Copilot masking to leave residue,** even when the agent reports full coverage. The measured misses sat in the final paragraph and in the later chapters, so give the tail and the later chapters the same verification care as the rest of the distribution.
- **Never accept the masking agent's own replacement counts as verification.** Its per-kind counts have disagreed with the ground-truth ledger while the replacements themselves were correct. Recount from the delivered copy itself. On the restricted path, count placeholder occurrences in the masked copy rather than asking the agent for figures; qa/verify_masking.py performs the original search, the pattern re-scan and the placeholder recount.
- **On the restricted path:**
  - Every report these checks send to a barred reader carries counts and locations only, never the matched strings: the strings themselves would be a new route for the original to reach that reader.
  - Run these verifications on the permitted side, never by a barred reader. The reader who holds the originals list, or the user, runs qa/verify_masking.py with --counts-only against the masked copy, and sends the barred reader its output (counts and locations only).
  - On a route where the reader works from handed-over files and cannot run the script, the user runs it locally on the returned masked copy and relays the counts.
- **Noticing is not a layer.** When a reader notices a term that looks unmasked, it stops and reports the location only. Noticing is damage limitation, not a layer of prevention; the checks above are what keep it rare.

## Repair

- Repair only the regions where verification finds residuals, by segmented re-masking with a per-segment replacement report, or by a reverse-order sweep.
- Do not segment a whole document by default: it costs a human round trip per segment. The segmented route is a repair tool, not the default route. Its clean result rests on a single dummy measurement, not a guarantee.

## Delete the derivatives

- Delete every unmasked derivative made for sharing as soon as the masked reading copy passes verification: scan texts, pilot outputs, the unmasked reading copy, and anything generated from it before masking (an early worksheet is regenerated from the final copy first, then the earlier version deleted). Delete directly, not through a trash folder.
- The originals list file is the exception: hold it until the work ends and delete it then, because a residual found later is repaired and re-verified against it.
- Delete any copy of the original held inside the working area as soon as the work no longer needs it; on a security-sensitive file, at the end of the job at the latest. Never delete the user's own source file outside the working area: these deletion rules govern the working copies and derivatives this skill made, not the user's files.
- When a copy of a flagged original reached a barred reader's storage, delete it unread and directly once the user confirms a permitted reader holds the file, and tell the user it was removed unread.
- Report the deletion by file name, and state that it clears the working storage rather than guaranteeing erasure from system backups.

## Reidentification

- Flag reidentification risk from context, such as rare numbers, dates or a unique history, as a separate warning the user can act on.
