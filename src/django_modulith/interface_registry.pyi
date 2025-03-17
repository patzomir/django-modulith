from typing import Callable, ClassVar, Set, TypeVar

C = TypeVar("C")
S = TypeVar("S")
T = TypeVar("T")

class InterfaceRegistry:
    _registered_interfaces: ClassVar[Set[str]]

    @classmethod
    def list_interfaces() -> Set[str]: ...
    @classmethod
    def mytest() -> str: ...
    @classmethod
    def register(func: Callable, name: str): ...
    @classmethod
    def sample_function(param: T) -> T: ...
