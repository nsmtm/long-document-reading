# Bridge reference for long_document_reading

This file carries the parts a receiving agent needs in plain form, because a receiving agent such as Copilot or a local model cannot load the house's Copilot file-work skill where these parts first lived.

## Handover file format

Build the handover as one Markdown file with these six items.

- The purpose of the work
- Fixed decisions with their reasons
- Where the work stands now
- Options not adopted with their reasons
- Unconfirmed and held items, written as unconfirmed and never as decided
- The next actions in priority order

Ask for a handover only at a break in the work, where a break means a finished unit of work, the end of a session, or a change of agent, and never while the other agent is still executing. Fix the deliverable at the head of the work and state that the handover file is not the deliverable.

## Reading check for the receiving agent

Give the receiving agent this check before it answers questions or transforms content. A mention of the file title is not evidence of reading.

First ask for the list of headings and the last paragraph, quoted exactly as written. With Copilot, expect a refusal of the verbatim quote on copyright grounds, as observed in the 2026-11-07 field test, and fall back to non verbatim access proofs that only full access can answer, such as how many numbered proposals the last page lists, or the first and last words of its last paragraph.

Then give the answering rule in this wording.

Answer only from this file. Quote the supporting sentence exactly and name its page or heading. If the answer is not in the file, say that the file does not contain it. Do not fill gaps with guesses or with knowledge from outside the file.

Repeat the reading check after a break in the work, after a change of topic, or at any sign the file is being misread, because a file read once can become unreadable later in the same chat. If the agent cannot open a file or fails the reading check, try a fresh upload in the same chat, then a renamed copy, then a fresh chat.

Confirm the file arrived as a direct upload rather than as a search or drive reference, because a referenced file can leave the agent holding only search snippets of its head, as Copilot itself reported in the 2026-11-07 field test after earlier claiming to have checked the content, and judge the arrival by the reading check and by what the agent itself reports holding.

## Verification prompt for file work

Use this wording at the start of file work with an agent whose reading is in doubt.

Base every answer on this file alone. Quote the exact sentence behind each answer and show its page or heading. If the answer cannot be found in the file, say only that it is not in the material. Do not complete the answer from inference or from knowledge outside the file.

## The Copilot masking route

The default is to mask locally and send only the masked copy. One exception exists and is used only under its conditions.

- Give Copilot the original file and have Copilot produce the masked file, then pass only the masked file onward to other agents.
- Use this route only for material up to the sensitivity the user has accepted Copilot seeing, because the original reaches Copilot in this route.
- Use this route as the default for a file flagged as security sensitive at triage, because the masking reader on this route is a permitted reader of the original while a barred reader must not read it, and a barred reader receives only the masked file this route produces.
- Record the route in the interview rulings for that reader, so the exception is a decision on file rather than a habit.
- Send a plain copy for masking work when the original carries encryption or a sensitivity label, because Copilot cannot read such files, where a plain copy is a copy without the encryption or the label, produced by the user, for example by printing the document to PDF.
- Open the masking instruction with a directive to execute the masking only, because Copilot tends to acknowledge receipt and offer a menu of other work such as reviewing the instruction or summarizing the content instead of executing, as observed in the 2026-11-07 field test.
- Hand the file and the instruction over together in the first message of a fresh chat, knowing that one package delivery alone did not prevent the menu stall in the 2026-11-07 field test, where the instruction still lacked the execute only directive.
- Treat a cannot reply deflection from Copilot, meaning the stock refusal of the whole topic rather than a refusal of one step, as a failed session rather than a failed instruction, restart in a fresh chat with the corrected package, and do not spend turns negotiating inside a chat that has already stalled, as observed in the same field test.
- Send commands to Copilot as pasted message text rather than as an attached instruction file, because an attached instruction is treated as material to describe and consult, while message text is treated as the user's direct command, as the contrast between the stalled runs and the immediately executed short commands showed in the same field test.
- Prefer a sequence of short single purpose commands over one long specification document when Copilot is the worker, and keep the full specification on the sending side as the checklist the delivered files are verified against, because a long specification invites consultation while short commands get executed, as the same field test showed.
- Hand each unit's text inline in the message when masking in segments, rather than relying on a file uploaded earlier in the session, because Copilot may no longer hold an earlier upload's content when a later unit is processed, as observed in the 2026-11-14 masking test, where it asked for a unit's original text it had already been given as a file.
