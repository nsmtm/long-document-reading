# Reading Long Documents

The coordinating agent in this skill — the agent running it — interviews the user, verifies what other agents deliver, and reads only what the rulings allow it. Other agents (a cloud assistant, the user's local models) each act under their own recorded rulings.

The history behind the rules (dates, trials, measurements) is in `references/sources.md`. The evidence cited as §1–§4 is in `references/evidence.md`.

## Which file carries which phase

| Phase | Carried by |
|---|---|
| Inventory | qa/inventory_pdf.py (whitelisted fields only), this file |
| Interview | this file; the rulings are recorded in the work folder's rulings.md |
| Masking decision and verification | this file for the framing rules, [the masking reference](references/masking.md) for the steps, [the bridge reference](references/bridge.md) for the Copilot route, qa/verify_masking.py |
| Conversion and preparation | [the conversion reference](references/conversion.md) for the steps, [the converter reference](references/converters.md), [the correspondence reference](references/correspondence.md), qa/make_reading_copy.py, qa/make_split_plan.py |
| Reading and notes | this file |
| Completion gate | qa/check_gate.py, the correspondence worksheet |

## Decide whether full reading earns its cost

- Use this skill when:
  - completeness itself is the deliverable, such as counting and reconciling items where an omission is an error;
  - a conclusion rests on something being absent, or on the document agreeing with itself as a whole, as with contract terms and required item coverage;
  - an extraction or a summary that another agent produced must be verified, because partial application and snippet-level reading only surface against a full count;
  - a document will be questioned repeatedly, because the structure map, the notes and the counts let later questions return to exact pages instead of starting over.
- Skip it when a question can be answered by search. Reason: search returns what it finds and cannot prove a total or an absence.
- Follow an explicit request for a full read even when search might answer the immediate question, and let the interview carry the exchange about purpose and scope. The choice belongs to the user; this section informs it rather than overruling it.
- Expect the read state itself to vanish with the session. The artifacts are the durable result: later work stays on the map and the notes, and returns to the text only at named anchors.
- Budget as a wide range, not a point, and measure from the pilot instead of trusting either end of the field record. One 116-page document cost about 5 percent of a monthly Codex quota and minutes of wall time on one reader, and between 37 minutes and seven and a half hours on a local model. Re-reading on demand stays a realistic alternative to holding the text in context.

## Inventory the document, declaration before sampling

- **Container fields first.** Run `pdfinfo <file>.pdf` and record the page count, the page size, and whether the pages are slide sized. Before the sensitivity declaration, record only those container fields, never the document's own metadata text such as its title or author: those fields can carry proper names before any declaration is taken.
- **Security signals,** checked without extracting body text: the encryption flag in the `pdfinfo` output, a sensitivity label carried in metadata, and the source the file came from.
- **The sensitivity declaration.** Ask the user to declare the document's sensitivity before any sampling, on every branch including a text or Markdown arrival, whatever the signals say. An unlabeled or mislabeled file is not thereby a safe file. The signals may only raise the sensitivity; record any user override of a signal-based flag in the rulings.
- **A flagged file** (the signals or the declaration mark it security sensitive): stop your own handling of the original, keep the original away from every reader the rulings bar from it from this point on, and route the file under the restricted path ("Decide masking on evidence"). A barred reader never reads the original of a flagged file and works only from its masked copy.
- **Sample a file that passed that check:** `pdftotext -f 1 -l 2 <file>.pdf -`, a sample from the middle, a sample from the last pages, and one table-heavy page. Judge whether the document is born digital, scanned or garbled. Damage hides mid-document, and this judgment feeds the choice between reading the PDF itself and converting.
- **Further probes:** `pdffonts <file>.pdf` when extraction looks garbled, `pdfimages -list <file>.pdf` when figures may matter, and `pdfdetach -list <file>.pdf` when the file might carry embedded documents.
- **Classify** the document as text heavy, scanned, slide deck, form heavy or data heavy: the reading strategy follows the type. In a slide deck, treat each slide as one reading unit, read its text layer for content, and rasterize only the slides a question names.
- **Other arrivals.**
  - Text or Markdown: skip the inventory and conversion steps, and enter at the interview with its headings or page anchors as the split basis. The sensitivity declaration is not skipped with them: on this branch, take it at the interview itself, before any sampling or reading.
  - A Word file (docx) is its own arrival branch. Do not open its body to judge it, because sensitivity labels ride on this format. Take its container facts and go to the interview, and let the interview and the conversion step settle how it is read.
  - Text or Markdown without page anchors or folio numbers: ask for the source PDF when page-level citation matters; otherwise read by heading units and reconcile coverage by sections and lines.

## Interview the user for what machines cannot know

- **Purpose and scope.** Ask what decision or deliverable the reading serves. Declare the scope as a full read or a named subset of the document, and fix a named subset as page ranges in the split plan before reading starts.
- **Readers.** Ask who will read the material. For each named reader, record whether the original is allowed or only a masked copy, together with the sensitivity cap that reader may see. The cap means which copy that reader may see (the original, the masked copy only, or nothing), not a graded scale.
- **The rulings file.** Record every ruling this read depends on in one rulings file in the work folder (rulings.md): the reader rulings, the sensitivity declaration and any override of it, the masking decision, and the correspondence ruling. Name that file among the artifacts a resumed reader reads first. Reason: a ruling held only in the conversation vanishes with the session.
- **Sensitive originals.** Ask the user to name them, such as client and organization names: the replacement list and the zero-hit verification both need them in the user's own words.
  - Keep that list in a separate originals file held by the user, not in the rulings file, and delete the file alongside the other unmasked derivatives when the work ends.
  - On the restricted path the list goes to the permitted reader who runs the verification, never to a barred reader, who receives counts and locations only.
- **Confirm the sensitivity declaration** taken in the inventory (on the text or Markdown branch, taken at the interview itself) before sampling. Treat the file as flagged when either the signals or the user mark it sensitive. Record any later change to the declaration, or any override of a signal-based flag, in the rulings.
- **Known structure and companions.** Ask what the user already knows about the structure, such as the chapter layout and where reference lists sit. Ask what companion material exists in any form, such as a slide deck, a summary, a term mapping file, or a numbering table held outside the document.
- **Citations and the correspondence ruling.** Ask how strict citations must be, and whether counts or coverage must be reconciled at the end. Record citation correspondence as a ruling, with the reader rulings:
  - Checking sampled citations against their list entries by content is part of the method by default wherever the document carries numbered (parenthesised, bracketed, or superscript) or author-year reference lists and in-text citations, a Chicago notes-bibliography apparatus (numbered notes citing in shortened form against a bibliography), or MLA in-text citations against a Works Cited.
  - It leaves the scope only when the requester explicitly excludes it, never by a reader's inference from silence. Reason: a plan that scoped the check out as unrequested once left a wrong citation undetected (evidence: references/evidence.md §1).
- Leave numbering systems and term usage to the structure-map stage, where the document itself can answer first and the user confirms.

## Decide masking on evidence

Read [the masking reference](references/masking.md) when this step comes up, and again before anything masked is sent on. It carries the restricted path's steps, the evidence scan, and the rules for applying, verifying, repairing and deleting. The rules that frame it stay here:

- **Two paths, never mixed.** Branch on the inventory triage: the restricted path for a flagged file, the evidence scan for any other file. Never mix steps across the two paths.
- **Who is barred is a ruling.** On the restricted path, only the readers the interview's rulings name as permitted may read the original. A barred reader receives no original, no unmasked derivative and no unmasked quotation. Which agents sit on which side is a ruling, recorded per read in the rulings file, never a fact written into this body; an agent with no recorded ruling is on the prohibited side by default.
- **The user decides masking** for each document, from the evidence the masking reference has you present.
- **Hold external transfer while the decision is open.** Work that stays within the recorded reader list and rulings may proceed, on the PDF itself or on a copy already made.
- **The Copilot route** in [the bridge reference](references/bridge.md) is the default masking route for a file flagged as security sensitive. Follow it only when the recorded ruling for that reader allows the original to reach it, up to the recorded sensitivity cap.
- **No masking, no masking verification.** Skip the masking verification when the decision was not to mask: there is no masked copy to verify, and the conversion checks already cover the unmasked copy.

## Convert a pilot first, then the whole document

- **Read the PDF itself** when the reading agent can read it faithfully page by page, and take pages as the unit of account for coverage in that case. Conversion is a means, not a step owed.
- **Convert only when direct reading hits its limits:** a garbled or missing text layer, pages that need OCR, tables or figures the text layer mangles, a handover that needs a file the receiving agent can open, an interview ruling that counts must be reconciled at the end, or the correspondence ruling standing. Reason: page-level accounting cannot reconcile counts, and a correspondence worksheet cannot be built on the PDF itself.
- **Read [the conversion reference](references/conversion.md) before converting.** It carries the steps in order: converting inside the reading agent, the pilot and its time budget, the choice of converter, multi-column documents, page anchors, the form of the copy, preparing it for the correspondence check, generating the worksheet, and recording the copy's identity.
- **The invariant that frames it:** record the reading copy's identity in the split plan only when the copy is final, after every step that rewrites it (preparation and, when the decision was to mask, masking, its verification, and any repair). Generate the worksheet and every artifact that will travel with a masked copy from that final copy only. Applying and verifying the masking: [the masking reference](references/masking.md).

## Build the structure map and confirm the traps

- Build a structure map from the table of contents, headings and chapter endings, and save it as a file the reading can follow.
- **Check the map:**
  - the heading line at the start of each unit against its table-of-contents entry; record a mismatch as a defect of the copy. Reason: a stale heading carried over from another chapter survives unnoticed when the map follows the contents alone.
  - against a slide deck or summary of the same document when one exists, because a compressed map catches chapters the extraction flattened. When sources conflict, trust the document itself first, then companion material, then recollection, and surface the conflict to the user.
  - against what the user declared in the interview; ask about any mismatch before reading. Known structure taught up front reads faster than structure discovered mid-read.
- **Numbering.** Confirm from the map how numbering works: whether numbers restart per chapter, and whether several numbering systems coexist. Ask the user only about systems the map cannot settle or that live outside the document. Record citations as the chapter name plus the number, never the number alone.
- **Verify correspondence, not only continuity.**
  - Sample citations against their list entries, always including the highest number cited from each list. Judge each pair by content: what the citing passage says the reference is (its topic, method, or authors) against the entry that actually sits at that number. Reason: a numbering offset leaves every number present and sequential while pointing one entry off (evidence: references/evidence.md §2).
  - Judge on the correspondence worksheet the completion gate requires, which places each sampled citing passage beside its list entry. A check left as an intention degenerates into verifying that the numbers run continuously.
  - Judge each pair from the passage and entry the sheet places side by side, without writing new extraction or recounting scripts for the judgment: improvised re-verification duplicates what the sheet already holds (evidence: references/evidence.md §2). When the sheet's material cannot settle a pair, record that insufficiency as the ground for that pair instead of extending the tooling.
  - Before judging a pair, confirm the citing passage belongs to the chapter whose list it is paired with: a sampled passage can come from the following chapter's body, which sits before that chapter's own list (evidence: references/evidence.md §2).
- **Traps to check:**
  - terms that appear under names in more than one language; build the term mapping at this stage when none exists;
  - where reference lists, appendices and supplements sit, because extraction targets often live at chapter ends rather than at the end of the document;
  - text that lives outside the text layer, such as figure labels and table cells drawn as graphics; list the pages that need visual reading;
  - two-column layouts and footnotes that break reading order; note the affected ranges in the map;
  - placeholder entries and duplicate items carried across chapters; keep duplicates per chapter until the user says to merge them.
- On the restricted path, build the map from the masked copy alone, as with every later artifact.
- **The split plan.**
  - Split the reading copy by structural units from the finished map, not by token count. A unit is a top-level structural division, such as a chapter or a top-level section. Write the split plan to a file before reading starts.
  - Create the split plan file at the first inventory action, so the start time has a file home from the start, with the reading copy's identity lines marked pending: the finished copy does not exist yet.
  - Record in it the start time taken when the work starts (the session's first inventory action, not when this file happens to be written), each count as the reading fixes it, and the correspondence ruling with the path of the worksheet in the work folder, or the exclusion and who requested it. Reason: the plan file is the checkpoint that survives a lost session, while anything held only in the conversation vanishes with it.
  - Once the copy is final (preparation finished and, when the decision was to mask, masking and its verification closed), record its identity (its path, byte size, and a hash such as MD5) by generating the plan from the template (qa/make_split_plan.py) with --start-time set to the start time already recorded, so generating the identity never rewrites it.
  - Sub-split any unit whose estimated cost (the measured tokens per page multiplied by its page range in the map) exceeds what the effective context window leaves room for alongside notes. Cut at subheading or paragraph boundaries in order, and record the sub-units in the split plan.

## Survive the harness losing your place

- **Know the compaction trigger before a long read on an agent harness.** Establish the effective context limit the harness will enforce and the compaction trigger it derives from that limit. The enforced limit can be smaller than the displayed one: the display can show a default while the endpoint's smaller served window governs the trigger.
  - With Goose defaults, the trigger is the smaller of four fifths of the effective limit and an absolute cap of 225,000 tokens (the resolution precedence and the measured case: references/evidence.md §3).
  - When the measured cost of the read will cross the trigger, raise the served window before starting, or accept the compactions under the checkpoint discipline below.
  - Never set a declared limit above the window the endpoint actually serves: requests then hit the real cap and truncate instead of compacting.
- **Keep every fact in the artifact files.** Assume the harness can compact, restart or replace the session at any point, because agent harnesses do this without asking. Every fact the rest of the read depends on lives in the structure map, the split plan as checkpoint, and the notes.
- **Resume from the checkpoint** after a compaction or in a new session:
  1. Read the split plan, the structure map, the rulings file and the notes first.
  2. Confirm the reading copy is the same file, by the byte size and hash recorded in the plan.
  3. Continue from the first unit that has no notes entry.

  Reason: a resumed reader who restarts from its own reconstruction re-derives finished work, and can silently drop defects and decisions the artifacts already recorded.
- **Write as you go.**
  - Write each unit's notes immediately after reading that unit and before reading the next one. The notes file is the resume granularity: a unit read but not yet noted leaves no trace after a context loss and will be read again.
  - Extend the same discipline to every deliverable: save the worksheet judgments, the structure map and any report as each phase completes, instead of batching all writing into a final phase. A session that stops before the final phase loses the batched work whole.
- **Do not re-derive what is recorded.** Treat counts and verifications already recorded in the artifacts as fixed once the copy's identity checks out, and re-verify only what the identity check or a visible inconsistency puts in doubt. Re-deriving finished work after every restart multiplies the cost of a long read.
- **Bounded chunks.** Read the copy in chunks sized to what the harness returns whole (a few hundred lines is a safe start). When a chunk comes back truncated, shrink the chunk and re-read the missing range before counting the unit as read: truncated output looks like a completed read and silently opens a coverage gap.

## Read in structural units and keep notes

- Read every unit and sub-unit in the declared scope in order yourself, without sampling and without delegating the primary read to summaries from another agent.
- Write notes to a file after each unit. Scale their depth to the purpose declared in the interview: full notes for a document that will be used in depth, lean notes for verification work, where counts, anomalies and coverage carry the value.
- Answer questions from the document with the supporting sentence quoted and its page or heading named. Say the document does not contain the answer when it does not.
- Track progress as units completed and units remaining within the declared scope, never as a percentage of pages skimmed.
- Rasterize a page with `pdftoppm -jpeg -r 150 -f N -l N <file>.pdf <prefix>` only when the map or a question names that page as visual: an image page costs several times a text page.
- Summarize from the notes at the end, following the document hierarchy from units to chapters to the whole, rather than summarizing raw chunks a second time.

## Pass the completion gate before claiming done

- **The coverage statement** names the source file, the declared scope, the total for that scope (in lines of the reading copy, or in pages when the PDF itself was read), and the exact range each unit and sub-unit covered, with its page anchors alongside.
  - Generate its facts with qa/make_coverage_statement.py from the copy, the plan and the notes, rather than writing its table by generation: its inputs determine it completely.
  - Reconcile it mechanically, so the unit ranges add up to the scoped total with no gap and no overlap unaccounted for.
- **Unread and out of scope.**
  - Require a notes entry for every unit and sub-unit in the split plan; a missing entry is an unread unit.
  - Name anything inside the declared scope that stays unread, with its reason, and do not describe the read as complete while it exists.
  - Name material outside the declared scope as out of scope, never as an unread remainder.
- **Counts.** For extraction work, the number of items in the deliverable equals the number counted in the source. Investigate any difference before delivery.
- **Times.** Take the start and end times a completion report states from the files: the start time from the split plan, the end time from when the coverage statement is written. Never take them from file or folder timestamps, which record when a file was placed, not when the reading ran.
- **Register the finished artifacts** with the work that owns the document: leave a pointer with the actual paths of the reading copy, the structure map, the notes and the coverage statement in the owning project's own record. Artifacts that only the reading session knows about are treated as absent by later work.
- **Numbers and enumerations come from tools.**
  - Carry every number in a deliverable from a tool output rather than retyping it, and have the counting tool itself print the totals it reconciles: a total re-derived in prose can diverge from the counts it claims to sum.
  - Build any table that enumerates the source (an anchor table, a page index, a long item list) from tool output rather than writing it out by generation, and reconcile it against the source by count or diff before the completion gate: a hand-written enumeration silently duplicates and drops entries.
- **The correspondence worksheet** is required among the deliverables whenever the interview's correspondence ruling stands.
  - Every sampled pair carries a recorded match or mismatch verdict and a one-line reason. Resolve every mismatch in the completion report before claiming done.
  - The sheet exists before any judging starts: it is generated from the prepared reading copy during conversion, never assembled by hand. The gate check compares its list counts against the copy, and its sampling stays inside the marked unit that owns each list.
  - The styles covered are numbered lists (including the Japanese journal forms: a 「文献」 heading, N) / N） entries, and single-parenthesis citations), author-year, Chicago notes-bibliography, and MLA. Superscript-number citations (AMA) are first rebuilt into (N) tokens during preparation. The per-style generators, the preparation tools and their validation records live in [the correspondence reference](references/correspondence.md).
  - When the requester excluded correspondence, require the completion report to restate the exclusion as a scope limitation instead: a correspondence check that leaves no artifact degenerates into checking that the numbers run continuously (evidence: references/evidence.md §4).
  - In the completion report, state the evidence base the check rests on: how many distinct documents and lists the sampling covered. Repeated trials of one test document are a single evidence base, not several independent ones.
- **The gate check.** Run qa/check_gate.py over the reading copy, the split plan, the notes and the worksheet before claiming done, and treat anything it fails as unread or unreconciled. The anchor continuity, the tiling of the unit ranges, the notes presence and the list counts are mechanical, and a reader's self-report of them is not evidence, least of all when reader and checker would be the same agent.
  - The counting rules those checks encode live in the shared detector (qa/list_detect.py) that the gate and the generators all use, where they are tested, rather than in this prose: count occurrences, never the lines that contain a match; count a list from its own heading line; an entry counts only at a line beginning with its number in one of the entry forms (N., [N], N), N）), the numbers running 1 to N without gap or repeat.
  - The gate reads the declared scope from the split plan, checks the copy's identity against the plan, requires a verdict on every sampled pair when the correspondence ruling stands, and compares the detected list count against any per-unit list count the plan declares. A detector shared by the gate and the generators can only lose a list it cannot see; the declared count is the one check that does not depend on it.
- Treat a self-reported figure from another agent, such as a read rate or a search accuracy, as a claim to verify against the artifact, never as evidence.
- Check delivered files byte for byte with qa/compare_bytes.py when a file arrives again under a new name: an unchanged file is sometimes uploaded twice.

## Bridge the work to another agent

- Confirm the first transfer to each external agent with the user before sending, as one named question the user can answer yes or no: the agent, the units, and whether the masked or the original copy goes.
- Hand over in a file at a break in the work, using the handover format in [the bridge reference](references/bridge.md).
- Before the receiving agent answers questions or transforms content, require it to prove it read the material by quoting the heading list and the last paragraph exactly. Where it refuses verbatim quotation, fall back to the non-verbatim access proofs in the bridge reference. On the restricted path, use only the non-verbatim access proofs: a verbatim quotation would itself carry unmasked wording to a barred reader.
- Send the receiving agent only the units its task needs, in the copy its recorded ruling allows, together with the structure map and the numbering rules.
- Verify what the receiving agent delivers against the source yourself, using counts, source strings and the coverage statement, before the work moves on.

## Alternatives for better results

- When the stakes justify it, use a second agent for an independent re-read, sending the same copy the recorded rulings allow. Reconcile only the disagreements against the source. The re-read is complete when every disagreement has been resolved against the source or recorded as unresolved.
