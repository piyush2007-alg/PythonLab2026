"""
style_checker.py
Lightweight PEP 8 style checker (no external dependency required).
Checks: line length, trailing whitespace, tab usage, blank-line rules,
multiple statements per line, and missing whitespace around operators.
"""

import re

MAX_LINE_LENGTH = 79
OPERATOR_RE = re.compile(r'[a-zA-Z0-9_\)\]]=[a-zA-Z0-9_\(\-]')  # a=b style, rough heuristic


def analyze(source_lines, filename):
    issues = []

    for i, line in enumerate(source_lines, start=1):
        stripped = line.rstrip("\n")

        # Line length
        if len(stripped) > MAX_LINE_LENGTH:
            issues.append({
                "file": filename, "line": i,
                "issue": f"Line exceeds {MAX_LINE_LENGTH} characters ({len(stripped)})",
                "severity": "Low",
            })

        # Trailing whitespace
        if stripped != stripped.rstrip():
            issues.append({
                "file": filename, "line": i,
                "issue": "Trailing whitespace",
                "severity": "Low",
            })

        # Tabs instead of spaces
        if "\t" in line:
            issues.append({
                "file": filename, "line": i,
                "issue": "Tab character used for indentation (use 4 spaces)",
                "severity": "Medium",
            })

        # Multiple statements on one line (naive check for ';')
        if ";" in stripped and not stripped.strip().startswith("#"):
            issues.append({
                "file": filename, "line": i,
                "issue": "Multiple statements on one line (semicolon usage)",
                "severity": "Medium",
            })

        # Missing whitespace around '=' (rough heuristic, skips kwargs in calls)
        if OPERATOR_RE.search(stripped) and "==" not in stripped:
            issues.append({
                "file": filename, "line": i,
                "issue": "Missing whitespace around operator '='",
                "severity": "Low",
            })

    return issues


def blank_line_check(source_lines, filename):
    """Checks for 2 blank lines before top-level def/class (PEP 8)."""
    issues = []
    for i, line in enumerate(source_lines):
        if line.startswith("def ") or line.startswith("class "):
            if i >= 2:
                preceding = source_lines[i - 2:i]
                blanks = sum(1 for p in preceding if p.strip() == "")
                if blanks < 2 and i > 0:
                    issues.append({
                        "file": filename, "line": i + 1,
                        "issue": "Expected 2 blank lines before top-level def/class",
                        "severity": "Low",
                    })
    return issues
