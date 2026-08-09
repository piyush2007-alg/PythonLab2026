# 15. Write a Python program to combine two dictionaries into a single dictionary. If both
# dictionaries share a key, the value from the second dictionary should take precedence.
# Given Input: dict1 = {"a": 1, "b": 2} and dict2 = {"b": 3, "c": 4}
dict1 = {"a": 1, "b": 2}    
dict2 = {"b": 3, "c": 4}
dict1.update(dict2)
print("Combined dictionary:", dict1)