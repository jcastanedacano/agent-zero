#!/usr/bin/env python3
"""Check that the numbers quoted in README.md match the files in the repository.

Counts are computed from the files (never typed by hand):

  modules            Track-*/Module-*.md
  tracks             Track-* directories
  skills             skills/*/*/SKILL.md
  library queries    KQL-Library/P0*.kql, counted by unique Q number per file
                     ("// Q5a:", "// Q5b:" and "// Q5:" are one query, Q5)
  skill query files  skills/*/*/queries/*.kql

Each place in README.md that quotes a count is listed in CHECKS below. The script
fails when a quoted number differs from the computed one, and also when a pattern
no longer matches anything, so a rewrite of the README cannot silently disable a check.

The description and the topics of the GitHub repository are not in the files:
update them by hand when a number changes (gh repo edit --description ...).

Usage: python scripts/check-counts.py          (exit code 1 on any mismatch)
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def count_library_queries():
    total = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "KQL-Library", "P0*.kql"))):
        with open(path, encoding="utf-8") as f:
            ids = set(re.findall(r"(?m)^// Q(\d+)[a-z]?:", f.read()))
        total += len(ids)
    return total


COUNTS = {
    "modules": len(glob.glob(os.path.join(ROOT, "Track-*", "Module-*.md"))),
    "tracks": len(glob.glob(os.path.join(ROOT, "Track-*"))),
    "skills": len(glob.glob(os.path.join(ROOT, "skills", "*", "*", "SKILL.md"))),
    "library queries": count_library_queries(),
    "skill query files": len(glob.glob(os.path.join(ROOT, "skills", "*", "*", "queries", "*.kql"))),
}

# (name, file, regex with ONE capture group holding the number, count key)
CHECKS = [
    ("modules badge", "README.md", r"Modules-(\d+)-", "modules"),
    ("tracks badge", "README.md", r"Tracks-(\d+)-", "tracks"),
    ("skills badge", "README.md", r"Agent_Skills-(\d+)-", "skills"),
    ("KQL library badge", "README.md", r"KQL_Library-(\d+)_queries", "library queries"),
    ("modules, summary table", "README.md", r"\*\*(\d+) modules\*\*", "modules"),
    ("modules, overview paragraph", "README.md", r"(\d+) instructional modules", "modules"),
    ("skills, summary table", "README.md", r"\*\*(\d+) agent skills\*\*", "skills"),
    ("skills, overview paragraph", "README.md", r"(\d+) agent skills in agentskills\.io format", "skills"),
    ("skills, repository tree", "README.md", r"skills/\s+← (\d+) agent skills", "skills"),
    ("skills, Skills Library section", "README.md", r"(?m)^(\d+) agent skills in \[agentskills\.io\]", "skills"),
    ("library queries, summary table", "README.md", r"\*\*(\d+) KQL library queries\*\*", "library queries"),
    ("library queries, overview paragraph", "README.md", r"(\d+) KQL queries in the KQL Library", "library queries"),
    ("library queries, repository tree", "README.md", r"KQL-Library/\s+← (\d+) queries", "library queries"),
    ("library queries, KQL Library section", "README.md", r"(?m)^(\d+) queries \(counted by unique Q number", "library queries"),
    ("skill query files, summary table", "README.md", r"plus (\d+) query files bundled with skills, with", "skill query files"),
    ("skill query files, overview paragraph", "README.md", r"plus (\d+) query files bundled with skills \(", "skill query files"),
]


def main():
    print("Counted from the files:")
    for key, value in COUNTS.items():
        print(f"  {key:18s} {value}")
    problems = 0
    cache = {}
    for name, rel, pattern, key in CHECKS:
        text = cache.setdefault(rel, read(rel))
        found = [int(n) for n in re.findall(pattern, text)]
        if not found:
            print(f"NOT FOUND  {name}: the pattern {pattern!r} matches nothing in {rel}; update this script or the README")
            problems += 1
            continue
        for n in found:
            if n != COUNTS[key]:
                print(f"MISMATCH   {name}: {rel} says {n}, the files give {COUNTS[key]}")
                problems += 1
    if problems:
        print(f"\n{problems} problem(s). Fix the README (and the GitHub description) so the numbers match the files.")
        return 1
    print(f"\nAll {len(CHECKS)} checks pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
