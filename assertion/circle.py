import math
import builtins


class Circle:
    def __init__(self, radius):
        """
        A Pythonic solution for the Circle class would be to turn the .radius attribute into a managed attribute using
        the @property decorator. This way, you perform the .radius validation every time the attribute changes:
        """
        self.radius = radius

    @property
    def radius(self):
        return self._radius

    # which is called whenever the class changes the value of .radius
    @radius.setter
    def radius(self, value: object) -> object:
        if value < 0:
            raise ValueError("Positive value only")
        self._radius = value

    def area(self):
        # assert self.radius >= 0, "Positive value only"
        return math.pi * self.radius ** 2

    def correct_radius(self, coefficient):
        # This can take in negative value -> introduce a bug
        self.radius *= coefficient


tire = Circle(42)
print(tire.area())

tire.correct_radius(-3)
print(tire.radius)

'''
if __debug__ and not expression:
    raise AssertionError(assertion_message)

# equivalent to
assert expression, assertion_message
'''
