from django_modulith.interface_decorator import interface


@interface
def sample_function(cls, param: str) -> str:
    return f"Called with {param}"


@interface
def sample_function2(cls, param: str) -> str:
    return f"Called with {param}"
