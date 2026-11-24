#!/usr/bin/env python3
"""Restore page anchors in a copy that keeps its printed folio numbers.

Deterministic restoration (proposal R-P05 of review run 20261118-12):
a line consisting solely of a folio number, where the folios form a
complete consecutive sequence, is replaced by a "# Page N" anchor
line. The result is trustworthy only after the sequence check passes;
when the sequence has a gap, a repeat, or goes backwards, the script
reports it and exits 2 without writing output, because a partial
restoration would silently shift every later citation.

Usage: restore_page_anchors.py COPY.md [OUT.md] [--start N]
  --start N: the expected first folio (default: the first folio found)
"""
import re
import sys

argv = [a for a in sys.argv[1:] if not a.startswith("--")]
start = None
raw = sys.argv[1:]
for i, a in enumerate(raw):
    if a == "--start" and i + 1 < len(raw):
        start = int(raw[i + 1])
    elif a.startswith("--start="):
        start = int(a.split("=", 1)[1])

src = argv[0]
out = argv[1] if len(argv) > 1 else src
lines = open(src, encoding="utf-8").read().split("\n")

FOLIO = re.compile(r"^\s*(\d{1,4})\s*$")
found = [(i, int(m.group(1))) for i, ln in enumerate(lines) if (m := FOLIO.match(ln))]
if not found:
    print("no folio-only lines found; nothing to restore", file=sys.stderr)
    sys.exit(2)
first = start if start is not None else found[0][1]
expect = first
problems = []
for i, v in found:
    if v != expect:
        problems.append(f"line {i + 1}: folio {v}, expected {expect}")
    expect = v + 1
if problems:
    for p in problems[:10]:
        print(f"sequence problem: {p}", file=sys.stderr)
    sys.exit(2)

folio_lines = {i for i, _ in found}
result = []
for i, ln in enumerate(lines):
    if i in folio_lines:
        result.append(f"# Page {int(ln.strip())}")
    else:
        result.append(ln)
open(out, "w", encoding="utf-8").write("\n".join(result))
print(f"anchors restored: {len(found)} (folios {found[0][1]}..{found[-1][1]}) -> {out}")
