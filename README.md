# Python Code Quality & Comment Analyzer — Phase 2

A command-line tool that analyzes Python source code for coding
standards, comment/docstring quality, code complexity, naming
conventions, and unused imports/variables — then generates a scored
quality report (with a Best / Good / Average / Poor grade) and
improvement suggestions.

Built entirely on the Python standard library (`ast`, `re`, `os`,
`argparse`) — no external dependencies required.

---

## What's New in Phase 2

- **Unused Imports Checker** — flags any `import` that is never
  referenced anywhere in the file.
- **Unused Variables Checker** — flags any local variable assigned
  inside a function but never read afterward.
- **Quality Grade Label** — every file (and the overall run) now gets
  a plain-language grade, not just a raw number:

| Score Range | Grade   |
|-------------|---------|
| 90 – 100    | Best    |
| 75 – 89     | Good    |
| 50 – 74     | Average |
| 0 – 49      | Poor    |

- **Grade Distribution Summary** — the overall report now shows how
  many files fell into each grade bucket.

---

## Project Structure

```
phase2/
├── main.py                     # single-file CLI tool (Phase 2)
├── sample_inputs/
│   ├── sample_bad.py           # intentionally messy file
│   ├── sample_good.py          # clean, well-documented file
│   └── sample_unused.py        # triggers unused import/variable checks
└── README.md
```

---

## Requirements

- Python 3.8 or higher
- No installation of external packages needed

---

## All Commands

**Analyze a single file:**
```bash
python main.py sample_inputs/sample_bad.py
```

**Analyze an entire directory (recursively finds all `.py` files):**
```bash
python main.py sample_inputs/
```

**Analyze and export a Markdown report:**
```bash
python main.py sample_inputs/ --export report.md
```

**Analyze the current directory:**
```bash
python main.py .
```

**View CLI help:**
```bash
python main.py --help
```

**Run against your own project folder:**
```bash
python main.py /path/to/your/project --export my_project_report.md
```

---

## What Each Check Looks For

| Analyzer | Checks |
|---|---|
| Style Checker | Line length > 79, trailing whitespace, tabs, semicolons, missing blank lines before def/class, missing spaces around `=` |
| Comment Analyzer | Missing module/class/function docstrings, low comment-to-code ratio, filler comments (e.g. `# fix this`) |
| Complexity Analyzer | Cyclomatic complexity > 10, nesting depth > 4, function length > 50 lines |
| Naming Checker | Functions/variables not in snake_case, classes not in PascalCase, constants not in UPPER_SNAKE_CASE |
| Unused Imports | Any `import` or `from ... import` name never referenced in the file |
| Unused Variables | Any variable assigned inside a function but never read |

---

## How Scoring & Grading Work

1. Every file starts at **100 points**.
2. Each issue subtracts points based on severity:
   - High = 5 points
   - Medium = 3 points
   - Low = 1 point
3. The total penalty is normalized against file length, so longer
   files aren't unfairly punished just for having more lines.
4. The final score is mapped to a grade using the table above.
5. The overall report averages all file scores and grades the
   project as a whole the same way.

---

## Sample Output

```
======================================================================
FILE: sample_inputs/sample_bad.py
QUALITY SCORE: 64.2/100   |   GRADE: Average
COMMENT-TO-CODE RATIO: 0.04
----------------------------------------------------------------------
[Medium] Line 2     - 'myclass' does not follow PascalCase convention
[Medium] Line 3     - Function 'DoSomething' is missing a docstring
...

######################################################################
OVERALL SUMMARY
######################################################################
Files analyzed: 3
Total issues found: 23
Average quality score: 86.1/100   |   OVERALL GRADE: Good

Grade distribution:
  Best    : 2 file(s)
  Average : 1 file(s)
```

---

## Extending the Project (Ideas for Phase 3)

- Duplicate code detection
- Type hint coverage checking
- Configurable rules via a `.codequalityrc` file
- HTML report with charts
- Git integration (analyze only changed files)
- `--fix` flag to auto-correct trivial issues

---

## License

MIT
