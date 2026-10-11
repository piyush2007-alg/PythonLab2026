"""Python Code Quality & Comment Analyzer Package."""

from analyzer.engine import (
    find_python_files,
    read_source,
    parse_source,
    check_style,
    check_comments,
    check_complexity,
    check_naming,
    check_unused_imports,
    check_unused_variables,
    compute_score,
    compute_grade,
    analyze_code,
    analyze_file,
    MAX_LINE_LENGTH,
    SEVERITY_WEIGHTS,
    GRADE_THRESHOLDS,
)
from analyzer.fixer import (
    auto_fix_code,
    auto_fix_file,
)
from analyzer.report import (
    print_report,
    print_summary,
    export_report,
    generate_markdown_report,
)

__all__ = [
    "find_python_files",
    "read_source",
    "parse_source",
    "check_style",
    "check_comments",
    "check_complexity",
    "check_naming",
    "check_unused_imports",
    "check_unused_variables",
    "compute_score",
    "compute_grade",
    "analyze_code",
    "analyze_file",
    "auto_fix_code",
    "auto_fix_file",
    "print_report",
    "print_summary",
    "export_report",
    "generate_markdown_report",
    "MAX_LINE_LENGTH",
    "SEVERITY_WEIGHTS",
    "GRADE_THRESHOLDS",
]
