"""
file_parser.py
Handles reading Python source files and safely parsing them into an AST.
"""

import ast
import os


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
