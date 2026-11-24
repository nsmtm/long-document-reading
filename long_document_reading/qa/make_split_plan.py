#!/usr/bin/env python3
"""Create a split-plan file for a long-document read, from the template.

The plan is the checkpoint that survives a lost session. Creating it at
the first inventory action gives the start time a file home from the
start (it used to live only in the conversation until the plan was
written after the structure map, and was lost to compaction more than
once). The template records the reading copy's identity (path, byte
size, MD5), the start time, the correspondence ruling, and the citation
style detected — the field whose accumulation is the review trigger for
the held proposal to retire low-use styles from the distributed body.

Units are added as lines in the fixed form the gate check parses:
  unit: <name> | pages: A-B
One notes entry per unit, headed "## <name>", is required in the notes
file.

Usage: make_split_plan.py READING_COPY OUT_PLAN.md [--start-time ISO]

The plan file is first opened at the first inventory action, before the
reading copy exists, so its identity lines start out pending; when the
finished (prepared) copy is in hand, regenerate or amend the plan with
--start-time carrying the start time recorded at that first action, so
regenerating the identity never rewrites the start time.
"""
import hashlib
import sys
from datetime import datetime

args = [a for a in sys.argv[1:] if not a.startswith("--")]
start_time = None
argv = sys.argv[1:]
for i, a in enumerate(argv):
    if a == "--start-time" and i + 1 < len(argv):
        start_time = argv[i + 1]
    elif a.startswith("--start-time="):
        start_time = a.split("=", 1)[1]

copy_path, out = args[0], args[1]
data = open(copy_path, "rb").read()
now = start_time or datetime.now().astimezone().isoformat(timespec="seconds")

plan = f"""# Split plan

- reading_copy: {copy_path}
- bytes: {len(data)}
- md5: {hashlib.md5(data).hexdigest()}
- start_time: {now}
- scope: (full read, or the named subset with its page ranges)
- correspondence_ruling: (stands / excluded by <name>)
- citation_style_detected: (numbered / author-year / notes / MLA / superscript-number)
- worksheet: (path, when the correspondence ruling stands)
- list_headings: (additional list headings beyond the shared default set, comma separated; omit when none)
- list_heading_dismissed: (line numbers of heading-like lines that are not lists, such as table-of-contents lines; omit when none)

## Units

unit: <unit name> | pages: A-B | lists: N
(the lists: field declares how many reference lists the unit owns, from
the structure map; the gate compares the total against the detected
count. A unit split inside a page adds "lines: a-b" (reading-copy line
ranges) beside its page range.)

## Notes

- One notes entry per unit, headed "## <unit name>", in the notes file.
- Record each count here as the reading fixes it.
"""
open(out, "w", encoding="utf-8").write(plan)
print(f"split plan -> {out} (start_time {now})")
