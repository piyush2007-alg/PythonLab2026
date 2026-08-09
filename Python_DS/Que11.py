# 11. Write a Python program to add a new key-value pair to a dictionary, modify an existing
# value, and access a specific key.
# Given Input: student = {"name": "Alice", "age": 20, "grade": "B"}
# Given dictionary
student = {"name": "Alice", "age": 20, "grade": "B"}
student["city"] = "New York"
student["grade"] = "A"
print("Student Name:", student["name"])
print(student)