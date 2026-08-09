# 10. Write a Python program to combine two sets into one, containing all unique elements
# from both sets.
# Given Input: set_a = {1, 2, 3, 4} and set_b = {3, 4, 5, 6}
set_a = {1, 2, 3, 4}
set_b = {3, 4, 5, 6}
# Combine the two sets using the union() method
combined_set = set_a.union(set_b)
print("Combined set:", combined_set)