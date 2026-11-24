#!/usr/bin/env python3
"""Indent continuation lines inside numbered reference lists in a copy.

Journal reference lists (JAMA, IEEE, most publisher PDFs) are typeset
flush-left: an entry's wrapped lines start at the same margin as the
entry itself, so the worksheet generator's entry run cannot tell a
continuation from the body text that follows the list, and stops after
the first entry. This preparer tool applies the same
preparer-marks-structure device as the chapter markers elsewhere in
this skill: inside a detected numbered list -- a line whose normalised
form (shared detector, qa/list_detect.py) is one of the list headings
(参考文献, 引用文献, 文献, References, Bibliography, Works Cited), followed by
entries 1., 2., 3., ... or [1], [2], [3], ... or 1), 2), ... in sequence -- every
continuation line is indented by two spaces, which is the form the
generator's run accepts.

The region ends at an entry number that restarts or skips, at an
all-caps heading line, at any other heading or '#' line, at a blank line followed by any flush-left line that is not the next entry
(post-list matter starts after a blank, while entry continuations run on
solid; blanks that belong to a page break sit next to a page anchor and
do not count), or after 800 lines; a line far wider than any journal column (250 characters) also ends it. A merely wide line (over 110 characters) is indented but counted in the report: an extractor sometimes merges the two lines that share a height across a column gutter into one, and the preparer should check those. The tool
prints how many lines it indented per list, so the preparer can check
the result before handing the copy on.

Scope: PDF-derived copies whose numbered lists are flush-left journal
lists. Report-style copies whose lists already indent their
continuations (the generator's home ground) need no preparation.

Usage: prepare_numbered_lists.py READING_COPY.md [OUT.md] [--plan SPLIT_PLAN]
When no numbered list is detected at all, the tool warns and exits with
code 2 (the generators' convention), instead of silently passing a copy
it did not prepare.
"""
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from list_detect import DEFAULT_HEADINGS, extra_headings_from_plan, normalize_heading

_argv = sys.argv[1:]
_plan_text = None
if "--plan" in _argv:
    _i = _argv.index("--plan")
    _plan_text = open(_argv[_i + 1], encoding="utf-8").read()
    del _argv[_i : _i + 2]
src = _argv[0]
out = _argv[1] if len(_argv) > 1 else src
lines = open(src, encoding="utf-8").read().split("\n")

_ACTIVE = {normalize_heading(h) for h in DEFAULT_HEADINGS}
if _plan_text:
    _extra, _ = extra_headings_from_plan(_plan_text)
    _ACTIVE |= {normalize_heading(h) for h in _extra}
ENTRY = re.compile(r"^(?:(\d{1,3})\.|\[(\d{1,3})\]|(\d{1,3})\)|(\d{1,3})）)\s*")
CAPS_HEADING = re.compile(r"^[A-Z][A-Z0-9 ,&\-]{3,}$")
ANCHOR = re.compile(r"^#{1,2} Page \d+$")

prepared = []
i = 0
report = []
while i < len(lines):
    ln = lines[i]
    prepared.append(ln)
    i += 1
    if normalize_heading(ln) not in _ACTIVE:
        continue
    expected = 1
    indented = 0
    wide = 0
    blank_seen = False
    prev_anchor = False
    steps = 0
    while i < len(lines) and steps < 800:
        cur = lines[i]
        steps += 1
        if ANCHOR.match(cur):
            prepared.append(cur)
            blank_seen = False
            prev_anchor = True
            i += 1
            continue
        if cur.strip() == "":
            prepared.append(cur)
            if not prev_anchor:
                blank_seen = True
            i += 1
            continue
        prev_anchor = False
        m = ENTRY.match(cur)
        if m and int(m.group(1) or m.group(2) or m.group(3) or m.group(4)) == expected:
            prepared.append(cur)
            expected += 1
            blank_seen = False
            i += 1
            continue
        if len(cur) > 250:
            break  # far wider than any journal column: body text, not a wrap
        if len(cur) > 110:
            wide += 1  # wider than the column: possibly two lines merged
            # across the gutter by the extractor; indent it as a
            # continuation, but count it so the preparer can check it
        if (
            m
            or CAPS_HEADING.match(cur.strip())
            or cur.lstrip().startswith("#")
            or normalize_heading(cur) in _ACTIVE
            or blank_seen
        ):
            break  # leave cur for the outer loop; the list region is over
        if not cur.startswith((" ", "\t", "　")):
            prepared.append("  " + cur)
            indented += 1
        else:
            prepared.append(cur)
        blank_seen = False
        i += 1
    report.append(f"list at line {len(prepared)}: entries 1..{expected - 1}, indented {indented} lines, wide lines {wide}")

open(out, "w", encoding="utf-8").write("\n".join(prepared))
if not report:
    print("警告: 番号方式のリストが1本も検出されませんでした（見出し・項目形式を確認すること）", file=sys.stderr)
    print("lists prepared: 0")
    sys.exit(2)
for r in report:
    print(r)
print(f"-> {out}")
