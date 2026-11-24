#!/usr/bin/env python3
"""Build a page-anchored plain-text reading copy from a PDF.

Runs pdftotext without -layout (the default extraction reads multi-column
pages in column sequence; -layout joins the columns line by line), splits
the output at the form feeds pdftotext emits per page, and writes each
page under a "# Page N" anchor line — the anchor form the worksheet
generators and the gate check consume.

Usage: make_reading_copy.py FILE.pdf OUT.md
"""
import subprocess
import sys

src, out = sys.argv[1], sys.argv[2]
r = subprocess.run(["pdftotext", src, "-"], capture_output=True, text=True)
if r.returncode != 0:
    print(f"pdftotext failed: {r.stderr.strip()}", file=sys.stderr)
    sys.exit(1)

pages = r.stdout.split("\f")
if pages and not pages[-1].strip():
    pages.pop()  # trailing form feed after the last page

blocks = []
for i, p in enumerate(pages, 1):
    blocks.append(f"# Page {i}\n{p.strip()}")
open(out, "w", encoding="utf-8").write("\n\n".join(blocks) + "\n")
print(f"pages={len(pages)} -> {out}")
