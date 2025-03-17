from functools import wraps
from typing import Any, Callable, Optional, TypeVar, Union, cast

from django_modulith.interface_registry import InterfaceRegistry

T = TypeVar("T", bound=Callable[..., Any])


def interface(
    name: Optional[Union[str, T]] = None,
) -> Union[Callable[[T], T], T]:
    """Decorator that can be used with or without parameters

    Usage:
        @interface
        def my_function(): ...

        @interface()
        def my_function(): ...

        @interface("custom_name")
        def my_function(): ...
    """
    func_or_name = name

    def decorator(func: T) -> T:
        service_name = (
            func.__name__
            if isinstance(func_or_name, (type(None), Callable))
            else func_or_name
        )
        InterfaceRegistry.register(func, str(service_name))

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        return cast(T, wrapper)

    # Handle both @interface and @interface() cases
    if isinstance(func_or_name, Callable):
        return decorator(func_or_name)

    # Handle @interface("name") case
    return decorator
