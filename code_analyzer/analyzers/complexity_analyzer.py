"""
complexity_analyzer.py
Computes a simple cyclomatic complexity score and nesting depth
for each function using AST traversal (no external dependency required).

Cyclomatic complexity approximation:
    1 (base path) + number of decision points
    (if, elif, for, while, except, with, boolean ops, comprehensions)
"""

import ast

DECISION_NODES = (
    ast.If, ast.For, ast.While, ast.ExceptHandler,
    ast.With, ast.Assert, ast.BoolOp,
    ast.comprehension,
)

COMPLEXITY_THRESHOLD = 10
NESTING_THRESHOLD = 4
LONG_FUNCTION_THRESHOLD = 50  # lines


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


def analyze(tree, filename):
    issues = []
    metrics = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            visitor = ComplexityVisitor()
            visitor.visit(node)
            complexity = visitor.complexity
            nesting = _max_nesting_depth(node)
            length = (node.end_lineno - node.lineno + 1) if hasattr(node, "end_lineno") else None

            metrics.append({
                "function": node.name,
                "line": node.lineno,
                "complexity": complexity,
                "nesting_depth": nesting,
                "length": length,
            })

            if complexity > COMPLEXITY_THRESHOLD:
                issues.append({
                    "file": filename,
                    "line": node.lineno,
                    "issue": f"Function '{node.name}' has high cyclomatic complexity ({complexity}); consider refactoring",
                    "severity": "High",
                })

            if nesting > NESTING_THRESHOLD:
                issues.append({
                    "file": filename,
                    "line": node.lineno,
                    "issue": f"Function '{node.name}' has deep nesting (depth {nesting}); consider flattening logic",
                    "severity": "Medium",
                })

            if length and length > LONG_FUNCTION_THRESHOLD:
                issues.append({
                    "file": filename,
                    "line": node.lineno,
                    "issue": f"Function '{node.name}' is long ({length} lines); consider splitting into smaller functions",
                    "severity": "Medium",
                })

    return issues, metrics
