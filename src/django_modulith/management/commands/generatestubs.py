import importlib
import inspect
import re
from pathlib import Path
from typing import List

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

from django_modulith.interface_registry import InterfaceRegistry


class Command(BaseCommand):
    help = (
        "Generate interface stubs by scanning all installed apps for modulith.py files"
    )

    def handle(self, *args, **options):
        # Find and import all modulith.py files
        self.stdout.write("Scanning installed apps for modulith.py files...")
        modules_found = self._find_and_import_modulith_files()

        if not modules_found:
            self.stdout.write(
                self.style.WARNING("No modulith.py files found in installed apps.")
            )
        else:
            self.stdout.write(f"Found {len(modules_found)} modulith.py files.")

        # Generate stubs
        self.stdout.write("Generating interface stubs...")
        # Default to the package directory
        package_dir = Path(__file__).parent.parent.parent
        output_path = package_dir / "interface_registry.pyi"

        stub_content = self._generate_stubs()

        # Ensure the directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the stub file
        output_path.write_text(stub_content)

        self.stdout.write(
            self.style.SUCCESS(f"Interface stubs generated at {output_path}")
        )

    def _find_and_import_modulith_files(self) -> List[str]:
        """Find and import all modulith.py files in installed apps."""
        modules_found = []

        for app_config in apps.get_app_configs():
            app_path = Path(app_config.path)
            modulith_file = app_path / "modulith.py"

            if modulith_file.exists():
                module_name = f"{app_config.name}.modulith"
                self.stdout.write(f"Found {module_name} at {modulith_file}")

                try:
                    importlib.import_module(module_name)
                    modules_found.append(module_name)
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error importing {module_name}: {e}")
                    )
                    raise CommandError(f"Error importing {module_name}: {e}")

        return modules_found

    def _clean_signature(self, signature):
        """Clean up the signature string by removing ~ from type annotations"""
        return str(signature).replace("~", "")

    def _extract_typevars(self, signatures):
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

    def _generate_stubs(self) -> str:
        """Generate stub file content for InterfaceRegistry"""
        # Collect all signatures first to extract TypeVars
        signatures = []

        # Get signatures from built-in methods
        for _, method in inspect.getmembers(
            InterfaceRegistry, predicate=inspect.ismethod
        ):
            signatures.append(inspect.signature(method))

        # Get signatures from registered methods
        for name in InterfaceRegistry.list_interfaces():
            method = getattr(InterfaceRegistry, name)
            signatures.append(inspect.signature(method))

        # Extract TypeVars from signatures
        typevar_defs = self._extract_typevars(signatures)

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
                clean_sig = self._clean_signature(signature)
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
            clean_sig = self._clean_signature(signature)
            stub_line = "    @classmethod\n"
            stub_line += f"    def {name}{clean_sig}: ...\n"
            stubs.append(stub_line)

        return "".join(stubs)
