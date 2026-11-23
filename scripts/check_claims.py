#!/usr/bin/env python3
"""Claims & Metrics Compliance Checker for ReturnZero AI.

Scans the codebase and documentation to enforce AGENTS.md §10 policies:
prohibits unbacked metrics, fabricated percentages, and forbidden buzzwords.

Exits with:
  0 - Clean: No forbidden claims detected.
  1 - Violation: One or more forbidden claims found.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import NamedTuple


class Violation(NamedTuple):
    file_path: Path
    line_number: int
    matched_pattern: str
    line_content: str


# Forbidden patterns from AGENTS.md §10
FORBIDDEN_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("₹18,000 Cr / $2.2B market sizing", re.compile(r"18[,.]?000\s*(?:cr(?:ore)?|Cr)", re.IGNORECASE)),
    ("$2.2B valuation/market claim", re.compile(r"\$2\.2\s*B(?:illion)?", re.IGNORECASE)),
    ("30-35% national RTO claim", re.compile(r"30[\s–-]+35\s*%\s*national\s*rto", re.IGNORECASE)),
    ("53%/32%/15% root-cause split", re.compile(r"53\s*%\s*/\s*32\s*%\s*/\s*15\s*%", re.IGNORECASE)),
    ("67% abandonment claim", re.compile(r"67\s*%\s*abandonment", re.IGNORECASE)),
    ("85% tape measure claim", re.compile(r"85\s*%\s*don['’]?t\s*use\s*tape", re.IGNORECASE)),
    ("2.4 Mt CO2 claim", re.compile(r"2\.4\s*Mt\s*CO", re.IGNORECASE)),
    ("420 g CO2 claim", re.compile(r"420\s*g\s*CO", re.IGNORECASE)),
    ("44% fit-return reduction claim", re.compile(r"44\s*%\s*fit[- ]return\s*reduction", re.IGNORECASE)),
    ("58% RTO reduction claim", re.compile(r"58\s*%\s*RTO\s*reduction", re.IGNORECASE)),
    ("54.1 lakh net profit claim", re.compile(r"54\.1\s*lakh\s*net\s*profit", re.IGNORECASE)),
    ("net profit claim", re.compile(r"\bnet\s+profit\b", re.IGNORECASE)),
    ("100% accuracy claim", re.compile(r"100\s*%\s*accuracy", re.IGNORECASE)),
    ("guaranteed fit claim", re.compile(r"\bguaranteed\s+fit\b", re.IGNORECASE)),
    ("sub-800 ms vision claim", re.compile(r"sub[\s–-]?800\s*ms\s*vision", re.IGNORECASE)),
    ("94% confidence claim", re.compile(r"94\s*%\s*confidence", re.IGNORECASE)),
    ("10-28% conversion shift claim", re.compile(r"10[\s–-]+28\s*%\s*conversion\s*shift", re.IGNORECASE)),
    ("XGBoost claim", re.compile(r"\bXGBoost\b", re.IGNORECASE)),
    ("Gemini 2.0 claim", re.compile(r"\bGemini\s+2\.0\b", re.IGNORECASE)),
]

# Paths allowed to document the policy or benchmark citations
EXCLUDED_FILE_PATTERNS: set[str] = {
    "AGENTS.md",
    "SOURCES_AND_ASSUMPTIONS.md",
    "ASSUMPTIONS.md",
    "DECISIONS.md",
    "check_claims.py",
}

# Directories to scan
TARGET_DIRECTORIES = ["backend", "frontend", "docs", "scripts"]
TARGET_FILES = ["README.md"]

# Directory names to skip everywhere
SKIPPED_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    ".next",
    "dist",
    "build",
    "coverage",
    ".venv",
    "venv",
    "env",
    "code_to_cart_hackathon",
}


def should_skip_file(file_path: Path) -> bool:
    for part in file_path.parts:
        if part in SKIPPED_DIR_NAMES:
            return True
    for excluded in EXCLUDED_FILE_PATTERNS:
        if file_path.name == excluded or file_path.name.endswith(excluded):
            return True
    return False


def scan_file(file_path: Path) -> list[Violation]:
    violations: list[Violation] = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        print(f"Warning: Could not read {file_path}: {exc}", file=sys.stderr)
        return violations

    for line_idx, line in enumerate(content.splitlines(), start=1):
        for label, pattern in FORBIDDEN_PATTERNS:
            if pattern.search(line):
                violations.append(
                    Violation(
                        file_path=file_path,
                        line_number=line_idx,
                        matched_pattern=label,
                        line_content=line.strip(),
                    )
                )
    return violations


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    files_to_scan: list[Path] = []

    for target_dir in TARGET_DIRECTORIES:
        dir_path = repo_root / target_dir
        if dir_path.is_dir():
            for p in dir_path.rglob("*"):
                if p.is_file() and not should_skip_file(p):
                    files_to_scan.append(p)

    for target_file in TARGET_FILES:
        file_path = repo_root / target_file
        if file_path.is_file() and not should_skip_file(file_path):
            files_to_scan.append(file_path)

    all_violations: list[Violation] = []
    for file_path in sorted(files_to_scan):
        violations = scan_file(file_path)
        all_violations.extend(violations)

    if all_violations:
        print(f"\n[ERROR] Found {len(all_violations)} forbidden claim violation(s):\n", file=sys.stderr)
        for v in all_violations:
            rel_path = v.file_path.relative_to(repo_root) if v.file_path.is_relative_to(repo_root) else v.file_path
            print(f"  {rel_path}:{v.line_number} [{v.matched_pattern}]", file=sys.stderr)
            print(f"    Line: \"{v.line_content}\"\n", file=sys.stderr)
        print("Please remove or correct forbidden claims per AGENTS.md §10.", file=sys.stderr)
        return 1

    print(f"[OK] Scanned {len(files_to_scan)} files. No forbidden claims found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
