"""
comment_analyzer.py
Analyzes comment and docstring quality:
    - Docstring coverage for modules, classes, functions
    - Comment-to-code ratio
    - Flags trivial / filler comments (e.g., "# fix this", "# code")
"""

import ast
import re

FILLER_PATTERNS = [
    r'^\s*#\s*(fix\s*this|todo|fixme|xxx|code|stuff|do this)\s*$',
    r'^\s*#\s*$',
]
FILLER_RE = [re.compile(p, re.IGNORECASE) for p in FILLER_PATTERNS]


def _is_filler(comment_text):
    return any(p.match(comment_text) for p in FILLER_RE)


def analyze(tree, source_lines, filename):
    issues = []

    total_code_lines = len([l for l in source_lines if l.strip() and not l.strip().startswith("#")])
    comment_lines = [l for l in source_lines if l.strip().startswith("#")]
    total_comment_lines = len(comment_lines)

    # --- Docstring coverage ---
    if not ast.get_docstring(tree):
        issues.append({
            "file": filename,
            "line": 1,
            "issue": "Module is missing a top-level docstring",
            "severity": "Medium",
        })

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not ast.get_docstring(node):
                kind = "Class" if isinstance(node, ast.ClassDef) else "Function"
                issues.append({
                    "file": filename,
                    "line": node.lineno,
                    "issue": f"{kind} '{node.name}' is missing a docstring",
                    "severity": "Medium",
                })

    # --- Filler / low-value comments ---
    for i, line in enumerate(source_lines, start=1):
        if line.strip().startswith("#") and _is_filler(line):
            issues.append({
                "file": filename,
                "line": i,
                "issue": "Comment appears to be filler / non-descriptive",
                "severity": "Low",
            })

    # --- Comment-to-code ratio ---
    ratio = round(total_comment_lines / total_code_lines, 2) if total_code_lines else 0
    if ratio < 0.1:
        issues.append({
            "file": filename,
            "line": None,
            "issue": f"Low comment-to-code ratio ({ratio}); consider adding more explanatory comments",
            "severity": "Low",
        })

    return issues, ratio
