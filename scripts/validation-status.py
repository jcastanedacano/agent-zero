#!/usr/bin/env python3
"""Build docs/validation-status.md: the validation status of every query, from its own header.

Sources (nothing is typed by hand in the generated page):

  KQL-Library/P0*.kql            blocks start at "// Qn: Title"; the date of the last
                                 validation of the file comes from the table in
                                 KQL-Library/README.md
  skills/*/*/queries/*.kql       blocks start at "// ── Query n ... ──"

Status rules, applied to the comment lines of each query and to the header of its file:

  NOT VERIFIED   the query's own comments say NOT VERIFIED
  Partly validated  the query's own comments say both: one branch ran, another is NOT VERIFIED
  Validated      the query's comments or the file header say it was validated, ran, compiled,
                 or give the result it returned on the validation tenant, or (library) the
                 file has a last-validation date and the query has no NOT VERIFIED note
  Not stated     the header says nothing: treat it as not verified until it does

"Runs in" comes from the code, not from the header: Timestamp means Defender Advanced Hunting,
TimeGenerated means Sentinel (Log Analytics), resources or authorizationresources means Azure
Resource Graph. "Preview" is shown when the header mentions a preview capability.

Usage:
  python scripts/validation-status.py            write docs/validation-status.md
  python scripts/validation-status.py --check    exit 1 if the file is out of date (used by CI)
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "validation-status.md")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def library_dates():
    text = read(os.path.join(ROOT, "KQL-Library", "README.md"))
    dates = {}
    for m in re.finditer(r"\|\s*\[(P0\d-[^\]]+\.kql)\]\([^)]*\)\s*\|[^|]*\|\s*(\d{4}-\d{2}-\d{2})\s*\|", text):
        dates[m.group(1)] = m.group(2)
    return dates


def split_blocks(path, library):
    text = read(path)
    if library:
        parts = re.split(r"(?m)^// (Q\d+[a-z]?): ([^\n]*)\n", text)
        step = 3
    else:
        parts = re.split(r"(?m)^// ── Query (\d+)([^\n]*)\n", text)
        step = 3
    header = parts[0]
    for i in range(1, len(parts), step):
        qid = parts[i] if library else "Q" + parts[i]
        raw_title = parts[i + 1]
        if not library:
            raw_title = re.sub(r"[─\s]+$", "", raw_title)
            raw_title = re.sub(r"^\s*\(([^)]*)\)", "", raw_title)  # "(Azure Resource Graph)" marker
            raw_title = raw_title.lstrip(": ").strip()
        yield qid, raw_title.strip(), parts[i + 2], header


def engine(code):
    if re.search(r"(?m)^\s*(resources|authorizationresources)\b", code):
        return "Azure Resource Graph"
    ts = re.search(r"\bTimestamp\b", code) is not None
    tg = re.search(r"\bTimeGenerated\b", code) is not None
    if ts and tg:
        return "Mixed (see header)"
    if ts:
        return "Advanced Hunting"
    if tg:
        return "Sentinel"
    return "Any"


VALID = re.compile(r"[Vv]alidated|\bcompiles?\b|\bcompiled\b|\bran\b|Result (on|in) the validation|returned (\d+ )?(rows|no rows)|\b\d+ rows\b")


def classify(comments, header, library, date):
    if "NOT VERIFIED" in comments:
        if VALID.search(comments):
            return "Partly validated", "its header (see notes)"
        return "NOT VERIFIED", "its header"
    if VALID.search(comments):
        return "Validated", "its header"
    if library and date:
        return "Validated", f"file, {date}"
    if VALID.search(header) and "NOT VERIFIED" not in header:
        return "Validated", "file header"
    if VALID.search(header):
        return "Validated", "file header (see notes)"
    return "Not stated", "-"


def build():
    dates = library_dates()
    sections = []
    totals = {"Validated": 0, "Partly validated": 0, "NOT VERIFIED": 0, "Not stated": 0}
    sources = [(True, sorted(glob.glob(os.path.join(ROOT, "KQL-Library", "P0*.kql")))),
               (False, sorted(glob.glob(os.path.join(ROOT, "skills", "*", "*", "queries", "*.kql"))))]
    for library, files in sources:
        for path in files:
            rel = os.path.relpath(path, ROOT).replace("\\", "/")
            date = dates.get(os.path.basename(path)) if library else None
            rows = []
            for qid, title, body, header in split_blocks(path, library):
                lines = body.split("\n")
                comments = "\n".join(l for l in lines if l.startswith("//"))
                code = "\n".join(l for l in lines if not l.startswith("//"))
                status, evidence = classify(comments, header, library, date)
                preview = "Preview" if re.search(r"\bpreview\b", comments, re.I) else ""
                title = title.replace("|", "/")
                title = (title[:88] + "...") if len(title) > 90 else title
                rows.append((qid, title, engine(code), status, evidence, preview))
                totals[status] += 1
            label = os.path.basename(path) if library else rel.split("/")[1] + "/" + rel.split("/")[2]
            link = "../" + rel
            sections.append((("KQL Library" if library else "Skill queries"), label, link, rows))
    total = sum(totals.values())

    out = []
    out.append("# Query validation status\n")
    out.append("Generated by `scripts/validation-status.py` from the header of each query. Do not edit by hand: change the header of the query and run the script (CI fails if this page is out of date).\n")
    out.append(f"**{total} queries**: {totals['Validated']} validated, {totals['Partly validated']} partly validated, {totals['NOT VERIFIED']} NOT VERIFIED, {totals['Not stated']} with no status stated. The KQL Library counts {len([1 for s in sections if s[0] == 'KQL Library' for _ in s[3]])} blocks here because a Q5a, Q5b and Q5c are separate blocks (the README counts them as one query).\n")
    out.append("| Status | Meaning |\n|---|---|\n"
               "| Validated | The header says the query ran or compiled on a tenant or workspace, gives the result it returned, or (KQL Library) the file has a last-validation date. Read the header for what exactly was checked. |\n"
               "| Partly validated | The header says one branch of the query ran and another is NOT VERIFIED (for example the app-role events ran and the consent events did not). Read the header. |\n"
               "| NOT VERIFIED | The header says it has not run against real data, usually because the table, event or preview capability is missing in the validation tenant. |\n"
               "| Not stated | The header says nothing. Treat it as not verified until it does. |\n")
    out.append("**Runs in** comes from the code: `Timestamp` means Defender Advanced Hunting, `TimeGenerated` means Sentinel (Log Analytics), `resources` or `authorizationresources` means Azure Resource Graph, and Mixed means both columns appear, so read the header before pasting. **Preview** means the header mentions a preview capability.\n")
    last = None
    for kind, label, link, rows in sections:
        if kind != last:
            out.append(f"\n## {kind}\n")
            last = kind
        out.append(f"\n### [{label}]({link})\n")
        out.append("| Query | Title | Runs in | Status | Evidence | Preview |\n|---|---|---|---|---|---|")
        for qid, title, eng, status, ev, prev in rows:
            out.append(f"| {qid} | {title} | {eng} | {status} | {ev} | {prev} |")
    return "\n".join(out) + "\n"


def main():
    new = build()
    if "--check" in sys.argv:
        old = read(OUT) if os.path.exists(OUT) else ""
        if old != new:
            print("docs/validation-status.md is out of date: run python scripts/validation-status.py and commit the result.")
            return 1
        print("docs/validation-status.md is up to date.")
        return 0
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(new)
    print("wrote", os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
