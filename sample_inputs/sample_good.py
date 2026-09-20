"""A small, well-documented utility module for basic math operations."""


def add_numbers(first_number, second_number):
    """Return the sum of two numbers."""
    return first_number + second_number


def is_even(number):
    """Return True if the given number is even."""
    return number % 2 == 0


class Rectangle:
    """Represents a rectangle and computes its area and perimeter."""

    def __init__(self, width, height):
        """Store width and height."""
        self.width = width
        self.height = height

    def area(self):
        """Return the area of the rectangle."""
        return self.width * self.height
