"""Utility module for basic mathematical operations.

This module provides simple functions and a Rectangle class
for demonstrating clean and maintainable Python code.
"""


# Add two numbers and return their sum.


def add_numbers(first_number, second_number):
    """Return the sum of two numbers."""
    return first_number + second_number


# Check whether a number is even.


def is_even(number):
    """Return True when the given number is even."""
    return number % 2 == 0


class Rectangle:
    """Represent a rectangle and calculate its area."""

    # Initialize the rectangle with its dimensions.
    def __init__(self, width, height):
        """Store the width and height of the rectangle."""
        self.width = width
        self.height = height

    # Calculate and return the rectangle area.
    def area(self):
        """Return the area of the rectangle."""
        return self.width * self.height