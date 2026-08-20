    # 12. Write a Python program to remove a specific key from a dictionary, retrieve all key-value
    # pairs, and check whether a given key exists.
    # Given Input: car = {"brand": "Toyota", "model": "Camry", "year": 2022, "color": "blue"}
    # Given dictionary
car = {
    "brand": "Toyota",
    "model": "Camry",
    "year": 2022,
    "color": "blue"
}
del car["color"]
print("All key-value pairs:")
for key, value in car.items():
    print(key, ":", value)
key_to_check = "model"

if key_to_check in car:
    print(key_to_check, "exists in the dictionary.")
else:
    print(key_to_check, "does not exist in the dictionary.")
