#!/usr/bin/env python3
"""Extract candidate personal names the replacement table may not cover.

Mechanical extraction only (proposal R-P05 of review run 20261118-12):
candidates are pulled from honorifics, role words, signature blocks,
and the neighbourhood of phone numbers, independently of whoever ran
the masking pass, because a candidate pass by the masking agent shares
that agent's blind spots. The script lists candidates with their line
numbers and the trigger that found them; whether each candidate is a
name to mask is the user's ruling, not the script's.

Usage: extract_name_candidates.py COPY.md
Output: one line per candidate: line N [kind] candidate
"""
import re
import sys

lines = open(sys.argv[1], encoding="utf-8").read().split("\n")
NAME = "[一-龯々]{2,4}"
found = {}


def add(cand, kind, lineno):
    cand = cand.strip()
    if cand and (cand, kind) not in found:
        found[(cand, kind)] = lineno


HONORIFIC = re.compile(rf"({NAME})(?:様|先生|氏|さん|君)")
ROLES = (
    "代表取締役|取締役|部長|課長|係長|主任|教授|准教授|講師|"
    "理事|院長|編集長|担当|責任者"
)
ROLE_AFTER = re.compile(rf"({NAME})\s*(?:{ROLES})")
ROLE_BEFORE = re.compile(rf"(?:{ROLES})\s*[：:]?\s*({NAME})")
PHONE = re.compile(r"(?:\d{2,4}-\d{2,4}-\d{4}|\d{10,11})")
NAME_TOKEN = re.compile(NAME)

for i, ln in enumerate(lines):
    for m in HONORIFIC.finditer(ln):
        add(m.group(1), "honorific", i + 1)
    for m in ROLE_AFTER.finditer(ln):
        add(m.group(1), "role-after", i + 1)
    for m in ROLE_BEFORE.finditer(ln):
        add(m.group(1), "role-before", i + 1)

phone_lines = [i for i, ln in enumerate(lines) if PHONE.search(ln)]
for i in phone_lines:
    for j in range(max(0, i - 2), min(len(lines), i + 3)):
        for m in NAME_TOKEN.finditer(lines[j]):
            add(m.group(0), "near-phone", j + 1)

for i, ln in enumerate(lines):
    if "署名" in ln or "記名" in ln:
        for j in range(i + 1, min(len(lines), i + 6)):
            m = NAME_TOKEN.search(lines[j])
            if m:
                add(m.group(0), "signature-block", j + 1)

for (cand, kind), lineno in sorted(found.items(), key=lambda kv: kv[1]):
    print(f"line {lineno} [{kind}] {cand}")
print(f"candidates: {len(found)}", file=sys.stderr)
