# 5.  Given a list of integers, iterate through the items and count how many are even and how
# many are odd.
# Given Input: Numbers: [10, 21, 4, 45, 66, 93, 11]
num = [10, 21, 4, 45, 66, 93, 11]
even_count = 0
odd_count = 0
for num in num:
    if num % 2 == 0:
        even_count += 1
    else:
        odd_count += 1
print("Numbers:", num)
print("Even numbers count:", even_count)
print("Odd numbers count:", odd_count)
