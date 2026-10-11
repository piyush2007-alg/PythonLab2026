"""Python Code Quality Analyzer - Automated Fixer Engine."""

import ast
import re
from typing import Dict, List, Tuple, Any, Optional

FILLER_COMMENT_RE = re.compile(
    r"^\s*#\s*(fix\s*this|todo|fixme|xxx|code|stuff|do this)\s*$",
    re.IGNORECASE
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

    indent = len(line) - len(line.lstrip())
    indent_str = line[:indent]

    return [indent_str + p if not p.startswith(" ") else p for p in parts] if parts else [line]


def _format_assignment_spacing(line: str) -> str:
    """Add spacing around '=' assignment operator outside quotes and comments."""
    if "=" not in line or line.strip().startswith("#"):
        return line

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
            out.append("".join(chars[i:]))
            break

        if c == "=" and not in_sq and not in_dq:
            prev_c = chars[i - 1] if i > 0 else ""
            next_c = chars[i + 1] if i + 1 < n else ""

            is_compound = (
                prev_c in ("=", "!", "<", ">", "+", "-", "*", "/", "%", "&", "|", "^")
                or next_c in ("=",)
            )

            if not is_compound:
                if out and out[-1] not in (" ", "\t", "("):
                    out.append(" ")
                out.append("=")
                if next_c and next_c not in (" ", "\t", ")"):
                    out.append(" ")
                i += 1
                continue

        out.append(c)
        i += 1

    return "".join(out)


def _get_unused_import_lines(tree: ast.AST) -> Dict[int, str]:
    """Find line numbers of unused import statements."""
    imported_names = {}

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
    """Analyze and apply automated fixes to Python code."""
    from analyzer.engine import analyze_code

    report_before = analyze_code(source, filename)
    score_before = report_before["score"]
    grade_before = report_before["grade"]

    fixes = []
    lines = source.splitlines()

    unused_import_lines = {}
    try:
        tree = ast.parse(source, filename=filename)
        unused_import_lines = _get_unused_import_lines(tree)
    except SyntaxError:
        pass

    transformed_lines: List[str] = []

    for lineno, line in enumerate(lines, start=1):
        if lineno in unused_import_lines:
            import_name = unused_import_lines[lineno]
            if line.strip().startswith(("import ", "from ")):
                fixes.append(f"Line {lineno}: Removed unused import '{import_name}'")
                continue

        if line.strip().startswith("#") and FILLER_COMMENT_RE.match(line):
            fixes.append(f"Line {lineno}: Removed non-descriptive filler comment '{line.strip()}'")
            continue

        if "\t" in line:
            expanded = line.expandtabs(4)
            if expanded != line:
                fixes.append(f"Line {lineno}: Converted indentation tabs to 4 spaces")
                line = expanded

        trimmed = line.rstrip()
        if trimmed != line:
            fixes.append(f"Line {lineno}: Trimmed trailing whitespace")
            line = trimmed

        if ";" in line and not line.strip().startswith("#"):
            split_parts = _split_semicolons_in_line(line)
            if len(split_parts) > 1:
                fixes.append(f"Line {lineno}: Split {len(split_parts)} semicolon statements onto separate lines")
                for part in split_parts:
                    formatted_part = _format_assignment_spacing(part)
                    transformed_lines.append(formatted_part)
                continue

        formatted = _format_assignment_spacing(line)
        if formatted != line:
            fixes.append(f"Line {lineno}: Added spacing around '=' operator")
            line = formatted

        transformed_lines.append(line)

    final_lines: List[str] = []
    i = 0
    while i < len(transformed_lines):
        line = transformed_lines[i]
        is_top_level_def_or_class = (
            (line.startswith("def ") or line.startswith("class "))
            and not line.startswith("    ")
        )

        if is_top_level_def_or_class and len(final_lines) > 0:
            blank_count = 0
            idx = len(final_lines) - 1
            while idx >= 0 and final_lines[idx].strip() == "":
                blank_count += 1
                idx -= 1

            if idx >= 0 and blank_count < 2:
                missing = 2 - blank_count
                for _ in range(missing):
                    final_lines.append("")
                fixes.append(f"Line {i + 1}: Added 2 blank lines before top-level '{line.split()[0]}'")

        final_lines.append(line)
        i += 1

    fixed_code = "\n".join(final_lines)
    if fixed_code and not fixed_code.endswith("\n"):
        fixed_code += "\n"
        fixes.append("End of file: Ensured standard newline")

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


def auto_fix_file(file_path: str) -> Dict[str, Any]:
    """Auto-fix a Python file on disk in place and return summary."""
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    result = auto_fix_code(source, file_path)
    if result["fixes_count"] > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(result["fixed_code"])

    return result
