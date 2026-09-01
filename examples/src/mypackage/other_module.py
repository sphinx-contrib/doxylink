"""A second module in the package, defining a same-named function in another scope."""


def my_func():
    """A function sharing its name with :py:func:`mypackage.my_module.my_func`."""
    return 1
