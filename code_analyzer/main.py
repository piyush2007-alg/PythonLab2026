"""
main.py
Entry point for the Python Code Quality & Comment Analyzer.

Usage:
    python main.py <file_or_directory> [--export report.md]
"""

import argparse
import sys

from utils.file_parser import find_python_files, read_source, parse_source
from analyzers import style_checker, comment_analyzer, complexity_analyzer, naming_checker
from report import report_generator


def analyze_file(filepath):
    source, source_lines = read_source(filepath)
    tree, error = parse_source(source, filepath)

    if error:
        return {
            "filename": filepath,
            "issues": [{"file": filepath, "line": None, "issue": error, "severity": "High"}],
            "complexity_metrics": [],
            "comment_ratio": 0,
            "score": 0,
        }

    issues = []
    issues += style_checker.analyze(source_lines, filepath)
    issues += style_checker.blank_line_check(source_lines, filepath)

    comment_issues, comment_ratio = comment_analyzer.analyze(tree, source_lines, filepath)
    issues += comment_issues

    complexity_issues, complexity_metrics = complexity_analyzer.analyze(tree, filepath)
    issues += complexity_issues

    issues += naming_checker.analyze(tree, filepath)

    score = report_generator.compute_score(issues, len(source_lines))

    return {
        "filename": filepath,
        "issues": issues,
        "complexity_metrics": complexity_metrics,
        "comment_ratio": comment_ratio,
        "score": score,
    }


def main():
    parser = argparse.ArgumentParser(description="Python Code Quality & Comment Analyzer")
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
        report_generator.print_report(file_report)

    report_generator.print_summary(all_reports)

    if args.export:
        report_generator.export_markdown(all_reports, args.export)
        print(f"\nMarkdown report exported to: {args.export}")


if __name__ == "__main__":
    main()
