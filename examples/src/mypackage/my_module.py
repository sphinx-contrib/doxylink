"""Example documented module inside the package."""

from enum import Enum


def my_func():
    """Example documented function."""
    return 0


def my_func_with_args(a, b=3, *args, **kwargs):
    """A function using positional, keyword, variadic and keyword arguments."""
    return a


class MyClass:
    """Example documented class."""

    def __init__(self):
        """Construct a MyClass."""
        self.my_attribute = 0.0

    def my_method(self):
        """Example documented method."""
        return self.my_attribute

    def my_method_with_args(self, name: str, count: int) -> str:
        """A method with type-annotated arguments."""
        return name * count

    def my_method_with_qualified_args(self, items: "typing.List[str]") -> None:
        """A method whose annotation is a fully-qualified, generic type."""
        return None


class Color(Enum):
    """A simple enum."""

    RED = 1
    GREEN = 2
    BLUE = 3
