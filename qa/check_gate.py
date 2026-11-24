#!/usr/bin/env python3
"""Mechanically check the completion gate's countable parts.

The gate's tiling, notes presence, anchor continuity, identity, and
list counts are mechanical; a reader's self-report of them is not
evidence, and when the coordinating agent is itself the reader there is
no second pair of eyes - this script is the verifier.

The gate follows the paths the skill body allows, not only the single
path PDF -> page-anchored copy, full scope, numbered lists (review run
20261118-12, decisions 1 and 4; R-04 to R-06, R-09, R-P06):

  1. Page anchors, when present, run consecutively with no gap or
     repeat (the run may start above 1, as a folio-restored copy can).
     A copy with no anchors passes this check only when the plan
     declares a heading basis (units given as sections).
  2. The split plan's unit ranges tile the declared scope with no gap
     and no overlap. The scope is read from the plan's scope line when
     it names page ranges, else the anchor span. Units split inside a
     page may overlap in pages only when their line ranges (lines:
     a-b, in reading-copy lines) tile without overlap.
  3. Every unit in the plan has a notes entry ("## <unit name>") whose
     section carries at least one content line; a missing or empty
     entry is an unread unit.
  4. The reading copy's identity (bytes, MD5) agrees with the identity
     recorded in the plan, when the plan records one.
  5. When the plan's correspondence ruling stands, a worksheet is
     required: it must exist, carry no warning block, list at least one
     list, have a verdict (and, where the sheet asks for one, a reason)
     recorded for every sampled pair, and its per-list entry counts
     must agree with the counts detected in the reading copy by the
     shared detector (qa/list_detect.py) for the plan's citation style.
     When the plan declares per-unit list counts (lists: N on a unit
     line), the total detected must agree with the total declared -
     a detector-independent check, because a detector can only lose a
     list it cannot see.

Counting rules (absorbed from the skill body): occurrences are counted,
never the lines that contain a match; a list is counted from its own
heading line; an entry counts only at a line beginning with its number
in one of the entry forms ("N.", "[N]", "N)", "N)"), the numbers
running 1 to N without gap or repeat.

Usage: check_gate.py READING_COPY SPLIT_PLAN NOTES [WORKSHEET]
Exit code 0 when every check passes, 1 otherwise.
"""
import hashlib
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from list_detect import detect_numbered_lists, extra_headings_from_plan, normalize_heading

copy_path, plan_path, notes_path = sys.argv[1], sys.argv[2], sys.argv[3]
sheet_path = sys.argv[4] if len(sys.argv) > 4 else None

copy_bytes = open(copy_path, "rb").read()
copy_lines = copy_bytes.decode("utf-8").split("\n")
plan = open(plan_path, encoding="utf-8").read()
notes = open(notes_path, encoding="utf-8").read()

failures = []
notes_out = []


def plan_field(name):
    m = re.search(rf"^-\s*{name}:\s*(.+)$", plan, re.M)
    return m.group(1).strip() if m else None


extra_headings, dismissed = extra_headings_from_plan(plan)
style = (plan_field("citation_style_detected") or "").lower()
ruling = (plan_field("correspondence_ruling") or "").lower()

# identity ----------------------------------------------------------------------
rec_bytes, rec_md5 = plan_field("bytes"), plan_field("md5")
if rec_bytes and rec_bytes.isdigit() and rec_md5 and "pending" not in rec_md5:
    if int(rec_bytes) != len(copy_bytes):
        failures.append(
            f"identity mismatch: plan bytes {rec_bytes} vs actual {len(copy_bytes)}"
        )
    if rec_md5.lower() != hashlib.md5(copy_bytes).hexdigest():
        failures.append("identity mismatch: plan md5 differs from actual md5")
else:
    notes_out.append("identity: no identity recorded in plan, check skipped")

# anchors -----------------------------------------------------------------------
anchors = []
for ln in copy_lines:
    m = re.match(r"^#{1,2} Page (\d+)$", ln)
    if m:
        anchors.append(int(m.group(1)))

units = []
for ln in plan.splitlines():
    m = re.match(r"^unit:\s*(.+?)\s*\|\s*(.+)$", ln)
    if not m:
        continue
    u = {"name": m.group(1)}
    rest = m.group(2)
    pm = re.search(r"pages:\s*(\d+)\s*-\s*(\d+)", rest)
    if pm:
        u["pages"] = (int(pm.group(1)), int(pm.group(2)))
    lm = re.search(r"lines:\s*(\d+)\s*-\s*(\d+)", rest)
    if lm:
        u["lines"] = (int(lm.group(1)), int(lm.group(2)))
    sm = re.search(r"section:\s*(.+?)\s*$", rest)
    if sm:
        u["section"] = sm.group(1)
    km = re.search(r"lists:\s*(\d+)", rest)
    if km:
        u["lists"] = int(km.group(1))
    units.append(u)

heading_basis = bool(units) and all("section" in u for u in units)
if anchors:
    if anchors != list(range(anchors[0], anchors[0] + len(anchors))):
        failures.append(
            f"anchor continuity broken: {anchors[:5]}... total {len(anchors)}"
        )
    page_lo, page_hi = anchors[0], anchors[-1]
elif heading_basis:
    page_lo = page_hi = None
    notes_out.append("anchors: none; plan uses section units")
    copy_norm = {normalize_heading(ln) for ln in copy_lines}
    for u in units:
        if normalize_heading(u["section"]) not in copy_norm:
            failures.append(f"unit '{u['name']}' section heading not found in copy")
else:
    failures.append("no page anchors detected")
    page_lo = page_hi = None

# tiling ------------------------------------------------------------------------
if not units:
    failures.append("no unit lines in split plan")
elif page_lo is not None and all("pages" in u for u in units):
    scope = plan_field("scope") or ""
    sm = re.search(r"(\d+)\s*[-\u2013\u2014~](\d+)", scope)
    if sm and "full" not in scope.lower():
        page_lo, page_hi = int(sm.group(1)), int(sm.group(2))
    covered = []
    for u in units:
        a, b = u["pages"]
        covered += list(range(a, b + 1))
    want = list(range(page_lo, page_hi + 1))
    missing = sorted(set(want) - set(covered))
    dup = sorted({p for p in covered if covered.count(p) > 1})
    if missing:
        failures.append(f"tiling mismatch (missing pages {missing})")
    if dup:
        involved = [u for u in units if u["pages"][0] <= dup[-1] and u["pages"][1] >= dup[0]]
        if all("lines" in u for u in involved):
            lc = []
            for u in involved:
                lc += list(range(u["lines"][0], u["lines"][1] + 1))
            if len(lc) != len(set(lc)):
                failures.append(f"tiling mismatch (overlap pages {dup}, line ranges also overlap)")
            else:
                notes_out.append(f"tiling: page overlap {dup} resolved by line ranges")
        else:
            failures.append(f"tiling mismatch (overlap pages {dup})")

# notes presence and content ------------------------------------------------------
note_lines = notes.split("\n")
for u in units:
    name = u["name"]
    idx = None
    for i, ln in enumerate(note_lines):
        if re.match(rf"^#{{1,3}}\s+{re.escape(name)}\s*$", ln):
            idx = i
            break
    if idx is None:
        failures.append(f"notes: no heading for unit '{name}' (treated as unread)")
        continue
    body = []
    for ln in note_lines[idx + 1:]:
        if re.match(r"^#{1,3}\s+", ln):
            break
        if ln.strip():
            body.append(ln)
    if not body:
        failures.append(f"notes: unit '{name}' section is empty (treated as unread)")

# list detection ------------------------------------------------------------------
numbered_lists, candidates = detect_numbered_lists(copy_lines, extra_headings)
cand_live = [c for c in candidates if c["line"] not in dismissed]
detected = [len(L["entries"]) for L in numbered_lists]


def ay_counts():
    year = re.compile(r"\(\d{4}[a-z]?[^)]*\)")
    surname = re.compile(r"^[A-Z\u00c0-\u00de][\w\u0300-\u036f\u00c0-\u00ff'\u2019.-]*")
    counts = []
    active = {normalize_heading(h) for h in
              ["\u53c2\u8003\u6587\u732e", "\u5f15\u7528\u6587\u732e", "\u6587\u732e",
               "references", "bibliography", "workscited"]}
    active |= {normalize_heading(h) for h in extra_headings}
    i = 0
    while i < len(copy_lines):
        if normalize_heading(copy_lines[i]) in active:
            count, j = 0, i + 1
            while j < len(copy_lines):
                ln = copy_lines[j]
                if not ln.strip() or ln[:1].isspace() or re.match(r"^#{1,2} Page \d+$", ln):
                    j += 1
                    continue
                if surname.match(ln) and (year.search(ln) or re.match(r"^[A-Z\u00c0-\u00de][\w'\u2019.-]*,\s", ln)):
                    count += 1
                    j += 1
                    continue
                break
            if count:
                counts.append(count)
            i = j
        else:
            i += 1
    return counts


def line_list_counts():
    counts = []
    active = {normalize_heading(h) for h in
              ["bibliography", "workscited", "\u53c2\u8003\u6587\u732e", "\u6587\u732e"]}
    active |= {normalize_heading(h) for h in extra_headings}
    i = 0
    while i < len(copy_lines):
        if normalize_heading(copy_lines[i]) in active:
            count, j = 0, i + 1
            while j < len(copy_lines):
                ln = copy_lines[j]
                if not ln.strip():
                    j += 1
                    continue
                if re.match(r"^#{1,3}\s", ln) or normalize_heading(ln) in active:
                    break
                count += 1
                j += 1
            if count:
                counts.append(count)
            i = j
        else:
            i += 1
    return counts


if "author-year" in style or "author_year" in style:
    detected = ay_counts()
elif "mla" in style or "notes" in style:
    detected = line_list_counts()

declared_lists = sum(u["lists"] for u in units if "lists" in u)
if declared_lists:
    if declared_lists != len(detected):
        failures.append(
            f"declared list count {declared_lists} != detected {len(detected)}"
        )
    else:
        notes_out.append(f"lists: declared {declared_lists} matches detected")

# worksheet checks ------------------------------------------------------------------
def sheet_sizes_of(sheet):
    return [
        int(m.group(1))
        for m in re.finditer(r"^##\s+.*?[(\uFF08][^)\uFF09]*?(\d+)\u4EF6", sheet, re.M)
    ]


if ruling.startswith("stands"):
    if not sheet_path:
        failures.append("correspondence ruling stands but no worksheet was given")
    else:
        sheet = open(sheet_path, encoding="utf-8").read()
        if "\u3010\u8B66\u544A\u3011" in sheet:
            failures.append("worksheet carries a warning block (empty run is not a pass)")
        ss = sheet_sizes_of(sheet)
        if not ss:
            failures.append("worksheet lists no lists at all")
        elif ss != detected:
            failures.append(f"sheet list sizes {ss} != detected in copy {detected}")
        verdict_lines = [ln for ln in sheet.split("\n") if "\u5224\u5B9A" in ln]
        unfilled = 0
        for ln in verdict_lines:
            tail = ln.split("\u5224\u5B9A", 1)[1]
            tail = re.sub(r"[(\uFF08]\u5408\uff0f\u5426\uff0f\u4FDD\u7559[)\uFF09]", "", tail)
            if "\u6839\u62E0" in tail:
                verdict, reason = tail.split("\u6839\u62E0", 1)
                verdict = verdict.strip(" \uff1a:/\uFF0F")
                if not verdict or not reason.strip(" \uff1a:"):
                    unfilled += 1
            elif not tail.strip(" \uff1a:"):
                unfilled += 1
        if verdict_lines and unfilled:
            failures.append(f"worksheet has {unfilled} pairs with unfilled verdict/reason")
        if not verdict_lines:
            failures.append("worksheet has no verdict fields")
        print(f"lists detected in copy: {detected}, on sheet: {ss}")
elif sheet_path:
    sheet = open(sheet_path, encoding="utf-8").read()
    ss = sheet_sizes_of(sheet)
    if ss and ss != detected:
        failures.append(f"sheet list sizes {ss} != detected in copy {detected}")
    print(f"lists detected in copy: {detected}" + (f", on sheet: {ss}" if ss else ""))

for c in cand_live:
    notes_out.append(
        f"candidate heading at line {c['line'] + 1} ({c['reason']}): {c['text'][:40]}"
    )

print(f"anchors: {len(anchors)} pages, units: {len(units)}")
for n in notes_out:
    print(n)
if failures:
    for f in failures:
        print(f"FAIL: {f}")
    sys.exit(1)
print("gate checks: all passed")
