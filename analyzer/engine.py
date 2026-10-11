"""Python Code Quality & Comment Analyzer - AST Engine.

Provides AST-based inspection of Python code for:
- PEP 8 style issues
- Comment and docstring quality and ratio
- Cyclomatic complexity, nesting depth, and function length
- Naming conventions (snake_case, PascalCase, UPPER_SNAKE_CASE)
- Unused imports and unused local variables
- Quality scoring and grading (0-100, Best/Good/Average/Poor)
"""

import ast
import os
import re
from typing import Dict, List, Optional, Tuple, Any

MAX_LINE_LENGTH = 79
SEVERITY_WEIGHTS = {"High": 5, "Medium": 3, "Low": 1}
GRADE_THRESHOLDS = [(90, "Best"), (75, "Good"), (50, "Average"), (0, "Poor")]

SNAKE_RE = re.compile(r"^[a-z_][a-z0-9_]*$")
PASCAL_RE = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
UPPER_SNAKE_RE = re.compile(r"^[A-Z_][A-Z0-9_]*$")
OP_RE = re.compile(r"[a-zA-Z0-9_)\]]=[a-zA-Z0-9_(\-]")
FILLER_RE = [
    re.compile(r"^\s*#\s*(fix\s*this|todo|fixme|xxx|code|stuff|do this)\s*$", re.I),
    re.compile(r"^\s*#\s*$")
]
DECISION_NODES = (
    ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With, ast.Assert, ast.BoolOp, ast.comprehension
)


def find_python_files(path: str) -> List[str]:
    """Recursively find all Python files in the given directory or return single file."""
    if os.path.isfile(path) and path.endswith(".py"):
        return [path]
    files = []
    for root, dirs, names in os.walk(path):
        # Exclude hidden directories, virtual environments, and web assets
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("__pycache__", "node_modules", "web", "venv", ".venv")]
        for name in names:
            if name.endswith(".py"):
                files.append(os.path.join(root, name))
    return sorted(files)


def read_source(path: str) -> Tuple[str, List[str]]:
    """Read source code from disk returning raw text and lines."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return text, text.splitlines()


def parse_source(source: str, filepath: str = "<source>") -> Tuple[Optional[ast.AST], Optional[str]]:
    """Parse Python source into AST, returning syntax error string if invalid."""
    try:
        return ast.parse(source, filename=filepath), None
    except SyntaxError as e:
        return None, f"SyntaxError: {e.msg} at line {e.lineno}"


def check_style(lines: List[str], filename: str) -> List[Dict[str, Any]]:
    """Check lines for PEP 8 styling violations."""
    issues = []

    for i, line in enumerate(lines, start=1):
        s = line.rstrip("\n")

        if len(s) > MAX_LINE_LENGTH:
            issues.append({
                "file": filename,
                "line": i,
                "category": "Style",
                "issue": f"Line exceeds {MAX_LINE_LENGTH} chars ({len(s)})",
                "severity": "Low",
                "tip": f"Break this line across multiple lines or reformat to fit within {MAX_LINE_LENGTH} characters."
            })
        if s != s.rstrip():
            issues.append({
                "file": filename,
                "line": i,
                "category": "Style",
                "issue": "Trailing whitespace",
                "severity": "Low",
                "tip": "Remove unnecessary spaces at the end of the line."
            })
        if "\t" in line:
            issues.append({
                "file": filename,
                "line": i,
                "category": "Style",
                "issue": "Tab character used for indentation",
                "severity": "Medium",
                "tip": "Use 4 spaces instead of tabs for standard Python indentation."
            })
        if ";" in s and not s.strip().startswith("#"):
            issues.append({
                "file": filename,
                "line": i,
                "category": "Style",
                "issue": "Multiple statements on one line",
                "severity": "Medium",
                "tip": "Split statements onto separate lines rather than using semicolons."
            })
        if OP_RE.search(s) and "==" not in s:
            issues.append({
                "file": filename,
                "line": i,
                "category": "Style",
                "issue": "Missing whitespace around '='",
                "severity": "Low",
                "tip": "Surround assignment operators with a single space (e.g. 'x = 1')."
            })

    for i, line in enumerate(lines):
        if (line.startswith("def ") or line.startswith("class ")) and i >= 2:
            prev = lines[i-2:i]
            if sum(1 for p in prev if p.strip() == "") < 2:
                issues.append({
                    "file": filename,
                    "line": i + 1,
                    "category": "Style",
                    "issue": "Expected 2 blank lines before top-level def/class",
                    "severity": "Low",
                    "tip": "Add 2 empty lines before top-level class and function definitions per PEP 8."
                })
    return issues


def is_filler_comment(line: str) -> bool:
    """Check if a comment line is vague or filler."""
    return any(p.match(line) for p in FILLER_RE)


def check_comments(tree: ast.AST, lines: List[str], filename: str) -> Tuple[List[Dict[str, Any]], float]:
    """Check docstrings, filler comments, and comment-to-code ratio."""
    issues = []

    if not ast.get_docstring(tree):
        issues.append({
            "file": filename,
            "line": 1,
            "category": "Comments",
            "issue": "Module is missing a top-level docstring",
            "severity": "Medium",
            "tip": "Add a triple-quoted docstring at line 1 explaining the purpose of this module."
        })

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not ast.get_docstring(node):
            kind = "Class" if isinstance(node, ast.ClassDef) else "Function"
            issues.append({
                "file": filename,
                "line": node.lineno,
                "category": "Comments",
                "issue": f"{kind} '{node.name}' is missing a docstring",
                "severity": "Medium",
                "tip": f"Add docstring describing parameters, return value, and purpose of {kind.lower()} '{node.name}'."
            })

    for i, line in enumerate(lines, start=1):
        if line.strip().startswith("#") and is_filler_comment(line):
            issues.append({
                "file": filename,
                "line": i,
                "category": "Comments",
                "issue": "Comment appears to be filler / non-descriptive",
                "severity": "Low",
                "tip": "Replace placeholder comment with meaningful context explaining the 'why' behind the logic."
            })

    code_lines = [l for l in lines if l.strip() and not l.strip().startswith("#")]
    comment_lines = [l for l in lines if l.strip().startswith("#")]
    ratio = round(len(comment_lines) / len(code_lines), 2) if code_lines else 0
    if ratio < 0.1:
        issues.append({
            "file": filename,
            "line": None,
            "category": "Comments",
            "issue": f"Low comment-to-code ratio ({ratio})",
            "severity": "Low",
            "tip": f"Aim for at least 10% explanatory comments (current: {int(ratio*100)}%)."
        })
    return issues, ratio


class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.value = 1

    def generic_visit(self, node):
        if isinstance(node, DECISION_NODES):
            self.value += 1
        super().generic_visit(node)


def max_nesting(node: ast.AST, depth: int = 0) -> int:
    """Calculate maximum block nesting depth within a node."""
    m_depth = depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
            m_depth = max(m_depth, max_nesting(child, depth + 1))
        else:
            m_depth = max(m_depth, max_nesting(child, depth))
    return m_depth


def check_complexity(tree: ast.AST, filename: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Measure function cyclomatic complexity, nesting depth, and line length."""
    issues = []
    metrics = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        visitor = ComplexityVisitor()
        visitor.visit(node)
        complexity = visitor.value
        nesting = max_nesting(node)
        length = (node.end_lineno - node.lineno + 1) if hasattr(node, "end_lineno") and node.end_lineno else 0

        metrics.append({
            "function": node.name,
            "line": node.lineno,
            "complexity": complexity,
            "nesting_depth": nesting,
            "length": length
        })

        if complexity > 10:
            issues.append({
                "file": filename,
                "line": node.lineno,
                "category": "Complexity",
                "issue": f"Function '{node.name}' has high cyclomatic complexity ({complexity})",
                "severity": "High",
                "tip": f"Decompose '{node.name}' into smaller helper functions to keep complexity <= 10."
            })
        if nesting > 4:
            issues.append({
                "file": filename,
                "line": node.lineno,
                "category": "Complexity",
                "issue": f"Function '{node.name}' has deep nesting (depth {nesting})",
                "severity": "Medium",
                "tip": "Use guard clauses, early returns, or helper functions to flatten nested loops/branches."
            })
        if length > 50:
            issues.append({
                "file": filename,
                "line": node.lineno,
                "category": "Complexity",
                "issue": f"Function '{node.name}' is long ({length} lines)",
                "severity": "Medium",
                "tip": "Functions longer than 50 lines often have multiple responsibilities; refactor into modular parts."
            })
    return issues, metrics


class NamingChecker(ast.NodeVisitor):
    def __init__(self, filename: str):
        self.filename = filename
        self.issues = []

    def add(self, node: ast.AST, name: str, expected: str):
        self.issues.append({
            "file": self.filename,
            "line": node.lineno,
            "identifier": name,
            "category": "Naming",
            "issue": f"'{name}' does not follow {expected}",
            "severity": "Medium",
            "tip": f"Rename '{name}' to follow standard Python {expected} styling."
        })

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if not SNAKE_RE.match(node.name) and not (node.name.startswith("__") and node.name.endswith("__")):
            self.add(node, node.name, "snake_case")
        for arg in node.args.args:
            if arg.arg != "self" and not SNAKE_RE.match(arg.arg):
                self.add(node, arg.arg, "snake_case (parameter)")
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        if not PASCAL_RE.match(node.name):
            self.add(node, node.name, "PascalCase")
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id
                if name.isupper() and not UPPER_SNAKE_RE.match(name):
                    self.add(node, name, "UPPER_SNAKE_CASE (constant)")
                elif not name.isupper() and not SNAKE_RE.match(name):
                    self.add(node, name, "snake_case (variable)")
        self.generic_visit(node)


def check_naming(tree: ast.AST, filename: str) -> List[Dict[str, Any]]:
    """Check identifier naming conventions."""
    checker = NamingChecker(filename)
    checker.visit(tree)
    return checker.issues


def check_unused_imports(tree: ast.AST, filename: str) -> List[Dict[str, Any]]:
    """Find imports that are never used in AST."""
    imported = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split(".")[0]
                imported[name] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name != "*":
                    imported[alias.asname or alias.name] = node.lineno

    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    return [{
        "file": filename,
        "line": line,
        "category": "Unused Code",
        "issue": f"Imported name '{name}' is never used",
        "severity": "Low",
        "tip": f"Remove unused import '{name}' to keep dependencies and namespace clean."
    } for name, line in imported.items() if name not in used]


def check_unused_variables(tree: ast.AST, filename: str) -> List[Dict[str, Any]]:
    """Find local variables assigned but never loaded."""
    issues = []
    for func in ast.walk(tree):
        if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        assigned = {}
        used = set()

        for node in ast.walk(func):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    assigned.setdefault(node.id, node.lineno)
                elif isinstance(node.ctx, ast.Load):
                    used.add(node.id)

        for name, line in assigned.items():
            if name not in used and not name.startswith("_"):
                issues.append({
                    "file": filename,
                    "line": line,
                    "category": "Unused Code",
                    "issue": f"Variable '{name}' in function '{func.name}' is assigned but never used",
                    "severity": "Low",
                    "tip": f"Remove '{name}' or prefix with an underscore (_{name}) if intentionally ignored."
                })
    return issues


def compute_score(issues: List[Dict[str, Any]], total_lines: int) -> float:
    """Compute 0-100 quality score penalized by issue severities."""
    if total_lines == 0:
        return 100.0
    penalty = sum(SEVERITY_WEIGHTS.get(i.get("severity", "Low"), 1) for i in issues)
    normalized = penalty / max(1, total_lines / 30)
    return max(0.0, round(100.0 - normalized, 1))


def compute_grade(score: float) -> str:
    """Return qualitative grade for quality score."""
    for threshold, label in GRADE_THRESHOLDS:
        if score >= threshold:
            return label
    return "Poor"


def analyze_code(source: str, filename: str = "<source>") -> Dict[str, Any]:
    """Analyze Python source text in memory."""
    lines = source.splitlines()
    total_lines = len(lines)
    tree, error = parse_source(source, filename)

    if error:
        return {
            "filename": filename,
            "total_lines": total_lines,
            "issues": [{
                "file": filename,
                "line": None,
                "category": "Syntax",
                "issue": error,
                "severity": "High",
                "tip": "Fix the syntax error to allow full AST analysis."
            }],
            "complexity_metrics": [],
            "comment_ratio": 0.0,
            "score": 0.0,
            "grade": "Poor",
            "stats": {
                "high": 1,
                "medium": 0,
                "low": 0,
                "total": 1,
                "code_lines": total_lines,
                "comment_lines": 0
            }
        }

    issues: List[Dict[str, Any]] = []
    issues += check_style(lines, filename)
    comment_issues, comment_ratio = check_comments(tree, lines, filename)
    issues += comment_issues
    complexity_issues, complexity_metrics = check_complexity(tree, filename)
    issues += complexity_issues
    issues += check_naming(tree, filename)
    issues += check_unused_imports(tree, filename)
    issues += check_unused_variables(tree, filename)

    score = compute_score(issues, total_lines)
    grade = compute_grade(score)

    counts = {"High": 0, "Medium": 0, "Low": 0}
    cat_counts = {}
    for issue in issues:
        sev = issue.get("severity", "Low")
        counts[sev] = counts.get(sev, 0) + 1
        cat = issue.get("category", "General")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    code_lines = len([l for l in lines if l.strip() and not l.strip().startswith("#")])
    comment_lines = len([l for l in lines if l.strip().startswith("#")])

    return {
        "filename": filename,
        "total_lines": total_lines,
        "issues": issues,
        "complexity_metrics": complexity_metrics,
        "comment_ratio": comment_ratio,
        "score": score,
        "grade": grade,
        "stats": {
            "high": counts.get("High", 0),
            "medium": counts.get("Medium", 0),
            "low": counts.get("Low", 0),
            "total": len(issues),
            "categories": cat_counts,
            "code_lines": code_lines,
            "comment_lines": comment_lines
        }
    }


def analyze_file(path: str) -> Dict[str, Any]:
    """Analyze Python file on disk."""
    source, _ = read_source(path)
    return analyze_code(source, path)
