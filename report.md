# Code Quality Report

**Files analyzed:** 3  
**Average quality score:** 86.1/100  
**Overall grade:** Good

## sample_inputs/sample_bad.py
- **Score:** 64.2/100
- **Grade:** Average
- **Comment-to-code ratio:** 0.04

| Severity | Line | Issue |
|---|---|---|
| Low | 4 | Missing whitespace around '=' |
| Medium | 28 | Multiple statements on one line |
| Low | 30 | Line exceeds 79 chars (103) |
| Low | 26 | Expected 2 blank lines before top-level def/class |
| Low | 30 | Expected 2 blank lines before top-level def/class |
| Medium | 1 | Module is missing a top-level docstring |
| Medium | 2 | Class 'myclass' is missing a docstring |
| Medium | 26 | Function 'add' is missing a docstring |
| Medium | 30 | Function 'calculate_something_with_a_really_long_name_that_definitely_exceeds_the_line_length_limit' is missing a docstring |
| Medium | 3 | Function 'DoSomething' is missing a docstring |
| Medium | 11 | Function 'process_data' is missing a docstring |
| Low | 29 | Comment appears to be filler / non-descriptive |
| Low | - | Low comment-to-code ratio (0.04) |
| Medium | 2 | 'myclass' does not follow PascalCase |
| Medium | 3 | 'DoSomething' does not follow snake_case |
| Medium | 3 | 'X' does not follow snake_case (parameter) |
| Low | 1 | Imported name 'os' is never used |

## sample_inputs/sample_good.py
- **Score:** 99.0/100
- **Grade:** Best
- **Comment-to-code ratio:** 0.0

| Severity | Line | Issue |
|---|---|---|
| Low | - | Low comment-to-code ratio (0.0) |

## sample_inputs/sample_unused.py
- **Score:** 95.0/100
- **Grade:** Best
- **Comment-to-code ratio:** 0.0

| Severity | Line | Issue |
|---|---|---|
| Low | - | Low comment-to-code ratio (0.0) |
| Low | 3 | Imported name 'os' is never used |
| Low | 4 | Imported name 'sys' is never used |
| Low | 5 | Imported name 'json' is never used |
| Low | 11 | Variable 'unused_temp' in function 'process' is assigned but never used |
