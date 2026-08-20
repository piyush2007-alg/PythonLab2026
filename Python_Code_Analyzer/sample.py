# Calculate student result

def calculate_marks(a, b, c):
    total = a + b + c

    if total >= 150:
        print("Pass")

    return total


x = 50
y = 60
z = 70

print(calculate_marks(x, y, z))