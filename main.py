"""
Python Code Quality & Comment Analyzer  (Phase 2)
=========================================================================
Analyzes Python source code for:
    1. Coding standards (PEP 8-style checks)
    2. Comment / docstring quality
    3. Code complexity (cyclomatic complexity, nesting, length)
    4. Naming conventions (snake_case, PascalCase, UPPER_SNAKE_CASE)
    5. Unused imports and unused variables            (NEW in Phase 2)
    6. Quality Grade label: Best / Good / Average / Poor  (NEW in Phase 2)

Generates a per-file quality score (out of 100) plus a grade label,
issue listings, and improvement suggestions. Built entirely on the
Python standard library — no external dependencies required.

Usage:
    python main.py <file_or_directory> [--export report.md]
"""

import argparse
import ast
import os
import re
import sys


# =========================================================================
# 1. FILE HANDLING
# =========================================================================

def find_python_files(path):
    """Return a list of .py files given a file or directory path."""
    if os.path.isfile(path) and path.endswith(".py"):
        return [path]

    py_files = []
    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    return py_files


def read_source(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    return source, source.splitlines()


def parse_source(source, filepath):
    """Returns (tree, error). error is None on success."""
    try:
        tree = ast.parse(source, filename=filepath)
        return tree, None
    except SyntaxError as e:
        return None, f"SyntaxError: {e.msg} at line {e.lineno}"


# =========================================================================
# 2. STYLE CHECKER (PEP 8-style checks)
# =========================================================================

MAX_LINE_LENGTH = 79
OPERATOR_RE = re.compile(r'[a-zA-Z0-9_\)\]]=[a-zA-Z0-9_\(\-]')


def check_style(source_lines, filename):
    issues = []
    for i, line in enumerate(source_lines, start=1):
        stripped = line.rstrip("\n")

        if len(stripped) > MAX_LINE_LENGTH:
            issues.append({"file": filename, "line": i,
                            "issue": f"Line exceeds {MAX_LINE_LENGTH} characters ({len(stripped)})",
                            "severity": "Low"})

        if stripped != stripped.rstrip():
            issues.append({"file": filename, "line": i,
                            "issue": "Trailing whitespace", "severity": "Low"})

        if "\t" in line:
            issues.append({"file": filename, "line": i,
                            "issue": "Tab character used for indentation (use 4 spaces)",
                            "severity": "Medium"})

        if ";" in stripped and not stripped.strip().startswith("#"):
            issues.append({"file": filename, "line": i,
                            "issue": "Multiple statements on one line (semicolon usage)",
                            "severity": "Medium"})

        if OPERATOR_RE.search(stripped) and "==" not in stripped:
            issues.append({"file": filename, "line": i,
                            "issue": "Missing whitespace around operator '='",
                            "severity": "Low"})

    for i, line in enumerate(source_lines):
        if line.startswith("def ") or line.startswith("class "):
            if i >= 2:
                preceding = source_lines[i - 2:i]
                blanks = sum(1 for p in preceding if p.strip() == "")
                if blanks < 2:
                    issues.append({"file": filename, "line": i + 1,
                                    "issue": "Expected 2 blank lines before top-level def/class",
                                    "severity": "Low"})
    return issues


# =========================================================================
# 3. COMMENT & DOCSTRING ANALYZER
# =========================================================================

FILLER_PATTERNS = [
    r'^\s*#\s*(fix\s*this|todo|fixme|xxx|code|stuff|do this)\s*$',
    r'^\s*#\s*$',
]
FILLER_RE = [re.compile(p, re.IGNORECASE) for p in FILLER_PATTERNS]


def _is_filler(comment_text):
    return any(p.match(comment_text) for p in FILLER_RE)


def check_comments(tree, source_lines, filename):
    issues = []
    total_code_lines = len([l for l in source_lines if l.strip() and not l.strip().startswith("#")])
    comment_lines = [l for l in source_lines if l.strip().startswith("#")]
    total_comment_lines = len(comment_lines)

    if not ast.get_docstring(tree):
        issues.append({"file": filename, "line": 1,
                        "issue": "Module is missing a top-level docstring",
                        "severity": "Medium"})

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not ast.get_docstring(node):
                kind = "Class" if isinstance(node, ast.ClassDef) else "Function"
                issues.append({"file": filename, "line": node.lineno,
                                "issue": f"{kind} '{node.name}' is missing a docstring",
                                "severity": "Medium"})

    for i, line in enumerate(source_lines, start=1):
        if line.strip().startswith("#") and _is_filler(line):
            issues.append({"file": filename, "line": i,
                            "issue": "Comment appears to be filler / non-descriptive",
                            "severity": "Low"})

    ratio = round(total_comment_lines / total_code_lines, 2) if total_code_lines else 0
    if ratio < 0.1:
        issues.append({"file": filename, "line": None,
                        "issue": f"Low comment-to-code ratio ({ratio}); consider adding more explanatory comments",
                        "severity": "Low"})

    return issues, ratio


# =========================================================================
# 4. COMPLEXITY ANALYZER
# =========================================================================

DECISION_NODES = (
    ast.If, ast.For, ast.While, ast.ExceptHandler,
    ast.With, ast.Assert, ast.BoolOp, ast.comprehension,
)
COMPLEXITY_THRESHOLD = 10
NESTING_THRESHOLD = 4
LONG_FUNCTION_THRESHOLD = 50


class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.complexity = 1

    def generic_visit(self, node):
        if isinstance(node, DECISION_NODES):
            self.complexity += 1
        super().generic_visit(node)


def _max_nesting_depth(node, depth=0):
    max_depth = depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
            max_depth = max(max_depth, _max_nesting_depth(child, depth + 1))
        else:
            max_depth = max(max_depth, _max_nesting_depth(child, depth))
    return max_depth


def check_complexity(tree, filename):
    issues = []
    metrics = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            visitor = ComplexityVisitor()
            visitor.visit(node)
            complexity = visitor.complexity
            nesting = _max_nesting_depth(node)
            length = (node.end_lineno - node.lineno + 1) if hasattr(node, "end_lineno") else None

            metrics.append({"function": node.name, "line": node.lineno,
                             "complexity": complexity, "nesting_depth": nesting,
                             "length": length})

            if complexity > COMPLEXITY_THRESHOLD:
                issues.append({"file": filename, "line": node.lineno,
                                "issue": f"Function '{node.name}' has high cyclomatic complexity ({complexity}); consider refactoring",
                                "severity": "High"})
            if nesting > NESTING_THRESHOLD:
                issues.append({"file": filename, "line": node.lineno,
                                "issue": f"Function '{node.name}' has deep nesting (depth {nesting}); consider flattening logic",
                                "severity": "Medium"})
            if length and length > LONG_FUNCTION_THRESHOLD:
                issues.append({"file": filename, "line": node.lineno,
                                "issue": f"Function '{node.name}' is long ({length} lines); consider splitting into smaller functions",
                                "severity": "Medium"})
    return issues, metrics


# =========================================================================
# 5. NAMING CONVENTION CHECKER
# =========================================================================

SNAKE_CASE_RE = re.compile(r'^[a-z_][a-z0-9_]*$')
PASCAL_CASE_RE = re.compile(r'^[A-Z][a-zA-Z0-9]*$')
UPPER_SNAKE_RE = re.compile(r'^[A-Z_][A-Z0-9_]*$')


class NamingChecker(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.issues = []

    def _add_issue(self, node, name, expected):
        self.issues.append({"file": self.filename, "line": node.lineno,
                             "identifier": name,
                             "issue": f"'{name}' does not follow {expected} convention",
                             "severity": "Medium"})

    def visit_FunctionDef(self, node):
        if not SNAKE_CASE_RE.match(node.name) and not (
            node.name.startswith("__") and node.name.endswith("__")
        ):
            self._add_issue(node, node.name, "snake_case")
        for arg in node.args.args:
            if not SNAKE_CASE_RE.match(arg.arg) and arg.arg != "self":
                self._add_issue(node, arg.arg, "snake_case (parameter)")
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node):
        if not PASCAL_CASE_RE.match(node.name):
            self._add_issue(node, node.name, "PascalCase")
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id
                if name.isupper():
                    if not UPPER_SNAKE_RE.match(name):
                        self._add_issue(node, name, "UPPER_SNAKE_CASE (constant)")
                else:
                    if not SNAKE_CASE_RE.match(name):
                        self._add_issue(node, name, "snake_case (variable)")
        self.generic_visit(node)


def check_naming(tree, filename):
    checker = NamingChecker(filename)
    checker.visit(tree)
    return checker.issues


# =========================================================================
# 6. UNUSED IMPORTS & UNUSED VARIABLES CHECKER   (NEW in Phase 2)
# =========================================================================

def check_unused_imports(tree, filename):
    """Flags imported names that are never referenced anywhere in the file."""
    issues = []
    imported_names = {}   # name -> line number

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split(".")[0]
                imported_names[name] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    continue
                name = alias.asname or alias.name
                imported_names[name] = node.lineno

    used_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used_names.add(node.id)
        elif isinstance(node, ast.Attribute):
            # captures cases like `os.path` -> counts 'os' as used via Name node already
            pass

    for name, line in imported_names.items():
        if name not in used_names:
            issues.append({"file": filename, "line": line,
                            "issue": f"Imported name '{name}' is never used",
                            "severity": "Low"})
    return issues


def check_unused_variables(tree, filename):
    """Flags local variables assigned inside a function but never read afterward."""
    issues = []

    for func in ast.walk(tree):
        if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        assigned = {}   # name -> line number (first assignment)
        used = set()

        for node in ast.walk(func):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    if node.id not in assigned:
                        assigned[node.id] = node.lineno
                elif isinstance(node.ctx, ast.Load):
                    used.add(node.id)

        for name, line in assigned.items():
            if name not in used and not name.startswith("_"):
                issues.append({"file": filename, "line": line,
                                "issue": f"Variable '{name}' in function '{func.name}' is assigned but never used",
                                "severity": "Low"})
    return issues


# =========================================================================
# 7. SCORING, GRADING & REPORT GENERATION
# =========================================================================

SEVERITY_WEIGHTS = {"High": 5, "Medium": 3, "Low": 1}

# Grade thresholds — tune these to taste
GRADE_THRESHOLDS = [
    (90, "Best"),
    (75, "Good"),
    (50, "Average"),
    (0,  "Poor"),
]


def compute_score(issues, total_lines):
    if total_lines == 0:
        return 100
    penalty = sum(SEVERITY_WEIGHTS.get(i.get("severity", "Low"), 1) for i in issues)
    normalized_penalty = penalty / max(1, total_lines / 30)
    return max(0, round(100 - normalized_penalty, 1))


def compute_grade(score):
    """Maps a numeric score to a Best / Good / Average / Poor label."""
    for threshold, label in GRADE_THRESHOLDS:
        if score >= threshold:
            return label
    return "Poor"


def print_report(file_report):
    filename = file_report["filename"]
    issues = file_report["issues"]
    score = file_report["score"]
    grade = file_report["grade"]

    print("=" * 70)
    print(f"FILE: {filename}")
    print(f"QUALITY SCORE: {score}/100   |   GRADE: {grade}")
    print(f"COMMENT-TO-CODE RATIO: {file_report['comment_ratio']}")
    print("-" * 70)

    if not issues:
        print("No issues found.")
    else:
        order = {"High": 0, "Medium": 1, "Low": 2}
        issues_sorted = sorted(issues, key=lambda x: (order.get(x.get("severity", "Low"), 3), x.get("line") or 0))
        for issue in issues_sorted:
            line = issue.get("line")
            line_str = str(line) if line is not None else "-"
            print(f"[{issue['severity']:<6}] Line {line_str:<5} - {issue['issue']}")

    if file_report["complexity_metrics"]:
        print("-" * 70)
        print("FUNCTION COMPLEXITY:")
        for m in file_report["complexity_metrics"]:
            print(f"  {m['function']:<25} line {m['line']:<5} "
                  f"complexity={m['complexity']:<3} nesting={m['nesting_depth']:<2} "
                  f"length={m['length']}")
    print()


def print_summary(all_reports):
    print("#" * 70)
    print("OVERALL SUMMARY")
    print("#" * 70)
    total_files = len(all_reports)
    avg_score = round(sum(r["score"] for r in all_reports) / total_files, 1) if total_files else 0
    overall_grade = compute_grade(avg_score)
    total_issues = sum(len(r["issues"]) for r in all_reports)

    print(f"Files analyzed: {total_files}")
    print(f"Total issues found: {total_issues}")
    print(f"Average quality score: {avg_score}/100   |   OVERALL GRADE: {overall_grade}")
    print()

    grade_counts = {}
    for r in all_reports:
        grade_counts[r["grade"]] = grade_counts.get(r["grade"], 0) + 1
    print("Grade distribution:")
    for label in ["Best", "Good", "Average", "Poor"]:
        if label in grade_counts:
            print(f"  {label:<8}: {grade_counts[label]} file(s)")
    print()

    worst = sorted(all_reports, key=lambda r: r["score"])[:5]
    print("Lowest scoring files:")
    for r in worst:
        print(f"  {r['filename']:<40} {r['score']}/100  ({r['grade']})")


def export_markdown(all_reports, out_path):
    lines = ["# Code Quality Report\n"]
    total_files = len(all_reports)
    avg_score = round(sum(r["score"] for r in all_reports) / total_files, 1) if total_files else 0
    overall_grade = compute_grade(avg_score)
    lines.append(f"**Files analyzed:** {total_files}  ")
    lines.append(f"**Average quality score:** {avg_score}/100  ")
    lines.append(f"**Overall grade:** {overall_grade}\n")

    for r in all_reports:
        lines.append(f"## {r['filename']}")
        lines.append(f"- **Score:** {r['score']}/100")
        lines.append(f"- **Grade:** {r['grade']}")
        lines.append(f"- **Comment-to-code ratio:** {r['comment_ratio']}")
        if r["issues"]:
            lines.append("\n| Severity | Line | Issue |")
            lines.append("|---|---|---|")
            for issue in r["issues"]:
                lines.append(f"| {issue['severity']} | {issue.get('line', '-')} | {issue['issue']} |")
        else:
            lines.append("- No issues found.")
        lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# =========================================================================
# 8. MAIN ORCHESTRATION
# =========================================================================

def analyze_file(filepath):
    source, source_lines = read_source(filepath)
    tree, error = parse_source(source, filepath)

    if error:
        return {"filename": filepath,
                "issues": [{"file": filepath, "line": None, "issue": error, "severity": "High"}],
                "complexity_metrics": [], "comment_ratio": 0, "score": 0, "grade": "Poor"}

    issues = []
    issues += check_style(source_lines, filepath)

    comment_issues, comment_ratio = check_comments(tree, source_lines, filepath)
    issues += comment_issues

    complexity_issues, complexity_metrics = check_complexity(tree, filepath)
    issues += complexity_issues

    issues += check_naming(tree, filepath)
    issues += check_unused_imports(tree, filepath)
    issues += check_unused_variables(tree, filepath)

    score = compute_score(issues, len(source_lines))
    grade = compute_grade(score)

    return {"filename": filepath, "issues": issues,
            "complexity_metrics": complexity_metrics,
            "comment_ratio": comment_ratio, "score": score, "grade": grade}


def main():
    parser = argparse.ArgumentParser(description="Python Code Quality & Comment Analyzer (Phase 2)")
    parser.add_argument("path", help="Path to a .py file or a directory of Python files")
    parser.add_argument("--export", help="Export a Markdown report to the given path", default=None)
    args = parser.parse_args()

    py_files = find_python_files(args.path)
    if not py_files:
        print(f"No Python files found at: {args.path}")
        sys.exit(1)

    all_reports = []
    for filepath in py_files:
        file_report = analyze_file(filepath)
        all_reports.append(file_report)
        print_report(file_report)

    print_summary(all_reports)

    if args.export:
        export_markdown(all_reports, args.export)
        print(f"\nMarkdown report exported to: {args.export}")


if __name__ == "__main__":
    main()
