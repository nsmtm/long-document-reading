#!/usr/bin/env python3
"""Regression tests for the gate widening and shared list detection.

Guards (review run 20261118-12 decisions 1 and 4, cross-check run
20261118-13):
  T1  mixed list headings （参考文献 + 文献） are both detected; the gate
      no longer passes a sheet that silently covers only one list.
  T3  a warning-carrying empty worksheet FAILS the gate when the
      correspondence ruling stands (it used to pass with exit 0).
  T5  entries in the N） form are read (they used to end the run).
  T7  heading variants (References:, references, "5. References",
      spaced-out 参考文献） are detected after normalisation.
  T10 enumeration (1,3,5), wave range (2〜4), and single-parenthesis
      citations 6) reach the citation population.
  G1  a partial scope declared in the plan tiles against the scope,
      not against page 1 (the gate used to fail pp.2-3 scopes).
  G2  page-interior sub-splits pass when their line ranges tile.
  G3  an identity mismatch between plan and copy FAILS (R-P06).
  G4  a declared per-unit list count that disagrees with detection
      FAILS (the detector-independent backstop).
  G5  an empty notes section FAILS (R-06: presence is not content).
  G6  unfilled verdicts on the worksheet FAIL (R-06).

Run: python3 qa/test_gate_and_detection.py  (exit 0 = all pass)
"""
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

QA = Path(__file__).resolve().parent
fails = []


def run(args):
    return subprocess.run(
        [sys.executable] + [str(a) for a in args],
        capture_output=True, text=True,
    )


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  {detail}" if not cond and detail else ""))
    if not cond:
        fails.append(name)


def write(d, name, text):
    p = d / name
    p.write_text(text, encoding="utf-8")
    return p


def plan_for(copy, units, scope="full read", ruling="stands", style="numbered", extra=""):
    data = Path(copy).read_bytes()
    return (
        "# Split plan\n\n"
        f"- reading_copy: {copy}\n- bytes: {len(data)}\n"
        f"- md5: {hashlib.md5(data).hexdigest()}\n"
        "- start_time: 2026-11-18T00:00:00+09:00\n"
        f"- scope: {scope}\n- correspondence_ruling: {ruling}\n"
        f"- citation_style_detected: {style}\n{extra}\n## Units\n\n" + units + "\n"
    )


def fill_verdicts(sheet_text):
    out = []
    for ln in sheet_text.split("\n"):
        if ln.rstrip() == "  判定:":
            out.append("  判定: 合／根拠: 内容が一致")
        elif ln.rstrip() == "  判定（合／否／保留）: ／根拠:":
            out.append("  判定（合／否／保留）: 合／根拠: 内容が一致")
        else:
            out.append(ln)
    return "\n".join(out)


with tempfile.TemporaryDirectory() as td:
    d = Path(td)

    # --- T1/T5/T7/T10: two lists, mixed headings and forms ---------------
    copy = write(d, "copy.md", """# Chapter 1
# Page 1
本文は (1) と (1,3,5) と (2〜4) と 6) を引く。
参考文献
1. 山田太郎. 論文A. 2020.
2. 佐藤花. 論文B. 2021.
3. 鈴木一. 論文C. 2022.
# Page 2
# Chapter 2
本文は (1) を引く。
文　献
1）高橋健. 論文D. 2019.
2）伊藤恵. 論文E. 2023.
""")
    sheet = d / "sheet.md"
    r = run([QA / "correspondence_worksheet.py", copy, sheet])
    st = sheet.read_text(encoding="utf-8")
    check("T1 lists both detected", "リスト1" in st and "リスト2" in st, st[:200])
    check("T5 N） entries read", "2件" in st)
    check("T7 spaced heading detected", r.returncode == 0, r.stderr[:200])
    check("T10 citation forms sampled", "本文の引用" in st and "(6)" in st or "6)" in st)
    notes = write(d, "notes.md", "## 第1章\n読んだ。\n\n## 第2章\n読んだ。\n")
    plan = write(d, "plan.md", plan_for(copy, "unit: 第1章 | pages: 1-1 | lists: 1\nunit: 第2章 | pages: 2-2 | lists: 1"))
    filled = write(d, "sheet_filled.md", fill_verdicts(st))
    r = run([QA / "check_gate.py", copy, plan, notes, filled])
    check("T1 gate passes on filled sheet", r.returncode == 0, r.stdout[-300:])

    # --- T3: warning empty sheet fails the gate ---------------------------
    copy3 = write(d, "copy3.md", "# Page 1\n本文 (1)。\n文献\n")
    sheet3 = d / "sheet3.md"
    r = run([QA / "correspondence_worksheet.py", copy3, sheet3])
    check("T3 generator warns (exit 2)", r.returncode == 2)
    plan3 = write(d, "plan3.md", plan_for(copy3, "unit: 全体 | pages: 1-1"))
    notes3 = write(d, "notes3.md", "## 全体\n読んだ。\n")
    r = run([QA / "check_gate.py", copy3, plan3, notes3, sheet3])
    check("T3 gate fails empty sheet", r.returncode == 1 and "warning block" in r.stdout, r.stdout[-200:])

    # --- G1: partial scope -------------------------------------------------
    copy4 = write(d, "copy4.md", "# Page 1\n表紙。\n# Page 2\n本文A。\n# Page 3\n本文B。\n")
    plan4 = write(d, "plan4.md", plan_for(
        copy4, "unit: 前半 | pages: 2-2\nunit: 後半 | pages: 3-3",
        scope="pages 2-3", ruling="excluded by tester"))
    notes4 = write(d, "notes4.md", "## 前半\n読んだ。\n\n## 後半\n読んだ。\n")
    r = run([QA / "check_gate.py", copy4, plan4, notes4])
    check("G1 partial scope tiles", r.returncode == 0, r.stdout[-200:])

    # --- G2: page-interior sub-splits by line ranges -----------------------
    copy5 = write(d, "copy5.md", "# Page 1\n行1\n行2\n# Page 2\n行3\n行4\n")
    plan5 = write(d, "plan5.md", plan_for(
        copy5, "unit: 上 | pages: 1-2 | lines: 1-3\nunit: 下 | pages: 2-2 | lines: 4-6",
        ruling="excluded by tester"))
    notes5 = write(d, "notes5.md", "## 上\n読んだ。\n\n## 下\n読んだ。\n")
    r = run([QA / "check_gate.py", copy5, plan5, notes5])
    check("G2 sub-split by lines tiles", r.returncode == 0, r.stdout[-200:])

    # --- G3: identity mismatch ---------------------------------------------
    bad = plan_for(copy4, "unit: 前半 | pages: 2-2\nunit: 後半 | pages: 3-3",
                   scope="pages 2-3", ruling="excluded by tester").replace(
                       f"- bytes: {len(Path(copy4).read_bytes())}", "- bytes: 999")
    plan6 = write(d, "plan6.md", bad)
    r = run([QA / "check_gate.py", copy4, plan6, notes4])
    check("G3 identity mismatch fails", r.returncode == 1 and "identity" in r.stdout, r.stdout[-200:])

    # --- G4: declared list count mismatch -----------------------------------
    plan7 = write(d, "plan7.md", plan_for(copy, "unit: 第1章 | pages: 1-1 | lists: 2\nunit: 第2章 | pages: 2-2 | lists: 1"))
    r = run([QA / "check_gate.py", copy, plan7, notes, filled])
    check("G4 declared count mismatch fails", r.returncode == 1 and "declared" in r.stdout, r.stdout[-200:])

    # --- G5: empty notes section ---------------------------------------------
    notes8 = write(d, "notes8.md", "## 前半\n\n## 後半\n読んだ。\n")
    r = run([QA / "check_gate.py", copy4, plan4, notes8])
    check("G5 empty notes fails", r.returncode == 1 and "empty" in r.stdout, r.stdout[-200:])

    # --- G6: unfilled verdicts -------------------------------------------------
    r = run([QA / "check_gate.py", copy, plan, notes, sheet])
    check("G6 unfilled verdicts fail", r.returncode == 1 and "verdict" in r.stdout, r.stdout[-200:])

    # --- R-P05 scripts -------------------------------------------------------
    folio = write(d, "folio.md", "title\n1\nbody A\n2\nbody B\n")
    fout = d / "folio_out.md"
    r = run([QA / "restore_page_anchors.py", folio, fout])
    check("P5 folio restore", r.returncode == 0 and fout.read_text(encoding="utf-8").count("# Page") == 2)
    badf = write(d, "badf.md", "1\nbody\n3\n")
    r = run([QA / "restore_page_anchors.py", badf, d / "badf_out.md"])
    check("P5 folio gap refused (exit 2)", r.returncode == 2)
    r = run([QA / "compare_bytes.py", folio, folio])
    check("P5 compare identical", r.returncode == 0 and "identical: yes" in r.stdout)
    r = run([QA / "compare_bytes.py", folio, badf])
    check("P5 compare different", r.returncode == 1 and "identical: no" in r.stdout)
    names = write(d, "names.md", "\u62C5\u5F53\u306F\u5C71\u7530\u592A\u90CE \u90E8\u9577\u3002\n\u7530\u4E2D\u82B1\u5B50\u69D8\u3078\u3002\n")
    r = run([QA / "extract_name_candidates.py", names])
    check("P5 name candidates", "\u5C71\u7530\u592A\u90CE" in r.stdout and "\u7530\u4E2D\u82B1\u5B50" in r.stdout, r.stdout[:200])
    cov = run([QA / "make_coverage_statement.py", copy4, plan4, notes4])
    check("P5 coverage statement generated", cov.returncode == 0 and "covered pages: 2" in cov.stdout, cov.stdout[-200:])

print("RESULT:", "all pass" if not fails else f"{len(fails)} failed: {fails}")
sys.exit(1 if fails else 0)
