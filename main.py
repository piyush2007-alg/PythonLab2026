import ast

def analyze_code(filename):
    with open(filename, "r") as file:
        code = file.read()

    lines = code.splitlines()

    # ---------- Basic Analysis ----------
    total_lines = len(lines)
    comment_lines = 0
    long_lines = 0

    for line in lines:
        if line.strip().startswith("#"):
            comment_lines += 1

        if len(line) > 79:
            long_lines += 1

    # ---------- Python Structure ----------
    tree = ast.parse(code)

    functions = []
    variables = []
    complexity = 1

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)

        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            variables.append(node.id)

        if isinstance(node, (ast.If, ast.For, ast.While)):
            complexity += 1

    # ---------- SCORE ----------
    score = 100

    # Comments - 20 marks
    if comment_lines == 0:
        score -= 20

    # Long lines - 20 marks
    score -= min(long_lines * 5, 20)

    # Complexity - 20 marks
    if complexity > 5:
        score -= 20
    elif complexity > 3:
        score -= 10

    # Naming - 20 marks
    bad_names = 0

    for name in variables:
        if len(name) <= 2:
            bad_names += 1

    score -= min(bad_names * 5, 20)

    # Structure - 20 marks
    if len(functions) == 0:
        score -= 20

    # Make sure score stays between 0 and 100
    score = max(0, min(score, 100))

    # ---------- Grade ----------
    if score >= 90:
        grade = "Excellent"
    elif score >= 75:
        grade = "Good"
    elif score >= 60:
        grade = "Average"
    elif score >= 40:
        grade = "Needs Improvement"
    else:
        grade = "Poor"

    # ---------- REPORT ----------
    print("\n================================")
    print("   PYTHON CODE QUALITY REPORT")
    print("================================")

    print("Total Lines      :", total_lines)
    print("Comment Lines    :", comment_lines)
    print("Functions        :", len(functions))
    print("Variables        :", len(set(variables)))
    print("Complexity       :", complexity)

    print("\n--------------------------------")
    print("       CODE QUALITY SCORE")
    print("--------------------------------")

    print("Score :", score, "/ 100")
    print("Grade :", grade)

    print("--------------------------------")
    print("Suggestions:")

    if comment_lines == 0:
        print("- Add comments to your code.")

    if long_lines > 0:
        print("- Reduce long lines.")

    if complexity > 5:
        print("- Reduce code complexity.")

    if bad_names > 0:
        print("- Use meaningful variable names.")

    if len(functions) == 0:
        print("- Divide code into functions.")

    if score >= 90:
        print("- Excellent code quality!")

    print("================================")


# Main Program
filename = input("Enter Python file name: ")

try:
    analyze_code(filename)

except FileNotFoundError:
    print("File not found!")

except SyntaxError:
    print("Invalid Python code!")