# Python Code Quality & Comment Analyzer

A command-line tool that analyzes Python source code for coding standards,
comment/docstring quality, code complexity, and naming conventions — then
generates a scored quality report with improvement suggestions.

## Features

- **Style Checker** — flags PEP 8-style issues: long lines, trailing
  whitespace, tabs, multiple statements per line, missing blank lines
  before functions/classes, missing whitespace around operators.
- **Comment Analyzer** — checks docstring coverage (module/class/function),
  comment-to-code ratio, and flags filler/non-descriptive comments.
- **Complexity Analyzer** — computes cyclomatic complexity, nesting depth,
  and function length using AST traversal (no external dependencies).
- **Naming Convention Checker** — verifies snake_case for functions and
  variables, PascalCase for classes, UPPER_SNAKE_CASE for constants.
- **Report Generator** — produces a per-file quality score (out of 100),
  a console report, an overall summary, and an optional Markdown export.

## Project Structure

```
code_analyzer/
├── main.py                        # CLI entry point
├── analyzers/
│   ├── style_checker.py
│   ├── comment_analyzer.py
│   ├── complexity_analyzer.py
│   └── naming_checker.py
├── report/
│   └── report_generator.py
├── utils/
│   └── file_parser.py
├── sample_inputs/
│   ├── sample_bad.py               # intentionally low-quality file
│   └── sample_good.py              # well-documented reference file
└── README.md
```

## Requirements

- Python 3.8+
- No external libraries required (built entirely on the standard library:
  `ast`, `re`, `os`, `argparse`)

## Usage

Analyze a single file:
```bash
python main.py path/to/file.py
```

Analyze an entire directory (recursively):
```bash
python main.py path/to/project/
```

Export a Markdown report:
```bash
python main.py path/to/project/ --export report.md
```

## How Scoring Works

Each file starts at 100 points. Issues are weighted by severity
(High = 5, Medium = 3, Low = 1) and the total penalty is normalized
against file length, so larger files aren't penalized unfairly for
having more total lines.

## Extending the Tool

- Add new checks by extending any file in `analyzers/` — each module
  returns a list of issue dictionaries with `file`, `line`, `issue`,
  and `severity` keys, which `report_generator.py` consumes generically.
- Swap in `pycodestyle` or `radon` for more rigorous checks by replacing
  the relevant analyzer's internals while keeping the same output format.
- Add an HTML/PDF export by extending `report_generator.py` (e.g., with
  `jinja2` templating) alongside the existing `export_markdown`.

## Sample Output

Running against `sample_inputs/sample_bad.py` produces a report showing
issues like missing docstrings, non-PascalCase class names, deep nesting,
and long lines — with a resulting score around 65/100.

Running against `sample_inputs/sample_good.py` (fully documented, simple
functions) produces a score around 99/100.
