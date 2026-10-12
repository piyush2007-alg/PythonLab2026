"""Python Code Quality & Comment Analyzer.

Command-line and Web frontend for reviewing and auto-fixing Python source files.
Checks style, documentation, complexity, naming, unused imports and variables,
scoring each file from 0 to 100 with an actionable quality grade.
"""

import argparse
import sys

from analyzer import (
    find_python_files,
    analyze_file,
    auto_fix_file,
    print_report,
    print_summary,
    export_report,
)


def run_web(host="127.0.0.1", port=5000, open_browser=True):
    """Start the Neumorphic Web Frontend server."""
    from server import start_server
    start_server(host=host, port=port, open_browser=open_browser)


def apply_fixes_to_files(files):
    """Auto-fix a list of files on disk and report improvements."""
    print("=" * 70)
    print(" 🛠️  AUTOMATED CODE FIXER - APPLYING REPAIRS")
    print("=" * 70)
    total_fixes = 0

    for fpath in files:
        result = auto_fix_file(fpath)
        fixes_count = result["fixes_count"]
        total_fixes += fixes_count
        score_before = result["score_before"]
        score_after = result["score_after"]

        print(f"\nFILE: {fpath}")
        print(f"  Score: {score_before}/100 ({result['grade_before']}) -> {score_after}/100 ({result['grade_after']})")
        if fixes_count > 0:
            print(f"  Fixes Applied ({fixes_count}):")
            for fix in result["fixes_applied"]:
                print(f"    + {fix}")
        else:
            print("  No automated style fixes needed.")

    print("\n" + "=" * 70)
    print(f"Auto-fix completed across {len(files)} file(s). Total repairs applied: {total_fixes}")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Python Code Quality & Comment Analyzer")
    parser.add_argument("path", nargs="?", default=None, help="Path to a .py file or directory")
    parser.add_argument("--export", metavar="FILE", help="Export the report to a Markdown file")
    parser.add_argument("--fix", action="store_true", help="Automatically fix PEP 8 style, semicolon statements, spacing, and unused imports in place")
    parser.add_argument("--web", action="store_true", help="Launch the interactive Neumorphic Web Frontend")
    parser.add_argument("--port", type=int, default=5000, help="Web server port (default: 5000)")
    parser.add_argument("--host", default="127.0.0.1", help="Web server host (default: 127.0.0.1)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open browser on web launch")
    args = parser.parse_args()

    if args.web or (not args.path and len(sys.argv) == 1):
        run_web(host=args.host, port=args.port, open_browser=not args.no_browser)
        return

    if not args.path:
        parser.print_help()
        sys.exit(1)

    files = find_python_files(args.path)
    if not files:
        print(f"No Python files found at: {args.path}")
        sys.exit(1)

    if args.fix:
        apply_fixes_to_files(files)

    reports = [analyze_file(f) for f in files]
    for r in reports:
        print_report(r)
    print_summary(reports)

    if args.export:
        export_report(reports, args.export)
        print(f"Markdown report exported to: {args.export}")


if __name__ == "__main__":
    main()