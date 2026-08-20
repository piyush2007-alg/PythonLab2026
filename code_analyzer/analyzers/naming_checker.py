"""
naming_checker.py
Checks Python identifiers (functions, variables, classes) against
standard naming conventions:
    - functions/variables -> snake_case
    - classes             -> PascalCase
    - constants           -> UPPER_SNAKE_CASE
"""

import ast
import re

SNAKE_CASE_RE = re.compile(r'^[a-z_][a-z0-9_]*$')
PASCAL_CASE_RE = re.compile(r'^[A-Z][a-zA-Z0-9]*$')
UPPER_SNAKE_RE = re.compile(r'^[A-Z_][A-Z0-9_]*$')


class NamingChecker(ast.NodeVisitor):
    def __init__(self):
        self.issues = []

    def check(self, tree, filename):
        self.filename = filename
        self.issues = []
        self.visit(tree)
        return self.issues

    def _add_issue(self, node, name, expected):
        self.issues.append({
            "file": self.filename,
            "line": node.lineno,
            "identifier": name,
            "issue": f"'{name}' does not follow {expected} convention",
            "severity": "Medium",
        })

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
        # Only check simple module/class-level constant-looking assignments
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id
                # Heuristic: if written in all caps already treat as constant,
                # else expect snake_case for regular variables.
                if name.isupper():
                    if not UPPER_SNAKE_RE.match(name):
                        self._add_issue(node, name, "UPPER_SNAKE_CASE (constant)")
                else:
                    if not SNAKE_CASE_RE.match(name):
                        self._add_issue(node, name, "snake_case (variable)")
        self.generic_visit(node)


def analyze(tree, filename):
    checker = NamingChecker()
    return checker.check(tree, filename)
