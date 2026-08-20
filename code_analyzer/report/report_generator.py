"""
report_generator.py
Aggregates issues from all analyzers into a per-file and overall
quality score, and prints/exports a readable report.
"""

SEVERITY_WEIGHTS = {"High": 5, "Medium": 3, "Low": 1}


def compute_score(issues, total_lines):
    """Simple scoring: start at 100, subtract weighted penalty per issue,
    normalized loosely by file size so large files aren't unfairly punished."""
    if total_lines == 0:
        return 100
    penalty = sum(SEVERITY_WEIGHTS.get(i.get("severity", "Low"), 1) for i in issues)
    normalized_penalty = penalty / max(1, total_lines / 30)
    score = max(0, round(100 - normalized_penalty, 1))
    return score


def print_report(file_report):
    """file_report: dict with filename, issues, complexity_metrics, comment_ratio, score"""
    filename = file_report["filename"]
    issues = file_report["issues"]
    score = file_report["score"]

    print("=" * 70)
    print(f"FILE: {filename}")
    print(f"QUALITY SCORE: {score}/100")
    print(f"COMMENT-TO-CODE RATIO: {file_report['comment_ratio']}")
    print("-" * 70)

    if not issues:
        print("No issues found. ✅")
    else:
        # Sort by severity then line number
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
    total_issues = sum(len(r["issues"]) for r in all_reports)

    print(f"Files analyzed: {total_files}")
    print(f"Total issues found: {total_issues}")
    print(f"Average quality score: {avg_score}/100")
    print()

    # Worst files first
    worst = sorted(all_reports, key=lambda r: r["score"])[:5]
    print("Lowest scoring files:")
    for r in worst:
        print(f"  {r['filename']:<40} {r['score']}/100")


def export_markdown(all_reports, out_path):
    lines = ["# Code Quality Report\n"]
    total_files = len(all_reports)
    avg_score = round(sum(r["score"] for r in all_reports) / total_files, 1) if total_files else 0
    lines.append(f"**Files analyzed:** {total_files}  ")
    lines.append(f"**Average quality score:** {avg_score}/100\n")

    for r in all_reports:
        lines.append(f"## {r['filename']}")
        lines.append(f"- **Score:** {r['score']}/100")
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
