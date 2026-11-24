#!/usr/bin/env python3
"""Build a citation-correspondence worksheet from a page-anchored Markdown copy.

Deterministic part only: enumerate (citing passage, list entry) pairs so the
reader can judge content match on one sheet, instead of checking number
continuity from memory. The judgement itself is left blank on the sheet.

List detection is shared with the gate check and the other tools
(qa/list_detect.py): a reference list starts at a line whose normalised
form is one of the list headings (参考文献, 引用文献, 文献, References,
Bibliography, Works Cited, plus any headings the split plan declares).
Its entry run accepts, in order: entries numbered
1..N at column 0 ("N. ...", the IEEE form "[N] ...", or the Japanese
journal forms "N) ..." / "N） ..."), blank lines, indented continuation lines, page
anchors, and flush-left lines that begin with a number other than the expected
next entry number (a wrapped citation fragment, such as the page numbers of a
folded entry). The first other flush-left line ends the run. A heading-like
line that does not become a list is reported as a candidate in the warning
block (dismiss a false candidate, such as a table-of-contents line, by
recording its line number in the split plan and passing --plan).

Sampling rule (fixed, no reader discretion):
  For each list, the sampling segment is the marked unit that contains the
  list: the preparer marks each unit that owns a reference list (a chapter,
  part, or section) with a "# Chapter ..." / "# Part ..." / "# Section ..."
  line in the reading copy, and the segment runs from that unit's marker to
  the next marker. When the copy carries no markers, the segment falls back
  to the legacy span from the end of the previous list (or the document
  start) to the next list's heading (or the document end) — a span that can
  reach into the next unit's body text and pair its citations with this list.
  Outside any list's entry run, collect citations of the form (N), （N）,
  or [N] (the IEEE surface form), including range and enumeration forms — (2–3),
  (2〜4), (2, 3), (1,3,5) — which are expanded to their individual numbers,
  and the Japanese single-parenthesis forms 6) / 7）. Citations whose
  number exceeds the list's size are kept and sampled too: an entry deleted
  from the list while the text still cites it is the classic offset, and
  dropping those citations would hide exactly that. Superscript citations
  (AMA) are rewritten into (N) tokens in the reading copy beforehand by
  extract_superscript_citations.py. Sample =
    - every occurrence of the segment's highest cited number (up to 6),
    - the first citation occurrence in the segment,
    - the occurrence nearest the segment's middle line,
    - up to 2 citations whose number exceeds the list's size.
  Each citing passage is shown as a window around the citation itself.
  Page anchors are "# Page N" lines; the "## Page N" form is also accepted.

Warnings: when no list, no page anchor, or no citation is detected, the
sheet carries a warning block and the script exits with code 2 instead of
reporting a clean empty result, because an empty sheet used to pass the
completion gate silently.

Flag: a sampled citation that sits after its list's entry run (line index
beyond the run's end) is marked 【要・章帰属確認】 on the sheet. Under the
legacy span a segment can hold the next chapter's body text, whose citations
do not belong to this list; even inside a marked unit, a citation after the
list can also be a legitimate post-list discussion of the same chapter. The flag
does not decide either way — it tells the reader to confirm the citation's
chapter attribution before judging the pair.

Usage: correspondence_worksheet.py READING_COPY.md [OUT.md] [--plan SPLIT_PLAN]
"""
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from list_detect import detect_numbered_lists, extra_headings_from_plan

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

# --- locate reference lists (shared detector: qa/list_detect.py) -------------
_extra_headings, _dismissed = (
    extra_headings_from_plan(plan_text) if plan_text else ([], set())
)

# --- chapter/section markers --------------------------------------------------
# A preparer who knows the document's structure marks each unit that owns a
# reference list with a "# Chapter ..." / "# Part ..." / "# Section ..." line
# in the reading copy. When markers exist, a list's sampling segment is the
# marked unit that contains the list, instead of the legacy span from the
# previous list to the next list's heading (which reaches into the next
# unit's body text and can pair its citations with this list).
MARKER = re.compile(r"^# (Chapter|Part|Section)\b")
markers = [i for i, ln in enumerate(lines) if MARKER.match(ln)]

lists, _candidates = detect_numbered_lists(lines, _extra_headings)
_candidates = [c for c in _candidates if c["line"] not in _dismissed]

in_list = [False] * n_lines
for L in lists:
    for i in range(L["heading"], L["end"] + 1):
        in_list[i] = True

# --- collect citations outside the lists -------------------------------------
# Citation surface forms: (N) parentheses (Vancouver and friends) and [N]
# square brackets (IEEE). Superscript markers (AMA) never reach this pattern
# as text; a preparer first rewrites them into (N) tokens in the reading
# copy with extract_superscript_citations.py (see its docstring).
CITE = re.compile(r"[（(](\d{1,3})[）)]|\[(\d{1,3})\]")
RANGE = re.compile(
    r"[（(](\d{1,3})\s*[–—\-〜～]\s*(\d{1,3})[）)]"
    r"|[（(](\d{1,3})\s*[,、]\s*(\d{1,3})[）)]"
)
ENUM = re.compile(r"[（(](\d{1,3}(?:\s*[,、]\s*\d{1,3}){2,})[）)]")
SINGLE = re.compile(r"(?<![\d\(\[、,])(\d{1,3})[)）](?!\d)")
citations = []  # (line_idx, number, char_pos)
for i, ln in enumerate(lines):
    if in_list[i]:
        continue
    spans = []
    for m in ENUM.finditer(ln):
        for tok in re.split(r"[,、]", m.group(1)):
            citations.append((i, int(tok.strip()), m.start()))
        spans.append(m.span())
    for m in RANGE.finditer(ln):
        a, b = int(m.group(1) or m.group(3)), int(m.group(2) or m.group(4))
        if a <= b and b - a <= 20:
            for num in range(a, b + 1):
                citations.append((i, num, m.start()))
            spans.append(m.span())
    for m in CITE.finditer(ln):
        if any(s <= m.start() < e for s, e in spans):
            continue
        citations.append((i, int(m.group(1) or m.group(2)), m.start()))
        spans.append(m.span())
    for m in SINGLE.finditer(ln):
        if any(s <= m.start() < e for s, e in spans):
            continue
        citations.append((i, int(m.group(1)), m.start()))


def passage(idx, pos, back_lines=3, width=340):
    """Citing passage: up to `back_lines` preceding non-blank lines plus the
    citing line, cut to the last `width` characters ending at the citation,
    because the description of the cited item often sits in the lines just
    above the line that carries the number."""
    parts = []
    j = idx - 1
    while j >= 0 and len(parts) < back_lines:
        if lines[j].strip() and not in_list[j]:
            parts.append(lines[j].strip())
        j -= 1
    parts.reverse()
    parts.append(lines[idx].strip())
    s = " ".join(parts)
    end = s.find(lines[idx].strip()[:20])
    # cut so the citation itself is included: keep the tail up to the citation
    # that was sampled (the match nearest `pos`), not the line's first match,
    # because a line can carry several citations and each pair needs its own
    # window
    cite_at = None
    cand = (
        list(CITE.finditer(lines[idx]))
        + list(RANGE.finditer(lines[idx]))
        + list(ENUM.finditer(lines[idx]))
        + list(SINGLE.finditer(lines[idx]))
    )
    if cand:
        mm = min(cand, key=lambda x: abs(x.start() - pos))
        cite_at = len(" ".join(parts[:-1])) + (1 if len(parts) > 1 else 0) + mm.end()
    if cite_at is not None:
        lo = max(0, cite_at - width)
        s = ("…" if lo > 0 else "") + s[lo : cite_at + 12]
    elif len(s) > width:
        s = "…" + s[-width:]
    return s.strip()


# --- sample per list segment and emit the worksheet ---------------------------
rows_out = []
rows_out.append("# 対応確認ワークシート（自動生成）")
rows_out.append("")
rows_out.append("各行について、引用箇所の内容説明とリスト項目が指す論文が一致するかを判定し、")
rows_out.append("「判定」欄に 合／否 と根拠を1行で記録すること。否 があれば完了報告で解決すること。")
rows_out.append("【要・章帰属確認】の付いた引用は、そのリストの末尾より後ろにある。次章の本文の引用が")
rows_out.append("紛れている場合があるので、判定の前に引用の章帰属を確認すること。")
rows_out.append("")

for k, L in enumerate(lists):
    size = max(L["entries"])
    consecutive = sorted(L["entries"]) == list(range(1, size + 1))
    if markers:
        before = [m for m in markers if m <= L["heading"]]
        after = [m for m in markers if m > L["heading"]]
        seg_lo = before[-1] if before else 0
        seg_hi = after[0] - 1 if after else n_lines - 1
    else:
        seg_lo = lists[k - 1]["end"] + 1 if k > 0 else 0
        seg_hi = lists[k + 1]["heading"] - 1 if k + 1 < len(lists) else n_lines - 1
    seg_all = [(i, num, pos) for (i, num, pos) in citations if seg_lo <= i <= seg_hi]
    seg = [t for t in seg_all if t[1] <= size]
    over = [t for t in seg_all if t[1] > size]
    picked = {}  # (line, number) -> pos; keyed by number as well as line,
    # because one line can carry several citations and each needs its own pair
    if seg:
        top = max(num for _, num, _ in seg)
        for i, num, pos in [t for t in seg if t[1] == top][:6]:
            picked[(i, num)] = pos
        picked.setdefault((seg[0][0], seg[0][1]), seg[0][2])
        mid_line = (seg_lo + seg_hi) // 2
        near = min(seg, key=lambda t: abs(t[0] - mid_line))
        picked.setdefault((near[0], near[1]), near[2])
    n_over_picked = 0
    for i, num, pos in over:
        if n_over_picked >= 2:
            break
        if (i, num) not in picked:
            picked[(i, num)] = pos
            n_over_picked += 1
    rows = [((i, num), pos) for (i, num), pos in sorted(picked.items())][:10]
    rows_out.append(
        f"## リスト{k + 1}（見出し行 {L['heading'] + 1}、p{page_of[L['heading']]}、{size}件、"
        f"1..N連続: {'yes' if consecutive else 'NO'}、本文の引用 {len(seg_all)} 件中 {len(rows)} 件を抽出"
        f"（リスト範囲外 {len(over)} 件））"
    )
    rows_out.append("")
    if not rows:
        rows_out.append("（この区間にサンプル対象の引用なし）")
        rows_out.append("")
        continue
    for (i, num), pos in rows:
        cite = passage(i, pos)
        entry = L["entries"].get(num, "（その番号の項目がリストに無い）")
        if len(entry) > 200:
            entry = entry[:200] + "…"
        flag = " 【要・章帰属確認】" if i > L["end"] else ""
        rows_out.append(f"- 引用 p{page_of[i]}（行{i + 1}）({num}): {cite}{flag}")
        rows_out.append(f"  リスト項目 {num}: {entry}")
        rows_out.append("  判定: ")
    rows_out.append("")

warnings = []
if not lists:
    warnings.append("リストが検出されませんでした（見出しは 参考文献／引用文献／文献／References／Bibliography／Works Cited のいずれか、または分割計画で宣言した見出し）")
for c in _candidates:
    reason = (
        "見出しが検出集合に無い"
        if c["reason"] == "heading-not-in-set"
        else "見出しの下に項目が1件も読めなかった（見出しの語か項目形式が未対応の可能性）"
    )
    warnings.append(
        f"見出し候補がリストになりませんでした（行{c['line'] + 1}: {c['text'][:30]}、{reason}）。"
        "目次行などの誤候補は、分割計画に list_heading_dismissed で行番号を記録し --plan で渡せば取り消せる"
    )
if not any(p is not None for p in page_of):
    warnings.append("ページアンカー（# Page N）が検出されませんでした")
if not citations:
    warnings.append("本文の引用が検出されませんでした")
if warnings:
    block = ["【警告】生成が空振りしている可能性があります。このシートを合格として扱わないこと。"]
    block += [f"- {w}" for w in warnings]
    block.append("")
    rows_out[1:1] = block
    for w in warnings:
        print(f"警告: {w}", file=sys.stderr)

text = "\n".join(rows_out)
if out:
    open(out, "w", encoding="utf-8").write(text)
print(text)
sys.exit(2 if warnings else 0)
