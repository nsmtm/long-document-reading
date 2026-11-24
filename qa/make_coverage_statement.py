#!/usr/bin/env python3
"""Generate a completion-gate coverage statement from the artifacts.

The statement's facts are fully determined by the reading copy, the
split plan, and the notes: the source identity, the declared scope,
the scoped total, and the exact range each unit covered with its page
anchors. Writing it by generation let totals diverge from the unit
table in past trials, so the statement is generated, not written
(proposal R-P05 of review run 20261118-12). The reader still writes
the completion report around it and judges anything the statement
flags (gaps, overlaps, units without notes).

Usage: make_coverage_statement.py READING_COPY SPLIT_PLAN NOTES
Prints the statement to stdout.
"""
import hashlib
import re
import sys

copy_path, plan_path, notes_path = sys.argv[1], sys.argv[2], sys.argv[3]
data = open(copy_path, "rb").read()
lines = data.decode("utf-8").split("\n")
plan = open(plan_path, encoding="utf-8").read()
notes = open(notes_path, encoding="utf-8").read()

anchors = []
for i, ln in enumerate(lines):
    m = re.match(r"^#{1,2} Page (\d+)$", ln)
    if m:
        anchors.append((int(m.group(1)), i + 1))

scope = "full read"
m = re.search(r"^-\s*scope:\s*(.+)$", plan, re.M)
if m:
    scope = m.group(1).strip()

units = []
for ln in plan.splitlines():
    m = re.match(r"^unit:\s*(.+?)\s*\|\s*pages:\s*(\d+)\s*-\s*(\d+)", ln)
    if m:
        units.append((m.group(1), int(m.group(2)), int(m.group(3))))

covered = []
for _, a, b in units:
    covered += list(range(a, b + 1))
total_pages = len(anchors)
span = f"{anchors[0][0]}-{anchors[-1][0]}" if anchors else "no page anchors"

print("# Coverage statement (generated)")
print()
print(f"- source: {copy_path} ({len(data)} bytes, md5 {hashlib.md5(data).hexdigest()})")
print(f"- declared scope: {scope}")
print(f"- copy total: {total_pages} pages (anchors {span}), {len(lines)} lines")
print()
print("| unit | pages | anchors present | notes entry |")
print("|---|---|---|---|")
for name, a, b in units:
    have = [p for p, _ in anchors if a <= p <= b]
    has_notes = bool(re.search(rf"^#{{1,3}}\s+{re.escape(name)}\s*$", notes, re.M))
    print(f"| {name} | {a}-{b} | {len(have)} of {b - a + 1} | {'yes' if has_notes else 'MISSING'} |")
print()
lo, hi = (anchors[0][0], anchors[-1][0]) if anchors else (0, -1)
sm = re.search(r"(\d+)\s*[-\u2013\u2014~](\d+)", scope)
if sm and "full" not in scope.lower():
    lo, hi = int(sm.group(1)), int(sm.group(2))
missing = sorted(set(range(lo, hi + 1)) - set(covered)) if anchors else []
dup = sorted({p for p in covered if covered.count(p) > 1})
print(f"- covered pages: {len(set(covered))}, gaps: {missing if missing else 'none'}, overlaps: {dup if dup else 'none'}")
