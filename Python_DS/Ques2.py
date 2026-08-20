# 2. Take a given list and modify it through five specific actions:
# Change Element: Change the second element of a list to 200 and print the updated list.
# Append Element: Add 600 o the end of a list and print the new list.
# Insert Element: Insert 300 at the third position (index 2) of a list and print the result.
# Remove Element (by value): Remove 600 from the list and print the list.
# Remove Element (by index): Remove the element at index 0 from the list print the list.
# Given Input: Initial List: [100, 50, 400, 500]
# Given list
numbers = [100, 50, 400, 500]
numbers[1] = 200
print("After changing second element:", numbers)
numbers.append(600)
print("After appending 600:", numbers)
numbers.insert(2, 300)
print("After inserting 300 at index 2:", numbers)
numbers.remove(600)
print("After removing 600:", numbers)
numbers.pop(0)
print("After removing element at index 0:", numbers)
