#!/usr/bin/env python3
"""Build a citation-correspondence worksheet for MLA-style documents.

Companion to correspondence_worksheet.py (numbered lists),
correspondence_worksheet_ay.py (author-year lists) and
correspondence_worksheet_notes.py (Chicago notes). This one covers MLA
style (CSL style id: modern-language-association, the same definition
Zotero ships): in-text citations are (Surname page) with no comma and no
"p.", the author is often named in the sentence itself so the parenthesis
carries the page alone, and the list at the back is a single Works Cited
in surname order. The correspondence act is: citation -> Works Cited entry.

The Works Cited entries are NOT parsed by this script. Reference strings
are parsed by AnyStyle (https://anystyle.io), the established CRF
reference parser, into CSL-JSON; this script consumes that output.
Preparation:

  1. Segment the Works Cited into one entry per line (a new entry starts
     at a flush-left "Surname," line; wrapped lines are joined; a line
     starting with the repeated-author dash "_____" is its own entry,
     written with the previous entry's author repeated in place of the
     dash) -> entries.txt, in the document's own order.
  2. Parse it:  LANG=C.UTF-8 anystyle -f csl parse entries.txt OUTDIR
     (the UTF-8 locale matters; without it the CLI fails on non-ASCII).
  3. Run this script with the reading copy, the CSL-JSON file, and
     entries.txt (JSON records and text lines align 1:1, in order).

What remains here is the style-specific thin layer: the citation forms
(surname-form and page-only), the fixed sampling rule, and the sheet.
Page-only citations cannot be keyed mechanically -- resolving them runs
through the author named in the surrounding sentence, which is exactly
the reader's judgement this sheet exists to support, so they are shown
with a passage window and no pre-filled pair.

Sampling rule (fixed, no reader discretion):
  - every surname-form citation (up to 6 per surname), each paired with
    its Works Cited entry when the surname resolves;
  - up to 3 surname-form citations whose surname has no Works Cited entry;
  - page-only citations: the first, the middle one, the last, and up to 4
    more spread across the text (7 at most), shown with their passage
    windows; the first/middle/last are guaranteed to survive the cap.

Usage: correspondence_worksheet_mla.py READING_COPY.md ENTRIES.json ENTRIES.txt [OUT.md]
"""
import json
import re
import sys
import unicodedata
from collections import Counter

src, entries_json, entries_txt = sys.argv[1], sys.argv[2], sys.argv[3]
out = sys.argv[4] if len(sys.argv) > 4 else None
lines = open(src, encoding="utf-8").read().split("\n")
n_lines = len(lines)

records = json.load(open(entries_json, encoding="utf-8"))
entry_texts = [l for l in open(entries_txt, encoding="utf-8").read().split("\n") if l.strip()]
assert len(records) == len(entry_texts), "entries JSON/text count mismatch"


def fold(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip(" .'’")


def entry_family(rec):
    for k in ("author", "editor"):
        a = rec.get(k)
        if isinstance(a, list) and a and isinstance(a[0], dict):
            fam = a[0].get("family") or (a[0].get("literal", "").split(",")[0])
            if fam:
                return fam
    return ""


entries = []  # (family_fold, display_text)
for rec, txt in zip(records, entry_texts):
    entries.append((fold(entry_family(rec)), txt))
by_family = {}
for idx, (fam, _) in enumerate(entries):
    if fam:
        by_family.setdefault(fam, []).append(idx)

# --- page anchors -----------------------------------------------------------
page_of = []
cur = None
for ln in lines:
    m = re.match(r"^#{1,2} Page (\d+)$", ln)
    if m:
        cur = int(m.group(1))
    page_of.append(cur)

# --- locate Works Cited -------------------------------------------------------
wc_head = None
for i, ln in enumerate(lines):
    if ln.replace(" ", "").strip().lower() == "workscited":
        wc_head = i
        break
body_end = (wc_head - 1) if wc_head is not None else n_lines - 1

# --- citation extraction ------------------------------------------------------
SUR = r"[A-ZÀ-Þ][\w\u0300-\u036fÀ-ÿ'’.-]*"
SURN_FORM = re.compile(
    rf"\(\s*(?:see\s+|cf\.\s*)?({SUR})(?:\s+(?:and|&)\s+{SUR})?(?:\s*,?\s*[“\"][^“”\"]{{1,60}}[”\"])?\s+(\d{{1,3}}(?:[-–]\d{{1,3}})?)\s*\)"
)
PAGE_ONLY = re.compile(r"\(\s*(\d{1,3}(?:[-–]\d{1,3})?)\s*\)")

surname_cites = []  # (line, surname, pages, raw)
page_cites = []  # (line, pages)
for i in range(0, body_end + 1):
    ln = lines[i]
    spans = []
    for m in SURN_FORM.finditer(ln):
        surname_cites.append((i, m.group(1), m.group(2), m.group(0)))
        spans.append(m.span())
    for m in PAGE_ONLY.finditer(ln):
        if any(s <= m.start() < e for s, e in spans):
            continue
        page_cites.append((i, m.group(1)))


def passage(i, lo_bound=0):
    lo = max(lo_bound, i - 1)
    hi = min(body_end, i + 1)
    txt = " ".join(x.strip() for x in lines[lo : hi + 1] if x.strip() and not x.startswith("# Page"))
    return txt[:360] + ("…" if len(txt) > 360 else "")


# --- build the sheet ----------------------------------------------------------
sheet = []
sheet.append("# 対応確認ワークシート（MLA方式）")
sheet.append("")
sheet.append(f"- 読みコピー: {src}")
sheet.append(
    "- 方式の定義は CSL の modern-language-association（Zotero が配布するのと同じスタイル定義）に従う。"
    "Works Cited 項目の著者・タイトルの切り分けは AnyStyle（参考文献パーサー）の出力を使っている。"
)
sheet.append(
    "- 判定は各対について、引用が指す内容（引用文・言及内容）と Works Cited 項目の文献が合うかで下す。"
    "ページだけの引用は、文中で名指しされた著者と合わせて解決する（MLA の通常の形）。"
)
sheet.append("")
sheet.append(
    f"## 全体（Works Cited {len(entries)}件、姓入り引用 {len(surname_cites)}件、ページのみ引用 {len(page_cites)}件）"
)

fam_counts = Counter(fold(s) for _, s, _, _ in surname_cites)
matched = [c for c in surname_cites if fold(c[1]) in by_family]
unmatched = [c for c in surname_cites if fold(c[1]) not in by_family]

picks = []
per_fam = Counter()
for c in matched:
    if per_fam[fold(c[1])] < 6:
        picks.append(c)
        per_fam[fold(c[1])] += 1
picks += unmatched[:3]
for i, surname, pages, raw in picks:
    idxs = by_family.get(fold(surname), [])
    sheet.append(f"- 引用 p{page_of[i]}（行{i + 1}）{raw}: {passage(i)}")
    if idxs:
        text = entries[idxs[0]][1]
        if len(text) > 300:
            text = text[:300] + "…"
        extra = f"（同姓{len(idxs)}件。タイトルで判別）" if len(idxs) > 1 else ""
        sheet.append(f"  Works Cited項目{extra}: {text}")
    else:
        sheet.append(f"  Works Cited項目: （対応なし: {surname}）")
    sheet.append("  判定（合／否／保留）: ／根拠: ")
sheet.append("")

ppicks = []
if page_cites:
    idxs = {0, len(page_cites) // 2, len(page_cites) - 1}
    step = max(1, len(page_cites) // 6)
    idxs.update(range(0, len(page_cites), step))
    base = sorted(idxs)
    if len(base) > 7:
        # cap the sample without dropping the guaranteed first/middle/last:
        # truncating the sorted set used to cut the last citation exactly
        # when the count was large
        keep = {0, len(page_cites) // 2, len(page_cites) - 1}
        rest = [j for j in base if j not in keep]
        base = sorted(keep | set(rest[: 7 - len(keep)]))
    ppicks = [page_cites[j] for j in base]
sheet.append(
    f"## ページのみの引用（文中で名指しされた著者で解決する。全 {len(page_cites)} 件中 {len(ppicks)} 件を抽出）"
)
for i, pages in ppicks:
    sheet.append(f"- 引用 p{page_of[i]}（行{i + 1}）({pages}): {passage(i)}")
    sheet.append("  Works Cited項目: （文中の著者名で引く）")
    sheet.append("  判定（合／否／保留）: ／根拠: ")
sheet.append("")

silent = [entries[i][1] for fam, idxs in by_family.items() if fam not in fam_counts for i in idxs]
sheet.append(
    f"（参考）姓入り引用に一度も現れない Works Cited 項目: {len(silent)}件"
    "（ページのみの引用で引かれている場合がある。情報としてのみ示す）"
)
sheet.append("")

warnings = []
if not entries:
    warnings.append("Works Cited 項目が 0 件です（entries の入力を確認すること）")
if not surname_cites and not page_cites:
    warnings.append("本文の引用が検出されませんでした")
if not any(p is not None for p in page_of):
    warnings.append("ページアンカーが検出されませんでした")
if warnings:
    block = ["【警告】生成が空振りしている可能性があります。このシートを合格として扱わないこと。"]
    block += [f"- {w}" for w in warnings]
    block.append("")
    sheet[2:2] = block
    for w in warnings:
        print(f"警告: {w}", file=sys.stderr)

result = "\n".join(sheet)
if out:
    open(out, "w", encoding="utf-8").write(result)
else:
    print(result)
sys.exit(2 if warnings else 0)
