#!/usr/bin/env python3
"""Verify a masked reading copy: original search plus pattern re scan.

Two layers, both mechanical:

  1. Each user-supplied sensitive original is searched on text normalized
     with NFKC and stripped of whitespace and line breaks, as a substring
     match — a whole-token search silently returns zero hits in Japanese.
     Hits are reported per original with their pages.
  2. A pattern re scan over the whole copy, with no section excluded
     (a contact block often sits after the reference list, at the very
     end): phone numbers and email addresses carry a zero-hit
     expectation; amounts and dates are reported as counts only, unless
     --targets names them, because a legitimate report carries years and
     budgets that would fail every time and train a rubber stamp.

With --counts-only (the restricted path), the report carries counts and
locations only and never prints an original string or a matched string,
because the strings themselves would be a new route for the original to
reach the coordinating agent.

  3. A placeholder recount, from the delivered copy itself: the masking
     agent's own replacement counts are never accepted as verification,
     so this script counts placeholder occurrences by kind. The default
     pattern matches the bracketed kind_number form, halfwidth or
     fullwidth ([NAME_1], ［名前_1］); --placeholder REGEX overrides it,
     and the regex's first group is taken as the kind label.

Usage: verify_masking.py MASKED_COPY ORIGINALS.txt [--counts-only]
       [--targets phone,email,amount,date] [--placeholder REGEX]
Exit code 1 when an original is found, or a zero-expectation pattern
hits; 0 otherwise.
"""
import re
import sys
import unicodedata

counts_only = "--counts-only" in sys.argv
targets = {"phone", "email"}
placeholder_pat = r"[［\[]([^＿_\]］\n]+)[_＿]\d+[］\]]"
args = []
argv = sys.argv[1:]
i = 0
while i < len(argv):
    a = argv[i]
    if a == "--targets" and i + 1 < len(argv):
        targets = set(argv[i + 1].split(","))
        i += 2
    elif a.startswith("--targets="):
        targets = set(a.split("=", 1)[1].split(","))
        i += 1
    elif a == "--placeholder" and i + 1 < len(argv):
        placeholder_pat = argv[i + 1]
        i += 2
    elif a.startswith("--placeholder="):
        placeholder_pat = a.split("=", 1)[1]
        i += 1
    elif a.startswith("--"):
        i += 1
    else:
        args.append(a)
        i += 1

copy_path, orig_path = args[0], args[1]
raw = open(copy_path, encoding="utf-8").read()
originals = [l.strip() for l in open(orig_path, encoding="utf-8") if l.strip()]


def norm(s):
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"\s+", "", s)


# split the copy into page segments by its anchors
segments = []  # (page, raw_text)
cur_page, buf = None, []
for ln in raw.split("\n"):
    m = re.match(r"^#{1,2} Page (\d+)$", ln)
    if m:
        if buf:
            segments.append((cur_page, "\n".join(buf)))
        cur_page, buf = int(m.group(1)), []
    else:
        buf.append(ln)
if buf:
    segments.append((cur_page, "\n".join(buf)))
if not segments:
    segments = [(None, raw)]
norm_segments = [(p, norm(t)) for p, t in segments]

fail = False

# 1. originals -----------------------------------------------------------------
for idx, orig in enumerate(originals, 1):
    needle = norm(orig)
    pages = [p for p, t in norm_segments if needle and needle in t]
    label = f"original[{idx}]" if counts_only else f"original[{idx}] {orig!r}"
    if pages:
        fail = True
        print(f"HIT {label}: pages {pages}")
    else:
        print(f"ok  {label}: 0 hits")

# 2. pattern re scan -------------------------------------------------------------
PHONE = re.compile(r"0\d{9,10}")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
AMOUNT = re.compile(r"\d{1,3}(?:,\d{3})+円|\d+万円|\d+円")
DATE = re.compile(r"\d{4}年\d{1,2}月\d{1,2}日|\d{4}[-/]\d{1,2}[-/]\d{1,2}")


def scan(name, pat, strip_seps=False, zero_expected=False):
    global fail
    pages = []
    total = 0
    for p, t in norm_segments:
        text = re.sub(r"[-()]", "", t) if strip_seps else t
        n = len(pat.findall(text))
        if n:
            pages.append(p)
            total += n
    mark = ""
    if zero_expected and total:
        fail = True
        mark = "  <- zero expected"
    print(f"pattern {name}: {total} hits, pages {pages}{mark}")


scan("phone", PHONE, strip_seps=True, zero_expected="phone" in targets)
scan("email", EMAIL, zero_expected="email" in targets)
scan("amount", AMOUNT, zero_expected="amount" in targets)
scan("date", DATE, zero_expected="date" in targets)

# 3. placeholder recount ---------------------------------------------------------
PH = re.compile(placeholder_pat)
kind_counts = {}
kind_pages = {}
total_ph = 0
for p, t in segments:
    for m in PH.finditer(t):
        kind = m.group(1) if m.groups() else m.group(0)
        kind_counts[kind] = kind_counts.get(kind, 0) + 1
        kind_pages.setdefault(kind, set()).add(p)
        total_ph += 1
print(f"placeholders: {total_ph} total")
for kind in sorted(kind_counts):
    pages = sorted(x for x in kind_pages[kind] if x is not None)
    print(f"placeholder {kind}: {kind_counts[kind]} hits, pages {pages}")

sys.exit(1 if fail else 0)
