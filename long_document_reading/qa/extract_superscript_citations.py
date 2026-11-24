#!/usr/bin/env python3
"""Make an augmented reading copy of a PDF whose citations are superscript.

Plain-text extraction flattens superscript citation markers (AMA style)
into ordinary digits, where they can no longer be told apart from years,
counts and measurements. This tool rebuilds the reading copy from the
PDF's styled text spans instead: a span that the PDF engine marks as
superscripted and whose text is only digits, commas and ranges is a
citation marker, and is written into the copy as (N) tokens, one per
cited number, exactly where it sits. The result is a normal page-anchored
reading copy ("# Page N" lines) that the numbered-list worksheet
generator (correspondence_worksheet.py) consumes unchanged.

Approach and attribution: superscript detection uses PyMuPDF, whose
span dictionary carries a superscript flag (bit 0 of the span "flags",
detected by the MuPDF engine from the text's size and baseline shift) --
the same device the citation-extraction literature uses for this problem
(e.g. the superscript flag projected onto Docling blocks in a 2026
University of Twente thesis on citation extraction; GROBID's pdfalto
layer likewise recognises superscript style for reference markers).
PyMuPDF is licensed AGPL-3.0 (Artifex); it is used here as an external
preparation tool and is not redistributed with this skill. A
license-cleaner alternative measured on the same document -- a
pdfplumber (MIT) character-geometry rule, digit chars notably smaller
than and raised above the line's body text -- recovered 30 of 41 cited
numbers against PyMuPDF's 41 of 41, so the flag route is the default and
the geometry rule is the fallback where AGPL is not acceptable.

Measured on the validation document (a JAMA Network Open article, AMA
style, 41 references): superscript digit spans yielded exactly the 41
cited numbers, and spot-checked spans sat at genuine citation points in
the sentences. Known confounders: superscript affiliation numbers in an
author byline and superscript table-footnote letters (letters are
ignored here; only digit spans are rewritten).

List preparation: numbered journal reference lists are often typeset
flush-left, continuations included, which leaves the worksheet
generator's entry run no way to tell a continuation from the body text
that follows the list. This tool does not indent them: run
prepare_numbered_lists.py on this tool's output as the next step. That
tool owns list indenting as the single implementation (its region ends
after 800 lines), so the two cannot drift apart.

Usage: extract_superscript_citations.py INPUT.pdf OUT.md
Requires: pymupdf (pip install pymupdf).
"""
import re
import sys

import pymupdf

src, out = sys.argv[1], sys.argv[2]
MARKER = re.compile(r"^[0-9][0-9,\-–〜～ ]*[)）]?$")


def expand(tok):
    tok = tok.rstrip(")）")
    vals = []
    for part in tok.split(","):
        part = part.strip()
        m = re.fullmatch(r"(\d+)[-–〜～](\d+)", part)
        if m:
            vals += list(range(int(m.group(1)), int(m.group(2)) + 1))
        elif part.isdigit():
            vals.append(int(part))
    return vals


doc = pymupdf.open(src)
out_lines = []
n_marks = 0
for pno, page in enumerate(doc, 1):
    out_lines.append(f"# Page {pno}")
    d = page.get_text("dict")
    for block in d["blocks"]:
        for line in block.get("lines", []):
            buf = ""
            for span in line["spans"]:
                t = span["text"]
                if (span["flags"] & 1) and MARKER.match(t.strip()):
                    for v in expand(t.strip()):
                        buf += f"({v})"
                        n_marks += 1
                else:
                    buf += t
            if buf.strip():
                out_lines.append(buf.rstrip())
    out_lines.append("")

open(out, "w", encoding="utf-8").write("\n".join(out_lines))
print(f"pages={len(doc)} superscript citation numbers written={n_marks} -> {out}")
print("next step: run prepare_numbered_lists.py on the output to indent list continuations")

