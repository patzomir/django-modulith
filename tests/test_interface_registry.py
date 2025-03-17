from typing import TypeVar

import pytest

from django_modulith.interface_decorator import interface
from django_modulith.interface_registry import InterfaceRegistry

T = TypeVar("T")


@interface(name="sample_function")
def sample_function(cls, param: T) -> T:
    return f"Called with {param}"


@interface
def mytest(a: str) -> str:
    return a + "test1"


def test_register_new_interface():
    """Test registering a new interface function"""
    print(InterfaceRegistry.list_interfaces())
    # Verify it was registered
    assert "sample_function" in InterfaceRegistry.list_interfaces()
    assert hasattr(InterfaceRegistry, "sample_function")

    # Verify it works as expected
    result = InterfaceRegistry.sample_function("test_value")
    assert result == "Called with test_value"


def test_register_duplicate_interface():
    """Test that trying to register a duplicate interface name raises an error"""

    def first_function(cls):
        return "first"

    def second_function(cls):
        return "second"

    # Register the first function
    InterfaceRegistry.register(first_function, "duplicate_name")

    # Try to register another with the same name
    with pytest.raises(ValueError) as excinfo:
        InterfaceRegistry.register(second_function, "duplicate_name")

    assert "is already registered" in str(excinfo.value)

    # Verify the original function is still intact
    assert InterfaceRegistry.duplicate_name() == "first"


def test_list_interfaces():
    """Test listing all registered interfaces"""

    # Register multiple test functions
    def func1(cls):
        pass

    def func2(cls):
        pass

    def func3(cls):
        pass

    InterfaceRegistry.register(func1, "test_func1")
    InterfaceRegistry.register(func2, "test_func2")
    InterfaceRegistry.register(func3, "test_func3")

    # Get the list of interfaces
    interfaces = InterfaceRegistry.list_interfaces()

    # Verify our test functions are in the list
    assert "test_func1" in interfaces
    assert "test_func2" in interfaces
    assert "test_func3" in interfaces


def test_registered_function_is_classmethod():
    """Test that registered functions become class methods"""
    # Track function calls to verify 'cls' parameter is passed
    calls = []

    def tracking_function(cls, param=None):
        calls.append(cls)
        return "called"

    # Register the function
    InterfaceRegistry.register(tracking_function, "tracked_method")

    # Call the method
    result = InterfaceRegistry.tracked_method()

    # Verify it was called with the class as first argument
    assert len(calls) == 1
    assert calls[0] == InterfaceRegistry
    assert result == "called"


def test_registered_functions_preserve_parameters():
    """Test that registered functions preserve their parameters"""

    def complex_function(
        cls, required_param, optional_param="default", *args, **kwargs
    ):
        return f"{required_param}-{optional_param}-{len(args)}-{len(kwargs)}"

    # Register the function
    InterfaceRegistry.register(complex_function, "complex_interface")

    # Call with different parameter combinations
    result1 = InterfaceRegistry.complex_interface("req")
    result2 = InterfaceRegistry.complex_interface("req", "opt")
    result3 = InterfaceRegistry.complex_interface("req", "opt", "arg1", "arg2")
    result4 = InterfaceRegistry.complex_interface("req", key1="val1", key2="val2")

    # Verify results
    assert result1 == "req-default-0-0"
    assert result2 == "req-opt-0-0"
    assert result3 == "req-opt-2-0"
    assert result4 == "req-default-0-2"
