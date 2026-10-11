"""Python Code Quality Analyzer - Report Exporter and CLI Printers."""

from typing import Dict, List, Any
from analyzer.engine import compute_grade


def print_report(report: Dict[str, Any]):
    """Print readable terminal report for a single file."""
    print("=" * 70)
    print(f"FILE: {report['filename']}")
    print(f"QUALITY SCORE: {report['score']}/100   |   GRADE: {report['grade']}")
    print(f"COMMENT-TO-CODE RATIO: {report['comment_ratio']}")
    print("-" * 70)

    if not report["issues"]:
        print("No issues found. Excellent code!")
    else:
        order = {"High": 0, "Medium": 1, "Low": 2}
        for issue in sorted(report["issues"], key=lambda x: (order.get(x.get("severity", "Low"), 3), x.get("line") or 0)):
            line = issue.get("line")
            print(f"[{issue['severity']:<6}] Line {str(line) if line is not None else '-':<5} - {issue['issue']}")

    if report.get("complexity_metrics"):
        print("-" * 70)
        print("FUNCTION COMPLEXITY:")
        for m in report["complexity_metrics"]:
            print(f"  {m['function']:<25} line {m['line']:<5} complexity={m['complexity']:<3} nesting={m['nesting_depth']:<2} length={m['length']}")
    print()


def print_summary(reports: List[Dict[str, Any]]):
    """Print summary metrics across all analyzed files."""
    total = len(reports)
    avg = round(sum(r["score"] for r in reports) / total, 1) if total else 0
    print("#" * 70)
    print("OVERALL SUMMARY")
    print("#" * 70)
    print(f"Files analyzed: {total}")
    print(f"Total issues found: {sum(len(r['issues']) for r in reports)}")
    print(f"Average quality score: {avg}/100   |   OVERALL GRADE: {compute_grade(avg)}")
    print()


def generate_markdown_report(reports: List[Dict[str, Any]]) -> str:
    """Generate Markdown report string from multiple analysis reports."""
    total = len(reports)
    avg = round(sum(r["score"] for r in reports) / total, 1) if total else 0
    lines = [
        "# Python Code Quality & Comment Analyzer Report",
        "",
        f"- **Files analyzed:** {total}",
        f"- **Average quality score:** {avg}/100",
        f"- **Overall grade:** {compute_grade(avg)}",
        f"- **Total issues detected:** {sum(len(r['issues']) for r in reports)}",
        ""
    ]

    for report in reports:
        lines.extend([
            f"## {report['filename']}",
            f"- **Score:** {report['score']}/100",
            f"- **Grade:** {report['grade']}",
            f"- **Comment-to-code ratio:** {report['comment_ratio']}",
            f"- **Lines of code:** {report.get('total_lines', '-')}",
            "",
            "| Severity | Line | Category | Issue |",
            "|---|---|---|---|"
        ])
        if report["issues"]:
            for issue in report["issues"]:
                line = issue.get("line")
                cat = issue.get("category", "General")
                message = issue["issue"].replace("|", "\\|")
                lines.append(f"| {issue['severity']} | {line if line is not None else '-'} | {cat} | {message} |")
        else:
            lines.append("| - | - | - | No issues found. Excellent code! |")
        lines.append("")

        if report.get("complexity_metrics"):
            lines.extend([
                "### Function Complexity Metrics",
                "",
                "| Function | Line | Cyclomatic Complexity | Nesting Depth | Length (lines) |",
                "|---|---|---|---|---|"
            ])
            for m in report["complexity_metrics"]:
                lines.append(f"| `{m['function']}` | {m['line']} | {m['complexity']} | {m['nesting_depth']} | {m['length']} |")
            lines.append("")

    return "\n".join(lines)


def export_report(reports: List[Dict[str, Any]], output_path: str):
    """Save markdown report to specified output path."""
    content = generate_markdown_report(reports)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
