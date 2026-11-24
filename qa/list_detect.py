#!/usr/bin/env python3
"""Shared reference-list detection for the long_document_reading tools.

One detector, used by the worksheet generators, the list preparer, and
the completion-gate check, so the four tools cannot drift apart in what
they count as a list (review run 20261118-12, R-09; cross-checked in run
20261118-13). Before this module, each tool carried its own copy of the
fixed heading set {"参考文献", "引用文献", "References", "REFERENCES"} and
its own entry pattern, and a list whose heading or entry form fell
outside the set was dropped silently by every tool at once — the gate
compared two outputs of the same detector and could never see the loss.

Heading matching is by whole-line equality after normalisation: strip
whitespace (including full-width spaces and spaces between characters),
'#' markers, emphasis markers, a leading chapter number ("5. "), and a
trailing colon, and fold Latin case. This is the tolerant comparison the
MLA and notes generators already used in miniature.

Default headings cover the house's main field, Japanese journals
(decision 4 of run 20261118-12): 参考文献, 引用文献, 文献, References,
Bibliography, Works Cited. A work folder can declare additional
headings once, in the split plan ("- list_headings: Sources, ..."), and
every tool reads them from there (generators take --plan PATH; the gate
already receives the plan), instead of each tool being handed the same
value separately.

Entry forms for numbered lists: "N. ...", "[N] ...", "N) ..." and
"N） ..." (the closing parenthesis may be half- or full-width, and the
space after a full-width parenthesis is optional, because Japanese
entries commonly run on without one).

Candidate headings: a line whose normalised form is in the wider
candidate vocabulary (or ends with 文献） but which did not become a list
— because its heading is outside the active set, or because no entry
could be read under it — is reported as a candidate, so the failure is
named instead of silent. A candidate can be dismissed on the record by
naming its line number in the split plan ("- list_heading_dismissed:
123, 456"), for table-of-contents lines and the like.
"""
import re
import unicodedata

DEFAULT_HEADINGS = {
    "参考文献",
    "引用文献",
    "文献",
    "references",
    "bibliography",
    "workscited",
}

# Wider vocabulary used only to *notice* a heading-like line that the
# active set missed; a candidate never becomes a list by itself.
CANDIDATE_HEADINGS = DEFAULT_HEADINGS | {
    "引用・参考文献",
    "参考文献リスト",
    "文献リスト",
    "参考資料",
    "引用",
    "referencesandnotes",
    "sources",
    "furtherreading",
    "literaturecited",
    "notesandreferences",
}

_LEADING_NUM = re.compile(r"^\d{1,3}[.．、:：]\s*")
_SPACES = re.compile(r"[\s　]+")


def normalize_heading(line):
    """Normalise a line for whole-line heading comparison."""
    s = line.strip().strip("#").strip()
    s = s.strip("*").strip()
    s = _LEADING_NUM.sub("", s)
    s = s.rstrip(":：").strip()
    s = _SPACES.sub("", s)
    return unicodedata.normalize("NFKC", s).lower()


def is_candidate_heading(line):
    n = normalize_heading(line)
    if not n or len(n) > 30:
        return False
    return n in CANDIDATE_HEADINGS or n.endswith("文献")


ENTRY = re.compile(
    r"^(?:(\d{1,3})\.|\[(\d{1,3})\]|(\d{1,3})\)|(\d{1,3})）)\s*(.*\S)\s*$"
)
ANCHOR = re.compile(r"^#{1,2} Page \d+$")


def entry_number(match):
    for g in match.groups()[:4]:
        if g is not None:
            return int(g)
    return None


def detect_numbered_lists(lines, extra_headings=()):
    """Detect numbered lists. Returns (lists, candidates).

    lists: [{heading (line idx), start, end, entries {n: text}}]
    candidates: [{line (idx), text, reason}] — heading-like lines that
    did not become a list, with the reason ("heading-not-in-set" or
    "no-entries-read").
    """
    active = {normalize_heading(h) for h in DEFAULT_HEADINGS}
    active |= {normalize_heading(h) for h in extra_headings}
    n = len(lines)
    lists = []
    candidates = []
    heading_idx = []
    for i, ln in enumerate(lines):
        nh = normalize_heading(ln)
        if nh in active:
            heading_idx.append(i)
        elif is_candidate_heading(ln):
            candidates.append({"line": i, "text": ln.strip(), "reason": "heading-not-in-set"})
    for h in heading_idx:
        entries = {}
        expect = 1
        last = None
        end = h
        i = h + 1
        while i < n:
            ln = lines[i]
            m = ENTRY.match(ln)
            if m and entry_number(m) == expect:
                last = expect
                entries[last] = m.group(5).strip()
                expect += 1
                end = i
            elif ANCHOR.match(ln) or ln.strip() == "":
                pass
            elif last is not None and (
                ln.startswith((" ", "\t"))
                or ln.startswith("　")
                or re.match(r"^\d+\.", ln)
                or re.match(r"^\[\d+\]", ln)
                or re.match(r"^\d+[)）]", ln)
            ):
                entries[last] += " " + ln.strip()
                end = i
            else:
                break
            i += 1
        if entries:
            lists.append({"heading": h, "start": h + 1, "end": end, "entries": entries})
        else:
            candidates.append(
                {"line": h, "text": lines[h].strip(), "reason": "no-entries-read"}
            )
    # A line that is not a heading but is immediately followed by a
    # numbered entry run (1., 2., ... in any entry form) is a heading
    # candidate the vocabulary missed: name it instead of dropping it.
    heading_set = set(heading_idx) | {L["heading"] for L in lists}
    for i in range(n - 1):
        if i in heading_set or not lines[i].strip():
            continue
        j = i + 1
        m1 = ENTRY.match(lines[j]) if j < n else None
        m2 = ENTRY.match(lines[j + 1]) if j + 1 < n else None
        if (
            m1 and entry_number(m1) == 1
            and m2 and entry_number(m2) == 2
            and not ENTRY.match(lines[i])
        ):
            candidates.append(
                {"line": i, "text": lines[i].strip(), "reason": "heading-not-in-set"}
            )
    candidates.sort(key=lambda c: c["line"])
    return lists, candidates


def extra_headings_from_plan(plan_text):
    """Read '- list_headings: A, B' and '- list_heading_dismissed: 1, 2'
    from a split plan. Returns (extra_headings, dismissed_line_numbers
    as 0-based indices)."""
    extra, dismissed = [], set()
    for ln in plan_text.splitlines():
        m = re.match(r"^-\s*list_headings:\s*(.+)$", ln.strip())
        if m:
            extra += [h.strip() for h in re.split(r"[,、]", m.group(1)) if h.strip()]
        m = re.match(r"^-\s*list_heading_dismissed:\s*(.+)$", ln.strip())
        if m:
            for tok in re.split(r"[,、\s]+", m.group(1)):
                if tok.isdigit():
                    dismissed.add(int(tok) - 1)
    return extra, dismissed
