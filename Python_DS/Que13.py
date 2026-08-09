# 13. Write a Python program to create a dictionary by mapping two equal-length lists, one
# containing keys and the other containing values.
# Given Input: keys = ["name", "age", "city"] and values = ["Bob", 25, "London"]
keys = ["name", "age", "city"]
values = ["Bob", 25, "London"]

student = dict(zip(keys, values))
print("Created dictionary:", student)