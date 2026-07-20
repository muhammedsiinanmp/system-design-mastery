#!/usr/bin/env python3
"""Verify every cross-document (Doc §N) citation resolves to a real section.

The repo's docs cite each other as `(Avail §6)`, `(SPOF §4)`, `(Rel §5)`.
Nothing enforced that N existed, so wrong citations shipped repeatedly:

  * `Foundations §7` — cited twice; that doc has only §1–§6.
  * `Scaling §5`     — cited five times for content that lives in §4.

This catches the first class (section does not exist). It CANNOT catch the
second (section exists but holds different content) — that still needs a human
to open the target and read it. Treat a clean run as necessary, not sufficient.

Usage:  python3 tools/check-citations.py [--list]
Exit:   0 = all citations resolve, 1 = unresolved citations found
"""

import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Short names used in citations -> the document they refer to.
# Note the deliberate collision: "Scaling" is Phase 01's group doc,
# "Scalability" is Phase 02's topic. They are different files.
DOC_ALIASES = {
    "Foundations":  "01-introduction/01-networking-foundations/README.md",
    "Scaling":      "01-introduction/04-scaling/README.md",
    "Storage":      "01-introduction/03-data-storage/README.md",
    "Dist":         "01-introduction/05-distributed-systems/README.md",
    "Distributed":  "01-introduction/05-distributed-systems/README.md",
    "Arch":         "01-introduction/06-architecture-patterns/README.md",
    "Latency":      "02-core-properties/01-latency-vs-throughput/README.md",
    "Avail":        "02-core-properties/02-availability/README.md",
    "Availability": "02-core-properties/02-availability/README.md",
    "Rel":          "02-core-properties/03-reliability/README.md",
    "Reliability":  "02-core-properties/03-reliability/README.md",
    "Scal":         "02-core-properties/04-scalability/README.md",
    "Scalability":  "02-core-properties/04-scalability/README.md",
    "SPOF":         "02-core-properties/05-single-point-of-failure/README.md",
    "DNS":          "03-networking/01-dns/README.md",
    "HTTP":         "03-networking/02-http-https/README.md",
    "TCP":          "03-networking/03-tcp-vs-udp/README.md",
}

# `Doc §N`, parenthesized or bare, plus multi-section forms like `Rel §5, §9`.
#
# The parentheses are OPTIONAL and that matters: the worst citation bug in this
# repo's history — `Foundations §7 made DNS Step 1 …` — was written bare, and an
# earlier version of this script required parentheses and sailed straight past
# it. Match the citation, not the punctuation around it.
CITATION = re.compile(r"\b([A-Z][A-Za-z]+)\s+§(\d+)((?:\s*,\s*§\d+)*)")
EXTRA_SECTIONS = re.compile(r"§(\d+)")
HEADING = re.compile(r"^## (\d+)\.", re.M)


def sections_of(relpath):
    """Return the set of numbered ## N. headings in a document."""
    path = os.path.join(REPO, relpath)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return {int(n) for n in HEADING.findall(fh.read())}


INLINE_CODE = re.compile(r"`[^`]*`")


def strip_mentions(line):
    """Blank out inline-code spans before matching.

    A citation in backticks is being *mentioned*, not *used* — the style guide
    and the roadmap both quote `Foundations §7` as an example of a broken
    citation, and flagging their own documentation would be noise. Replace with
    spaces rather than deleting so column positions stay honest.
    """
    return INLINE_CODE.sub(lambda m: " " * len(m.group(0)), line)


def markdown_files():
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in (".git", "tools")]
        for name in sorted(files):
            if name.endswith(".md"):
                yield os.path.join(root, name)


def main():
    section_cache = {}
    problems = []
    checked = 0

    for path in markdown_files():
        rel = os.path.relpath(path, REPO)
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()

        for lineno, raw in enumerate(lines, 1):
            line = strip_mentions(raw)
            for match in CITATION.finditer(line):
                alias, first, rest = match.group(1), match.group(2), match.group(3)

                if alias not in DOC_ALIASES:
                    continue  # not a known doc alias; ignore

                target = DOC_ALIASES[alias]
                if target not in section_cache:
                    section_cache[target] = sections_of(target)
                available = section_cache[target]

                if available is None:
                    problems.append((rel, lineno, match.group(0),
                                     f"target file missing: {target}"))
                    continue

                cited = [int(first)] + [int(n) for n in EXTRA_SECTIONS.findall(rest)]
                for num in cited:
                    checked += 1
                    if num not in available:
                        span = f"§1–§{max(available)}" if available else "none"
                        problems.append((rel, lineno, match.group(0),
                                         f"{alias} has no §{num} (has {span})"))

    print(f"checked {checked} citations across {len(section_cache)} target docs")

    if problems:
        print(f"\n❌ {len(problems)} unresolved:\n")
        for rel, lineno, text, why in problems:
            print(f"  {rel}:{lineno}")
            print(f"    {text}  →  {why}")
        print("\nFix the citation, or name the section in prose if it is unnumbered.")
        return 1

    print("✅ all citations resolve to real sections")
    print("   (this proves the section EXISTS, not that it is the RIGHT one —")
    print("    open the target and read it when adding a new citation)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
