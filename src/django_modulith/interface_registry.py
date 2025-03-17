from typing import Callable, Set


class InterfaceRegistry:
    """Registry that dynamically adds interfaces as actual methods"""

    _registered_interfaces: Set[str] = (
        set()
    )  # Track registered names to prevent overrides

    @classmethod
    def register(cls, func: Callable, name: str):
        """Register a function dynamically as a method on the class"""
        if name in cls._registered_interfaces:
            raise ValueError(
                f"interface '{name}' is already registered. Choose a unique name."
            )

        setattr(cls, name, classmethod(func))
        cls._registered_interfaces.add(name)

    @classmethod
    def list_interfaces(cls) -> Set[str]:
        """List all registered interfaces"""
        return cls._registered_interfaces
