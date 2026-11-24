#!/usr/bin/env python3
"""Print only the whitelisted container fields of a PDF, before any
sensitivity declaration is taken.

The skill's inventory step records page count, page size, the encryption
flag, and whether a sensitivity label is present — but the document's own
metadata text (title, author, subject) can carry proper names before any
declaration, so this tool never prints those fields. It reports the
label's presence as a flag only, never its text. Label key names are
looked for in the default output, in `pdfinfo -custom`, and in the XMP
element names of `pdfinfo -meta`, because the default output alone does
not surface them (fixed 2026-11-18, review run 20261118-12, R-07).

Usage: inventory_pdf.py FILE.pdf
"""
import os
import re
import subprocess
import sys

src = sys.argv[1]
out = subprocess.run(["pdfinfo", src], capture_output=True, text=True)
if out.returncode != 0:
    print(f"pdfinfo failed: {out.stderr.strip()}", file=sys.stderr)
    sys.exit(1)

fields = {}
for ln in out.stdout.splitlines():
    if ":" in ln:
        k, v = ln.split(":", 1)
        fields[k.strip()] = v.strip()

print(f"file: {src}")
print(f"bytes: {os.path.getsize(src)}")
print(f"pages: {fields.get('Pages', '?')}")
print(f"page_size: {fields.get('Page size', '?')}")
print(f"encrypted: {fields.get('Encrypted', '?')}")

# A sensitivity label (e.g. an MSIP label) does not appear in pdfinfo's
# default output: its key names surface only in the custom metadata
# (`pdfinfo -custom`), and a label carried in XMP appears only in
# `pdfinfo -meta`. Check all three, looking at key and element names
# only — never at values, which can carry the label's own text.
label_found = any('label' in k.lower() or 'sensitiv' in k.lower() for k in fields)

custom = subprocess.run(["pdfinfo", "-custom", src], capture_output=True, text=True)
if custom.returncode == 0:
    for ln in custom.stdout.splitlines():
        if ":" in ln:
            k = ln.split(":", 1)[0]
            if 'label' in k.lower() or 'sensitiv' in k.lower():
                label_found = True

meta = subprocess.run(["pdfinfo", "-meta", src], capture_output=True, text=True)
if meta.returncode == 0:
    for m in re.finditer(r"<\s*/?\s*([A-Za-z0-9_:\-\.]+)", meta.stdout):
        name = m.group(1).lower()
        if 'label' in name or 'sensitiv' in name or 'msip' in name:
            label_found = True
    for m in re.finditer(r"([A-Za-z0-9_:\-\.]+)\s*=", meta.stdout):
        name = m.group(1).lower()
        if 'label' in name or 'sensitiv' in name or 'msip' in name:
            label_found = True

print(f"sensitivity_label_present: {'yes' if label_found else 'no'}")
