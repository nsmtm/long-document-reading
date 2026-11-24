#!/usr/bin/env python3
"""Build a citation-correspondence worksheet for author-year documents.

Companion to correspondence_worksheet.py, which covers numbered reference
lists. In an author-year document the list entries carry no numbers; the
correspondence key is (first author's surname, year), with a letter suffix
(2014a) separating same-author same-year entries. Deterministic part only:
enumerate (citing passage, list entry) pairs on one sheet; the content
judgement is left blank for the reader.

List detection: a reference list starts at a line whose normalised form
(shared with the other tools, qa/list_detect.py) is one of the list
headings (参考文献, 引用文献, 文献, References, Bibliography, Works Cited,
plus any headings the split plan declares). An entry starts at a
flush-left line that opens with a surname (or an organisation name) and
carries a (YYYY) year; the entry run then accepts blank lines, indented
continuation lines, and page anchors, and ends at the first other flush-left
line.

Citations are collected only from the unit that owns the list (see the
marker rule in correspondence_worksheet.py; without markers, the segment is
the body span from the previous list's end to this list's heading, because
an author-year list sits at its chapter's end). Citation forms collected:
parenthetical (Surname, 2020), multi-key parentheticals split on ";",
two-author forms with & or and, et al. forms, and narrative Surname (2020).

Sampling rule (fixed, no reader discretion):
  - every occurrence of the unit's most frequently cited key (up to 6),
  - the first citation occurrence in the segment,
  - the occurrence nearest the segment's middle line,
  - up to 3 occurrences whose key has no entry in the list -- the author-year
    analogue of a numbering offset: a citation pointing at no entry is
    itself a finding candidate and is shown as such on the sheet.
Each citing passage is shown as a window around the citation itself.

Flag: a sampled citation that sits after its list's entry run is marked
【要・章帰属確認】, as in the numbered generator.

Japanese author-year citations （山田ら（2020）、（佐藤, 2019）) are NOT
supported: the key extraction covers Latin surnames only. When body lines
carry that shape, the sheet carries a warning block and the script exits
with code 2, so the gap is stated rather than silently producing an empty
or partial sheet. The same warning-and-exit applies when no list, no page
anchor, or no citation is detected at all.

Usage: correspondence_worksheet_ay.py READING_COPY.md [OUT.md] [--plan SPLIT_PLAN]
"""
import re
import sys
import unicodedata
from collections import Counter

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from list_detect import (
    DEFAULT_HEADINGS,
    extra_headings_from_plan,
    is_candidate_heading,
    normalize_heading,
)

_argv = sys.argv[1:]
plan_text = None
if "--plan" in _argv:
    _i = _argv.index("--plan")
    plan_text = open(_argv[_i + 1], encoding="utf-8").read()
    del _argv[_i : _i + 2]
src = _argv[0]
out = _argv[1] if len(_argv) > 1 else None
lines = open(src, encoding="utf-8").read().split("\n")
n_lines = len(lines)

# --- page anchors -----------------------------------------------------------
page_of = []
cur = None
for ln in lines:
    m = re.match(r"^#{1,2} Page (\d+)$", ln)
    if m:
        cur = int(m.group(1))
    page_of.append(cur)

# --- locate reference lists -------------------------------------------------
ANCHOR = re.compile(r"^#{1,2} Page \d+$")
_extra_headings, _dismissed = (
    extra_headings_from_plan(plan_text) if plan_text else ([], set())
)
_ACTIVE_HEADINGS = {normalize_heading(h) for h in DEFAULT_HEADINGS} | {
    normalize_heading(h) for h in _extra_headings
}
heading_idx = [
    i for i, ln in enumerate(lines) if normalize_heading(ln) in _ACTIVE_HEADINGS
]
_candidate_idx = [
    i
    for i, ln in enumerate(lines)
    if i not in heading_idx
    and i not in _dismissed
    and is_candidate_heading(ln)
]

YEAR = re.compile(r"\((\d{4}[a-z]?)[^)]*\)")  # (2010, 2016) / (1620/2005) -> first year
SURNAME_TOKEN = r"[A-ZÀ-Þ][\w\u0300-\u036fÀ-ÿ'’.-]*"  # incl. combining marks (Gla + caron)
PARTICLE = r"(?:[a-z]{1,4}\s+)?"  # de / van / von / der ... before a surname
ENTRY_A = re.compile(rf"^{PARTICLE}({SURNAME_TOKEN}),\s")  # Surname, I. (YYYY)
ENTRY_D = re.compile(r"^(.{2,60}?)\.\s*\(\d{4}")  # multi-word organisation. (YYYY)
YFRAG = r"(?:\d{4}[a-z]?|in press)"
ENTRY_B = re.compile(rf"^({SURNAME_TOKEN})\.\s*\({YFRAG}")  # OECD. (YYYY)
ENTRY_C = re.compile(rf"^({SURNAME_TOKEN})\s+\({YFRAG}")    # OECD (YYYY)


def entry_start(ln):
    """Return the surname if this flush-left line starts an entry, else None.

    The author-name comma form (Surname, I. ...) is accepted without a year
    on the first line: a long author list can push the (year) onto the
    second line, and requiring it here would end the run mid-list.
    """
    if ln[:1].isspace() or not ln.strip():
        return None
    m = ENTRY_A.match(ln)
    if m:
        return m.group(1)
    if YEAR.search(ln) or "(in press)" in ln:
        sur = _entry_surname(ln)
        if sur:
            return sur
        m = ENTRY_D.match(ln)
        if m:
            return m.group(1).split()[0].strip(",")
    return None


def _entry_surname(ln):
    for pat in (ENTRY_A, ENTRY_B, ENTRY_C):
        m = pat.match(ln)
        if m:
            return m.group(1)
    return None


def fold(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip(".'’")


lists = []
for h in heading_idx:
    entries = []  # [start_line, end_line, surname, year]
    cur_entry = None
    j = h + 1
    last = h
    while j < n_lines:
        ln = lines[j]
        es = entry_start(ln)
        if es:
            if cur_entry:
                entries.append(cur_entry)
            cur_entry = [j, j, es]
            last = j
        elif ANCHOR.match(ln) or not ln.strip() or ln[:1].isspace():
            if cur_entry:
                cur_entry[1] = j
            last = j
        else:
            break
        j += 1
    if cur_entry:
        entries.append(cur_entry)
    if entries:
        by_key = {}
        for st, en, sur in entries:
            text = " ".join(lines[st : en + 1]).strip()
            ym = YEAR.search(text)
            yr = ym.group(1) if ym else ("inpress" if "(in press)" in text else "")
            by_key.setdefault((fold(sur), yr), (st, text))
        lists.append({"heading": h, "end": last, "entries": entries, "by_key": by_key})

in_list = [False] * n_lines
for L in lists:
    for i in range(L["heading"], L["end"] + 1):
        in_list[i] = True

# --- chapter/section markers ------------------------------------------------
MARKER = re.compile(r"^# (Chapter|Part|Section)\b")
markers = [i for i, ln in enumerate(lines) if MARKER.match(ln)]

# --- citation extraction ----------------------------------------------------
PAREN_GROUP = re.compile(r"\(([^()]{1,300})\)")
PAREN_PART = re.compile(
    rf"^\s*{PARTICLE}({SURNAME_TOKEN})(?:\s+(?:&|and)\s+{PARTICLE}{SURNAME_TOKEN})?"
    rf"(?:\s*,?\s*et al\.)?\s*,\s*(\d{{4}}[a-z]?|in press)\s*(?:,.*)?$"
)
NARRATIVE = re.compile(
    rf"{PARTICLE}({SURNAME_TOKEN})(?:\s+(?:&|and)\s+{PARTICLE}{SURNAME_TOKEN})?"
    rf"(?:\s+et al\.)?\s*\((\d{{4}}[a-z]?|in press)\)"
)


def citations_on_line(i):
    """Return [(key, raw)] for each citation found on body line i."""
    ln = lines[i]
    found = []
    spans = []
    for g in PAREN_GROUP.finditer(ln):
        for part in g.group(1).split(";"):
            m = PAREN_PART.match(part)
            if m:
                found.append(((fold(m.group(1)), m.group(2).replace(" ", "")), g.group(0)))
                spans.append(g.span())
    for m in NARRATIVE.finditer(ln):
        if any(s <= m.start() < e for s, e in spans):
            continue
        found.append(((fold(m.group(1)), m.group(2).replace(" ", "")), m.group(0)))
    return found


# --- Japanese author-year detection (unsupported; warn, do not stay silent) --
JP_NARRATIVE = re.compile(r"[\u4e00-\u9fff]{1,10}(?:ら|他|・[\u4e00-\u9fff]{1,10})?\s*[（(]\s*\d{4}")
JP_PAREN = re.compile(r"[（(]\s*[\u4e00-\u9fff]{1,10}(?:ら|他)?\s*[,、]\s*\d{4}")
jp_hits = 0
for i, ln in enumerate(lines):
    if in_list[i]:
        continue
    if JP_NARRATIVE.search(ln) or JP_PAREN.search(ln):
        jp_hits += 1

# --- build the sheet --------------------------------------------------------
total_occ = 0
sheet = []
sheet.append("# 対応確認ワークシート（著者–年方式）")
sheet.append("")
sheet.append(f"- 読みコピー: {src}")
sheet.append(
    "- 判定は各対について、引用箇所の述べる内容（主題・方法・著者）と、鍵（第1著者・年）で引いたリスト項目の内容が合うかで下す。"
    "鍵がリストに無い引用は「対応キーなし」として示す（項目の欠落・年の誤り・別章の引用の候補）。"
)
sheet.append("")

for k, L in enumerate(lists):
    if markers:
        before = [m for m in markers if m <= L["heading"]]
        after = [m for m in markers if m > L["heading"]]
        seg_lo = before[-1] if before else 0
        seg_hi = after[0] - 1 if after else n_lines - 1
    else:
        seg_lo = lists[k - 1]["end"] + 1 if k > 0 else 0
        seg_hi = L["heading"] - 1
    occ = []  # (line, key, raw)
    for i in range(seg_lo, seg_hi + 1):
        if in_list[i]:
            continue
        for key, raw in citations_on_line(i):
            occ.append((i, key, raw))
    total_occ += len(occ)
    counts = Counter(key for _, key, _ in occ)
    sheet.append(
        f"## リスト{k + 1}（見出し行 {L['heading'] + 1}、p{page_of[L['heading']]}、"
        f"{len(L['entries'])}件、本文の引用 {len(occ)}件・鍵 {len(counts)}種）"
    )
    picks = []
    if occ:
        top_key = min(
            counts,
            key=lambda kk: (-counts[kk], next(i for i, k2, _ in occ if k2 == kk)),
        )
        picks += [o for o in occ if o[1] == top_key][:6]
        picks.append(occ[0])
        mid = (seg_lo + seg_hi) // 2
        picks.append(min(occ, key=lambda o: abs(o[0] - mid)))
        picks += [o for o in occ if o[1] not in L["by_key"]][:3]
    seen = set()
    uniq = []
    for o in picks:
        if (o[0], o[1]) not in seen:
            seen.add((o[0], o[1]))
            uniq.append(o)
    if not uniq:
        sheet.append("（この区間に本文引用なし）")
    for i, key, raw in uniq:
        flag = " 【要・章帰属確認】" if i > L["end"] else ""
        lo = max(seg_lo, i - 1)
        hi = min(seg_hi, i + 1)
        passage = " ".join(x.strip() for x in lines[lo : hi + 1] if x.strip())
        if len(passage) > 360:
            passage = passage[:360] + "…"
        sheet.append(f"- 引用 p{page_of[i]}（行{i + 1}）{raw}{flag}: {passage}")
        hit = L["by_key"].get(key)
        if hit:
            text = hit[1]
            if len(text) > 300:
                text = text[:300] + "…"
            sheet.append(f"  リスト項目 {key[0]} ({key[1]}): {text}")
        else:
            sheet.append(f"  リスト項目: （対応キーなし: {key[0]} ({key[1]})）")
        sheet.append("  判定（合／否／保留）: ／根拠: ")
    sheet.append("")

warnings = []
if not lists:
    warnings.append("リストが検出されませんでした（見出しは 参考文献／引用文献／文献／References／Bibliography／Works Cited のいずれか、または分割計画で宣言した見出し）")
_list_headings = {L["heading"] for L in lists}
for i in heading_idx:
    if i not in _list_headings and i not in _dismissed:
        warnings.append(
            f"見出し候補がリストになりませんでした（行{i + 1}: {lines[i].strip()[:30]}、見出しの下に項目が1件も読めなかった）。"
            "目次行などの誤候補は、分割計画に list_heading_dismissed で行番号を記録し --plan で渡せば取り消せる"
        )
for i in _candidate_idx:
    warnings.append(
        f"見出し候補がリストになりませんでした（行{i + 1}: {lines[i].strip()[:30]}、見出しが検出集合に無い）。"
        "目次行などの誤候補は、分割計画に list_heading_dismissed で行番号を記録し --plan で渡せば取り消せる"
    )
if not any(p is not None for p in page_of):
    warnings.append("ページアンカー（# Page N）が検出されませんでした")
if total_occ == 0 and jp_hits == 0:
    warnings.append("本文の引用が検出されませんでした")
if jp_hits:
    warnings.append(
        f"日本語の著者–年引用らしい箇所が {jp_hits} 行あります。この生成器は日本語の著者–年方式に未対応で、それらの引用はシートに載りません"
    )
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
