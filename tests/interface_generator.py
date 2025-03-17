import importlib
import inspect
import pkgutil
import re
from pathlib import Path
from typing import List

from django_modulith.interface_registry import InterfaceRegistry


def find_modules_using_registry() -> List[str]:
    """Find all modules that import InterfaceRegistry"""
    modules = []
    root_paths = [
        Path(__file__).parent.parent / "src",
        Path(__file__).parent.parent / "tests",
    ]

    for finder, name, _ in pkgutil.walk_packages(root_paths):
        try:
            module = importlib.import_module(name)
            module_content = Path(module.__file__).read_text()

            # Check if module imports InterfaceRegistry
            if "InterfaceRegistry" in module_content:
                modules.append(name)
        except Exception as e:
            print(f"Warning: Could not import {name}: {e}")

    return modules


def clean_signature(signature):
    """Clean up the signature string by removing ~ from type annotations"""
    return str(signature).replace("~", "")


def extract_typevars(signatures):
    """Extract TypeVar definitions from signatures"""
    typevar_pattern = r"([A-Z]_co|[A-Z]_contra|[A-Z])"
    typevars = set()

    for sig in signatures:
        # Look for capital letter followed by _co, _contra or just capital letter alone
        matches = re.findall(typevar_pattern, str(sig))
        typevars.update(matches)

    # Generate TypeVar definitions
    typevar_defs = []
    for tv in sorted(typevars):
        if tv.endswith("_co"):
            base = tv[:-3]
            typevar_defs.append(f"{tv} = TypeVar('{base}', covariant=True)")
        elif tv.endswith("_contra"):
            base = tv[:-7]
            typevar_defs.append(f"{tv} = TypeVar('{base}', contravariant=True)")
        else:
            typevar_defs.append(f"{tv} = TypeVar('{tv}')")

    return typevar_defs


def generate_stubs():
    # Collect all signatures first to extract TypeVars
    signatures = []

    # Get signatures from built-in methods
    for _, method in inspect.getmembers(InterfaceRegistry, predicate=inspect.ismethod):
        signatures.append(inspect.signature(method))

    # Get signatures from registered methods
    for name in InterfaceRegistry.list_interfaces():
        method = getattr(InterfaceRegistry, name)
        signatures.append(inspect.signature(method))

    # Extract TypeVars from signatures
    typevar_defs = extract_typevars(signatures)

    # Start building stubs
    stubs = [
        "from typing import Any, Callable, Set, ClassVar, List, TypeVar\n",
    ]

    # Add TypeVar definitions if found
    if typevar_defs:
        stubs.append("\n")
        for tv_def in typevar_defs:
            stubs.append(f"{tv_def}\n")

    stubs.extend(
        [
            "\n",
            "class InterfaceRegistry:\n",
            "    _registered_interfaces: ClassVar[Set[str]]\n",
            "\n",
        ]
    )

    # Add built-in class methods first
    for name, method in inspect.getmembers(
        InterfaceRegistry, predicate=inspect.ismethod
    ):
        if not name.startswith("_") or name == "__init__":
            signature = inspect.signature(method)
            clean_sig = clean_signature(signature)
            stub_line = "    @classmethod\n"
            stub_line += f"    def {name}{clean_sig}: ...\n"
            stubs.append(stub_line)

    # Add dynamically registered methods
    for name in InterfaceRegistry.list_interfaces():
        # Skip if already added (in case list_interfaces itself is registered)
        if any(f"def {name}" in line for line in stubs):
            continue

        method = getattr(InterfaceRegistry, name)
        signature = inspect.signature(method)
        clean_sig = clean_signature(signature)
        stub_line = "    @classmethod\n"
        stub_line += f"    def {name}{clean_sig}: ...\n"
        stubs.append(stub_line)

    # Write to .pyi file
    stub_path = Path("src/modulith/interface_registry.pyi")
    stub_path.write_text("".join(stubs))
    print(f"Generated stub file at {stub_path}")


if __name__ == "__main__":
    find_modules_using_registry()
    generate_stubs()
