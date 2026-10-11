# Python Code Quality & Comment Analyzer

An interactive **Neumorphic Web Frontend** and command-line tool for reviewing and **auto-fixing** Python source code quality, documentation, style, complexity, and naming conventions.

Scores every file from 0 to 100 with actionable feedback, function-level cyclomatic complexity breakdowns, and exportable reports. Built exclusively with the **Python Standard Library** (`ast`, `http.server`, `re`, `argparse`) — zero third-party pip dependencies required.

---

## 🛠️ Automated Code Fixer

The built-in Auto-Fix engine can automatically correct common PEP 8 violations in-place:

- **Whitespace Normalization**: Trims trailing whitespace from line ends.
- **Indentation Normalization**: Converts tabs to 4 spaces.
- **Semicolon Splitting**: Splits multiple statements separated by `;` onto clean individual lines.
- **Operator Spacing**: Adds standard spacing around `=` assignment operators (`x=1` -> `x = 1`).
- **PEP 8 Blank Lines**: Ensures 2 blank lines before top-level function and class definitions.
- **Unused Import Removal**: AST-informed detection and removal of unused `import` statements.
- **Filler Comments Cleanup**: Removes vague filler comments (`# fix this`, `# todo`).
- **Standard Newline**: Ensures file ends with a trailing newline.

### Run Auto-Fix via CLI:
```bash
# Auto-fix a single file in-place
python main.py my_script.py --fix

# Auto-fix all Python files in a directory
python main.py ./src --fix
```

### Run Auto-Fix via Web:
Click the **"Auto Fix"** button on the editor toolbar to view a before/after score breakdown and a checklist of all repairs applied.

---

## 🎨 Neumorphic Web Frontend Features

- **Soft UI / Neumorphism Aesthetics**:
  - Tactile dual-shadow surfaces (convex cards, concave inset editor, embossed badges).
  - Instant toggle between **Obsidian Dark Soft UI** and **Alabaster Light Soft UI**.
  - Animated Neumorphic **Circular Score Gauge** with color-coded grade glow.
- **Interactive Code Playground**:
  - Inset editor with synchronized line numbers and real-time cursor tracking.
  - Tab indentation support (4 spaces) and drag-and-drop file upload.
  - Quick actions: **Blank File**, **Paste Clipboard**, **Clean PEP 8 Template**, **Upload .py**.
  - **1-Click Auto-Fix** with before & after score improvement modal.
- **Deep Code Quality Inspection**:
  - **PEP 8 Style**: Lines > 79 chars, trailing whitespace, tabs, semicolons, operator spacing.
  - **Docstrings & Comments**: Module, class, and function docstrings, comment-to-code ratio health bar.
  - **Complexity Explorer**: Cyclomatic complexity, max nesting depth, and function lengths.
  - **Naming Conventions**: `snake_case`, `PascalCase`, `UPPER_SNAKE_CASE`.
  - **Unused Code Detection**: Unused imports and unused local variables.
- **Actionable Issues Explorer**:
  - Jump directly to line in editor with visual flashing gutter highlight.
  - Filter chips by Severity (**All**, **High**, **Medium**, **Low**) and Category (**Style**, **Comments**, **Complexity**, **Naming**, **Unused**).
  - Search bar to filter issue descriptions and line numbers.
- **Workspace & Directory Batch Scanner**:
  - Scan all project `.py` files or upload custom batches.
  - Rollup summary: Total files analyzed, average score, grade distribution.
- **Report Exporter**:
  - 1-Click Markdown report download (`.md`).
  - Copy formatted markdown to clipboard for GitHub PRs and code reviews.
  - Download raw JSON analysis data.

---

## 🚀 Quick Start (Web Interface)

Launch the web app directly (default: `http://127.0.0.1:5000/`):

```bash
python app.py
```

Or using `main.py`:

```bash
python main.py --web
```

To specify a custom port:

```bash
python app.py 8080
```

---

## 💻 Command-Line Usage (CLI)

Run against a single file:

```bash
python main.py my_script.py
```

Analyze an entire directory recursively:

```bash
python main.py ./src
```

Auto-fix issues in place:

```bash
python main.py my_script.py --fix
```

Export report to Markdown:

```bash
python main.py ./src --export report.md
```

View CLI options:

```bash
python main.py --help
```

---

## 📂 Project Organization

```text
Python_Code_Quality&Comment_Analyzer/
├── analyzer/                 # Core analysis & repair package
│   ├── __init__.py           # Unified exports
│   ├── engine.py             # AST inspections & quality rules
│   ├── fixer.py              # Automated code repair engine
│   └── report.py             # Markdown report generators & CLI printers
├── server/                   # Backend HTTP server package
│   ├── __init__.py           # Server exports
│   └── http_server.py        # Zero-dependency HTTP & REST API server
├── web/                      # Neumorphic Web Frontend
│   ├── index.html            # Semantic HTML5 layout
│   ├── style.css             # Neumorphic CSS design system (Dark & Light)
│   └── app.js                # Interactive client-side controller
├── main.py                   # Primary CLI & Web entrypoint
├── app.py                    # Web launcher shortcut (python app.py)
├── analyzer.py               # Root forwarding module for backwards-compatibility
├── server.py                 # Root forwarding module for backwards-compatibility
├── fixer.py                  # Root forwarding module for backwards-compatibility
├── README.md                 # Project documentation
└── report.md                 # Sample generated report
```

---

## 📊 Scoring & Grading Scale

Each file begins with 100 points. Penalties are normalized by file length:

| Severity | Penalty |
| :--- | :--- |
| **High** | 5 points |
| **Medium** | 3 points |
| **Low** | 1 point |

### Quality Grades

| Score Range | Grade | Description |
| :--- | :--- | :--- |
| **90 – 100** | `Best` | Clean PEP 8 compliance, thorough documentation, low complexity |
| **75 – 89** | `Good` | Well-structured code with minor style or comment notices |
| **50 – 74** | `Average` | Moderate issues such as missing docstrings or high complexity |
| **0 – 49** | `Poor` | Major architectural issues, deep nesting, or syntax errors |

---

## 🛠️ Requirements

- **Python 3.8+**
- **Zero external packages** (runs completely with standard library modules)
