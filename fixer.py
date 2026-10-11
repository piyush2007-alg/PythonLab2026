"""Python Code Quality Analyzer - Automated Fixer Engine.

Provides safe, AST and token-informed automated fixes for common PEP 8
and code quality violations:
- Trailing whitespace removal
- Tab-to-spaces indentation normalization (4 spaces)
- Semicolon-delimited multi-statement splitting
- Operator spacing normalization around '='
- Top-level function & class blank line normalization (2 blank lines)
- Unused import statement removal
- Non-descriptive filler comment removal
- Final newline standardization
"""

import ast
import re
from typing import Dict, List, Tuple, Any, Optional

FILLER_COMMENT_RE = re.compile(
    r"^\s*#\s*(fix\s*this|todo|fixme|xxx|code|stuff|do this)\s*$",
    re.IGNORECASE
)
ASSIGN_OP_RE = re.compile(
    r"(?<![=!<>+\-*/%&|^])(?<!\s)=(?!\s)(?![=!<>])"
)


def _split_semicolons_in_line(line: str) -> List[str]:
    """Split line containing semicolons into multiple statements, respecting strings and comments."""
    if ";" not in line or line.strip().startswith("#"):
        return [line]

    parts = []
    current = []
    in_single_quote = False
    in_double_quote = False
    escape = False

    for char in line:
        if escape:
            current.append(char)
            escape = False
            continue

        if char == "\\":
            escape = True
            current.append(char)
            continue

        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
            current.append(char)
            continue

        if char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            current.append(char)
            continue

        if char == "#" and not in_single_quote and not in_double_quote:
            # Comment starts, remainder is comment
            remainder = "".join(current).strip()
            if remainder:
                parts.append(remainder)
            current = []
            break

        if char == ";" and not in_single_quote and not in_double_quote:
            statement = "".join(current).strip()
            if statement:
                parts.append(statement)
            current = []
            continue

        current.append(char)

    remainder = "".join(current).strip()
    if remainder:
        parts.append(remainder)

    # Determine base indentation from original line
    indent = len(line) - len(line.lstrip())
    indent_str = line[:indent]

    return [indent_str + p if not p.startswith(" ") else p for p in parts] if parts else [line]


def _format_assignment_spacing(line: str) -> str:
    """Add spacing around '=' assignment operator outside quotes and comments."""
    if "=" not in line or line.strip().startswith("#"):
        return line

    # Quick check if '=' has missing spaces
    if not re.search(r"[a-zA-Z0-9_)\]]=[a-zA-Z0-9_(\-]", line):
        return line

    out = []
    in_sq = False
    in_dq = False
    escape = False
    chars = list(line)
    n = len(chars)

    i = 0
    while i < n:
        c = chars[i]

        if escape:
            out.append(c)
            escape = False
            i += 1
            continue

        if c == "\\":
            escape = True
            out.append(c)
            i += 1
            continue

        if c == "'" and not in_dq:
            in_sq = not in_sq
            out.append(c)
            i += 1
            continue

        if c == '"' and not in_sq:
            in_dq = not in_dq
            out.append(c)
            i += 1
            continue

        if c == "#" and not in_sq and not in_dq:
            # Rest is comment
            out.append("".join(chars[i:]))
            break

        # Check for single '=' without spaces
        if c == "=" and not in_sq and not in_dq:
            prev_c = chars[i - 1] if i > 0 else ""
            next_c = chars[i + 1] if i + 1 < n else ""

            # Skip if ==, !=, <=, >=, +=, -=, *=, /=
            is_compound = (
                prev_c in ("=", "!", "<", ">", "+", "-", "*", "/", "%", "&", "|", "^")
                or next_c in ("=",)
            )

            if not is_compound:
                # Ensure space before
                if out and out[-1] not in (" ", "\t", "("):
                    out.append(" ")
                out.append("=")
                # Ensure space after
                if next_c and next_c not in (" ", "\t", ")"):
                    out.append(" ")
                i += 1
                continue

        out.append(c)
        i += 1

    return "".join(out)


def _get_unused_import_lines(tree: ast.AST) -> Dict[int, str]:
    """Find line numbers of unused import statements."""
    imported_names = {}  # name -> (lineno, is_from_import, mod_or_alias)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split(".")[0]
                imported_names[name] = (node.lineno, False, alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name != "*":
                    name = alias.asname or alias.name
                    imported_names[name] = (node.lineno, True, name)

    used_names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    unused_lines = {}
    for name, (lineno, is_from, mod) in imported_names.items():
        if name not in used_names:
            unused_lines[lineno] = name

    return unused_lines


def auto_fix_code(source: str, filename: str = "<source>") -> Dict[str, Any]:
    """Analyze and apply automated fixes to Python code.

    Returns:
        dict:
            - original_code: input source
            - fixed_code: modified source
            - fixes_applied: list of description strings
            - fixes_count: total number of fixes
            - score_before: quality score before fixes
            - score_after: quality score after fixes
            - grade_before: grade before fixes
            - grade_after: grade after fixes
    """
    from analyzer import analyze_code

    report_before = analyze_code(source, filename)
    score_before = report_before["score"]
    grade_before = report_before["grade"]

    fixes = []
    lines = source.splitlines()

    # Step 1: Detect unused imports via AST before modifying line numbers
    unused_import_lines = {}
    try:
        tree = ast.parse(source, filename=filename)
        unused_import_lines = _get_unused_import_lines(tree)
    except SyntaxError:
        pass  # If syntax error, skip AST-level removals

    # Step 2: Line-by-line transformations
    transformed_lines: List[str] = []

    for lineno, line in enumerate(lines, start=1):
        # A) Check unused import removal
        if lineno in unused_import_lines:
            import_name = unused_import_lines[lineno]
            # Verify line looks like import statement
            if line.strip().startswith(("import ", "from ")):
                fixes.append(f"Line {lineno}: Removed unused import '{import_name}'")
                continue

        # B) Remove filler comments
        if line.strip().startswith("#") and FILLER_COMMENT_RE.match(line):
            fixes.append(f"Line {lineno}: Removed non-descriptive filler comment '{line.strip()}'")
            continue

        # C) Normalize indentation tabs to 4 spaces
        if "\t" in line:
            expanded = line.expandtabs(4)
            if expanded != line:
                fixes.append(f"Line {lineno}: Converted indentation tabs to 4 spaces")
                line = expanded

        # D) Remove trailing whitespace
        trimmed = line.rstrip()
        if trimmed != line:
            fixes.append(f"Line {lineno}: Trimmed trailing whitespace")
            line = trimmed

        # E) Split semicolon statements
        if ";" in line and not line.strip().startswith("#"):
            split_parts = _split_semicolons_in_line(line)
            if len(split_parts) > 1:
                fixes.append(f"Line {lineno}: Split {len(split_parts)} semicolon statements onto separate lines")
                for part in split_parts:
                    # Apply operator spacing to each part
                    formatted_part = _format_assignment_spacing(part)
                    transformed_lines.append(formatted_part)
                continue

        # F) Format assignment operator spacing
        formatted = _format_assignment_spacing(line)
        if formatted != line:
            fixes.append(f"Line {lineno}: Added spacing around '=' operator")
            line = formatted

        transformed_lines.append(line)

    # Step 3: Normalize blank lines before top-level def and class
    final_lines: List[str] = []
    i = 0
    while i < len(transformed_lines):
        line = transformed_lines[i]
        # Check if top-level def or class
        is_top_level_def_or_class = (
            (line.startswith("def ") or line.startswith("class "))
            and not line.startswith("    ")
        )

        if is_top_level_def_or_class and len(final_lines) > 0:
            # Count trailing blank lines in final_lines
            blank_count = 0
            idx = len(final_lines) - 1
            while idx >= 0 and final_lines[idx].strip() == "":
                blank_count += 1
                idx -= 1

            # If preceded by code/docstring and less than 2 blank lines, insert missing
            if idx >= 0 and blank_count < 2:
                missing = 2 - blank_count
                for _ in range(missing):
                    final_lines.append("")
                fixes.append(f"Line {i + 1}: Added 2 blank lines before top-level '{line.split()[0]}'")

        final_lines.append(line)
        i += 1

    # Step 4: Ensure single trailing newline
    fixed_code = "\n".join(final_lines)
    if fixed_code and not fixed_code.endswith("\n"):
        fixed_code += "\n"
        fixes.append("End of file: Ensured standard newline")

    # Step 5: Verify the fixed code parses and calculate score_after
    report_after = analyze_code(fixed_code, filename)
    score_after = report_after["score"]
    grade_after = report_after["grade"]

    return {
        "original_code": source,
        "fixed_code": fixed_code,
        "fixes_applied": fixes,
        "fixes_count": len(fixes),
        "score_before": score_before,
        "grade_before": grade_before,
        "score_after": score_after,
        "grade_after": grade_after,
        "report_after": report_after
    }
