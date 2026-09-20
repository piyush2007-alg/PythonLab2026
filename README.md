# Python Code Quality & Comment Analyzer

A command-line tool for reviewing Python source files and directories. It
checks style, documentation, complexity, naming conventions, unused imports,
and unused local variables, then prints a scored quality report with practical
issue details.

The analyzer uses only the Python standard library, including `ast`, `argparse`,
`os`, and `re`. No third-party packages are required.

## Features

- Recursively analyze a single Python file or a directory of Python files.
- Report PEP 8-style issues such as long lines, tabs, trailing whitespace,
  semicolons, and missing operator spacing.
- Check module, class, and function docstrings and comment quality.
- Measure function complexity, nesting depth, and function length.
- Check `snake_case`, `PascalCase`, and `UPPER_SNAKE_CASE` naming conventions.
- Find imports that are never referenced and local variables that are never used.
- Score every file from 0 to 100 and assign a `Best`, `Good`, `Average`, or
  `Poor` grade.
- Export results as a Markdown report.

## Project Structure

```text
Python_Code_Quality&Comment_Analyzer/
├── main.py
├── README.md
├── report.md
└── sample_inputs/
    ├── sample_bad.py
    ├── sample_good.py
    └── sample_unused.py
```

## Requirements

- Python 3.8 or newer
- No external dependencies

## Usage

Run the analyzer against one file:

```bash
python main.py sample_inputs/sample_bad.py
```

Analyze every Python file in a directory, including subdirectories:

```bash
python main.py sample_inputs/
```

Export the results to Markdown:

```bash
python main.py sample_inputs/ --export report.md
```

Analyze another project:

```bash
python main.py /path/to/project --export project_report.md
```

See all command-line options:

```bash
python main.py --help
```

## Checks

| Check | Examples |
| --- | --- |
| Style | Lines over 79 characters, trailing whitespace, tabs, semicolons, missing blank lines, and missing spaces around `=` |
| Comments and docstrings | Missing module, class, or function docstrings; filler comments; low comment-to-code ratio |
| Complexity | Cyclomatic complexity above 10, nesting depth above 4, and functions longer than 50 lines |
| Naming | Functions and variables not in `snake_case`, classes not in `PascalCase`, and constants not in `UPPER_SNAKE_CASE` |
| Unused code | Imports that are never referenced and local variables that are assigned but never read |

## Scoring

Each file starts with a score of 100. Issues reduce the score according to
severity:

| Severity | Penalty |
| --- | ---: |
| High | 5 points |
| Medium | 3 points |
| Low | 1 point |

The penalty is normalized by file length. Scores are graded as follows:

| Score | Grade |
| ---: | --- |
| 90-100 | Best |
| 75-89 | Good |
| 50-74 | Average |
| 0-49 | Poor |

When multiple files are analyzed, the output also includes the average score,
overall grade, grade distribution, and the lowest-scoring files.

## Sample Files and Report

The `sample_inputs` directory demonstrates the analyzer's behavior:

- `sample_bad.py` contains style, documentation, naming, and import issues.
- `sample_good.py` is a mostly clean example.
- `sample_unused.py` demonstrates unused import and variable detection.

The checked-in `report.md` is an example Markdown report generated from these
three sample files.

## Possible Improvements

- Duplicate code detection
- Type-hint coverage checks
- Configurable rules through a project configuration file
- HTML reports with charts
- A mode that analyzes only changed Git files
- Automatic fixes for simple style issues
