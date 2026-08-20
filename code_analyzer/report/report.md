# Code Quality Report

**Files analyzed:** 2  
**Average quality score:** 81.7/100

## sample_inputs\sample_bad.py
- **Score:** 65.2/100
- **Comment-to-code ratio:** 0.04

| Severity | Line | Issue |
|---|---|---|
| Low | 4 | Missing whitespace around operator '=' |
| Medium | 28 | Multiple statements on one line (semicolon usage) |
| Low | 30 | Line exceeds 79 characters (103) |
| Low | 26 | Expected 2 blank lines before top-level def/class |
| Low | 30 | Expected 2 blank lines before top-level def/class |
| Medium | 1 | Module is missing a top-level docstring |
| Medium | 2 | Class 'myclass' is missing a docstring |
| Medium | 26 | Function 'add' is missing a docstring |
| Medium | 30 | Function 'calculate_something_with_a_really_long_name_that_definitely_exceeds_the_line_length_limit' is missing a docstring |
| Medium | 3 | Function 'DoSomething' is missing a docstring |
| Medium | 11 | Function 'process_data' is missing a docstring |
| Low | 29 | Comment appears to be filler / non-descriptive |
| Low | None | Low comment-to-code ratio (0.04); consider adding more explanatory comments |
| Medium | 2 | 'myclass' does not follow PascalCase convention |
| Medium | 3 | 'DoSomething' does not follow snake_case convention |
| Medium | 3 | 'X' does not follow snake_case (parameter) convention |

## sample_inputs\sample_good.py
- **Score:** 98.1/100
- **Comment-to-code ratio:** 0.21

| Severity | Line | Issue |
|---|---|---|
| Low | 9 | Expected 2 blank lines before top-level def/class |
| Low | 15 | Expected 2 blank lines before top-level def/class |
