from typing import Any, Callable, Set, ClassVar, List, TypeVar

C = TypeVar('C')
S = TypeVar('S')

class InterfaceRegistry:
    _registered_interfaces: ClassVar[Set[str]]

    @classmethod
    def list_interfaces() -> Set[str]: ...
    @classmethod
    def register(func: Callable, name: str): ...
    @classmethod
    def sample_function(param: str) -> str: ...
