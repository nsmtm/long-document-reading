#!/usr/bin/env python3
"""Build a citation-correspondence worksheet for notes-bibliography documents.

Companion to correspondence_worksheet.py (numbered lists) and
correspondence_worksheet_ay.py (author-year lists). This one covers the
Chicago notes-bibliography style (CSL style id: chicago-notes-bibliography,
the same definition Zotero ships): the body carries numbered notes, the
notes themselves cite in shortened form (surname + short title + pages),
and the full records sit in a single Bibliography at the back. The
correspondence act is: note segment -> bibliography entry.

The bibliography entries are NOT parsed by this script. Reference strings
are parsed by AnyStyle (https://anystyle.io), the established CRF reference
parser, into CSL-JSON; this script consumes that output. Preparation:

  1. Segment the bibliography into one entry per line (a new entry starts
     at a flush-left "Surname," line; wrapped lines are joined) ->
     entries.txt, in the document's own order. A line starting with the
     3-em dash (---, the Chicago repeated-author mark) is its own entry:
     write it as a separate line with the previous entry's author repeated
     in place of the dash, so the parser sees the author.
  2. Parse it:  LANG=C.UTF-8 anystyle -f csl parse entries.txt OUTDIR
     (the UTF-8 locale matters; without it the CLI fails on non-ASCII).
  3. Run this script with the reading copy, the CSL-JSON file, and
     entries.txt (JSON records and text lines align 1:1, in order).

What remains here is the style-specific thin layer: locating the Notes
section (its heading, with note numbering restarting per chapter, which is
also how the sheet's units are cut), splitting notes into citation
segments, extracting the short-form key (surname + short title), and the
fixed sampling rule. The content judgement is left blank for the reader.

Sampling rule (fixed, no reader discretion), per notes unit:
  - the unit's first citation segment,
  - the segment in the note nearest the unit's middle,
  - every segment citing the unit's most frequently cited surname (up to 6),
  - up to 3 segments with no bibliography match -- a short-form citation
    that resolves to no entry is this style's analogue of a numbering
    offset, and is shown as a finding candidate. Segments citing archives
    by abbreviation (all-caps tokens, shelfmarks) are counted separately:
    they legitimately resolve against the archives list, not the
    bibliography of published works, in many books.

Usage: correspondence_worksheet_notes.py READING_COPY.md ENTRIES.json ENTRIES.txt [OUT.md]
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


def words(s):
    return [w for w in re.split(r"[^0-9a-zà-ÿ]+", fold(s)) if len(w) > 1]


STOP = {"the", "a", "an", "in", "of", "de", "la", "le", "les", "du", "des", "et", "and", "on", "for", "au", "aux", "un", "une"}


def title_words(s):
    return [w for w in words(s) if w not in STOP]


def title_score(tw, ew):
    """Length of the longest prefix of tw appearing as a contiguous run in ew."""
    if not tw or not ew:
        return 0
    for size in range(min(len(tw), len(ew)), 0, -1):
        run = tw[:size]
        for j in range(0, len(ew) - size + 1):
            if ew[j : j + size] == run:
                return size
    return 0


def entry_family(rec):
    for k in ("author", "editor"):
        a = rec.get(k)
        if isinstance(a, list) and a and isinstance(a[0], dict):
            fam = a[0].get("family") or (a[0].get("literal", "").split(",")[0])
            if fam:
                return fam
    return ""


entries = []  # (family_fold, title_words, display_text)
for rec, txt in zip(records, entry_texts):
    t = rec.get("title") or ""
    entries.append((fold(entry_family(rec)), title_words(t if isinstance(t, str) else ""), txt))
by_family = {}
for idx, (fam, _, _) in enumerate(entries):
    if fam:
        by_family.setdefault(fam, []).append(idx)


def match_entry(surname, title):
    """Return (entry_index, basis) or (None, reason).

    A present surname restricts the pool to that family's entries: a note
    naming an author who has no entry is itself the finding (the author may
    be a chapter author inside an edited volume listed under its editor).
    The whole-bibliography title search runs only for title-first segments
    that carry no surname at all.
    """
    tw = title_words(title) if title else []
    if surname:
        sf = fold(surname)
        keys = [sf] + [fold(w) for w in surname.split()]
        if " in " in surname:  # "Author in Editor, Title": entry sits under the editor
            keys.append(fold(surname.split(" in ")[-1]))
        cands = []
        for k in keys:
            if k in by_family:
                cands = by_family[k]
                break
        if not cands:
            return None, "姓がBibliographyに無い"
        if tw:
            best, best_score = None, 0
            for i in cands:
                sc = title_score(tw, entries[i][1])
                if sc > best_score:
                    best, best_score = i, sc
            if best is not None and best_score >= min(2, len(tw)):
                return best, "姓+短縮タイトル"
            return None, "同姓だがタイトルが合わない"
        if len(cands) == 1:
            return cands[0], "姓のみ（同姓1件）"
        return cands[0], f"姓のみ（同姓{len(cands)}件中1件目・要確認）"
    if tw:
        best, best_score = None, 0
        for i in range(len(entries)):
            sc = title_score(tw, entries[i][1])
            if sc > best_score:
                best, best_score = i, sc
        if best is not None and best_score >= 2:
            return best, "タイトルのみ"
    return None, "対応なし"


# --- page anchors -----------------------------------------------------------
page_of = []
cur = None
for ln in lines:
    m = re.match(r"^#{1,2} Page (\d+)$", ln)
    if m:
        cur = int(m.group(1))
    page_of.append(cur)

# --- locate the Notes section and the Bibliography --------------------------
NOTE_START = re.compile(r"^\s{0,4}(\d{1,3})\.\s+\S")


def despaced(ln):
    return ln.replace(" ", "").replace("　", "").strip().lower()


notes_head = None
for i, ln in enumerate(lines):
    if despaced(ln) == "notes":
        if any(NOTE_START.match(x) for x in lines[i + 1 : i + 21]):
            notes_head = i
            break
if notes_head is None:
    print("警告: Notes 見出し（番号つき注の続くもの）が検出されませんでした", file=sys.stderr)
    sys.exit(2)
if not any(p is not None for p in page_of):
    print("警告: ページアンカーが検出されませんでした", file=sys.stderr)
    sys.exit(2)
bib_head = None
for i in range(notes_head + 1, n_lines):
    if despaced(lines[i]) == "bibliography":
        bib_head = i
        break
notes_end = (bib_head - 1) if bib_head is not None else n_lines - 1

# --- segment the notes ------------------------------------------------------
notes = []  # (start_line, number, text)
cur_note = None
for i in range(notes_head, notes_end + 1):
    m = NOTE_START.match(lines[i])
    if m:
        if cur_note:
            notes.append(cur_note)
        cur_note = [i, int(m.group(1)), lines[i].strip()]
    elif cur_note and lines[i].strip() and not re.match(r"^#{1,2} Page", lines[i]):
        cur_note[2] += " " + lines[i].strip()
if cur_note:
    notes.append(cur_note)
if not notes:
    print("警告: 注が1件も切り分けられませんでした", file=sys.stderr)
    sys.exit(2)

units = []
for nt in notes:
    if nt[1] == 1 or not units:
        units.append([])
    units[-1].append(nt)

# --- citation segments inside a note ----------------------------------------
LEAD = re.compile(
    r"^(see also|see,\s*e\.g\.,?|see e\.g\.,?|see|cf\.|e\.g\.,?|and|on\b.{0,70}?\bsee|for\b.{0,50}?\bsee|on)\s+",
    re.I,
)
ARCHIVE = re.compile(r"^[A-Z][A-Z0-9/]{1,}$")


def segments(note_text):
    body = re.sub(r"^\s*\d{1,3}\.\s+", "", note_text)
    body = re.sub(r"(\w)- (\w)", r"\1\2", body)  # line-break hyphenation
    out = []
    for seg in body.split(";"):
        seg = seg.strip().rstrip(".")
        if len(seg) < 6:
            continue
        s = LEAD.sub("", seg)
        surname, title = None, None
        qm = re.search(r"[“\"]([^“”\"]{3,70})[”\"]", s)
        if qm:
            title = qm.group(1)
        if s[:1] in "“\"":
            pass  # title-first citation
        else:
            m = re.match(r"^([^,]{2,42}),\s*(.*)$", s)
            if m and not re.search(r"\d", m.group(1)):
                surname = m.group(1).strip()
                rest = m.group(2)
                if not title:
                    rest = re.split(r",\s*\d", rest)[0]
                    if ". " in rest:  # full form: Firstname. Title ...
                        rest = rest.split(". ", 1)[1].split(". ")[0]
                    title = rest.strip(" ,") or None
        out.append((seg, surname, title))
    return out


# --- build the sheet --------------------------------------------------------
sheet = []
sheet.append("# 対応確認ワークシート（ノート方式：シカゴ・ノート版）")
sheet.append("")
sheet.append(f"- 読みコピー: {src}")
sheet.append(
    "- 方式の定義は CSL の chicago-notes-bibliography（Zotero が配布するのと同じスタイル定義）に従う。"
    "Bibliography 項目の著者・タイトルの切り分けは AnyStyle（参考文献パーサー）の出力を使っている。"
)
sheet.append(
    "- 判定は各対について、注の短縮引用（姓＋短縮タイトル＋ページ）が指す文献と、Bibliography 項目の内容が合うかで下す。"
    "対応の無い引用は「対応なし」として示す（短縮形の誤り・項目の欠落・別章の注の候補）。"
    "アーカイブ略号で引く引用は、刊行文献の Bibliography でなくアーカイブ一覧側で解決するのが通常なので、別枠で数える。"
)
sheet.append("")

for k, unit in enumerate(units):
    segs = []  # (note, seg_idx, raw, surname, title, match_idx, basis, archive?)
    for nt in unit:
        for si, (raw, surname, title) in enumerate(segments(nt[2])):
            if surname and ARCHIVE.match(surname.replace(" ", "")):
                segs.append((nt, si, raw, surname, title, None, "アーカイブ系", True))
                continue
            mi, basis = match_entry(surname, title)
            segs.append((nt, si, raw, surname, title, mi, basis, False))
    matched = [s for s in segs if s[5] is not None]
    unmatched = [s for s in segs if s[5] is None and not s[7]]
    arch = [s for s in segs if s[7]]
    fam_counts = Counter(s[3] for s in matched if s[3])
    lo_line, hi_line = unit[0][0], unit[-1][0]
    sheet.append(
        f"## 注セクション{k + 1}（p{page_of[lo_line]}開始、注{len(unit)}件、引用セグメント{len(segs)}件、"
        f"対応あり{len(matched)}件、対応なし{len(unmatched)}件、アーカイブ系{len(arch)}件）"
    )
    picks = []
    if segs:
        picks.append(segs[0])
        mid_note = unit[len(unit) // 2]
        mid_segs = [s for s in segs if s[0] is mid_note]
        if mid_segs:
            picks.append(mid_segs[0])
        if fam_counts:
            top = min(fam_counts, key=lambda f: (-fam_counts[f], next(s[0][0] for s in segs if s[3] == f)))
            picks += [s for s in segs if s[3] == top][:6]
        picks += unmatched[:3]
    seen, uniq = set(), []
    for s in picks:
        key = (s[0][0], s[1])
        if key not in seen:
            seen.add(key)
            uniq.append(s)
    if not uniq:
        sheet.append("（この区間に引用セグメントなし）")
    for nt, si, raw, surname, title, mi, basis, is_arch in uniq:
        seg_disp = raw if len(raw) <= 200 else raw[:200] + "…"
        sheet.append(f"- 注 p{page_of[nt[0]]}（行{nt[0] + 1}）注{nt[1]}: {seg_disp}")
        if is_arch:
            sheet.append("  Bibliography項目: （アーカイブ系の引用。アーカイブ一覧側で解決する）")
        elif mi is not None:
            text = entries[mi][2]
            if len(text) > 300:
                text = text[:300] + "…"
            sheet.append(f"  Bibliography項目（{basis}）: {text}")
        else:
            sheet.append(f"  Bibliography項目: （対応なし: {surname or ''} {title or ''}）")
        sheet.append("  判定（合／否／保留）: ／根拠: ")
    sheet.append("")

result = "\n".join(sheet)
if out:
    open(out, "w", encoding="utf-8").write(result)
else:
    print(result)
