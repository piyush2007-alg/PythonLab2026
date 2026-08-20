# 8. Write a Python program to determine how many elements are in a set without using the
# built-in len() function.
# Given Input: animals = {"cat", "dog", "bird", "fish"}
animals = {"cat", "dog", "bird", "fish"}
count = 0
for animal in animals:
    count += 1
print("Number of elements in the set:", count)
