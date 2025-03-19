# Djnago Modulith

A toolkit for building modular, maintainable Django applications using the Modulith architectural pattern.

## What is a Modulith?

A Modulith is a monolithic application that is internally structured as a collection of well-defined, loosely-coupled modules. It combines the deployment simplicity of a monolith with the architectural clarity of microservices.

## Features

- **Module Generation**: Quickly scaffold new application modules with proper structure
- **Interface Registry**: Define clear boundaries between modules via the interface registry
- **Import Control**: Enforce architectural boundaries using import linting
- **Django Integration**: Seamlessly works with Django's existing patterns

## Installation
```bash
pip install django-modulith
```


Add to your Django project's INSTALLED_APPS:
```python
INSTALLED_APPS = [
    # ...
    'django_modulith',
    # ...
]
```

## Quick Start
1. Create a new module
This will:

Create a new module directory with proper structure
Update the importlinter configuration to include the new module

2. Define module interfaces in `modulith.py`:
```python
# modulith.py
from django_modulith.interface_decorator import interface

@interface
def get_user_profile(user_id: int) -> dict:
    # Implementation here
    pass
```

3. Use module interfaces
```python
# some_module.py
from django_modulith.interface_registry import InterfaceRegistry

user_profile = InterfaceRegistry.get_user_profile(user_id=1)
```

## Architecture Enforcement
The library helps enforce module boundaries through import linting:
```python
# Check for import rule violations
python -m importlinter

# Generate visualization of module dependencies
python -m importlinter.visualization
```

## Interface Registry
The `InterfaceRegistry` serves as the core of the inter-module communication:

* Functions registered with the `@interface` decorator become available via the registry
* Type annotations are preserved for IDE autocomplete support
* The registry pattern discourages direct imports between modules

## Best Practices
1. Keep modules focused: Each module should have a single responsibility
1. Use interfaces: Access other modules through the interface registry, not direct imports
1. Honor boundaries: Structure code to respect the architectural boundaries
1. Document interfaces: Well-documented interfaces make the module boundaries clear

## Configuration
Import Linter Configuration
The `.importlinter` file controls module boundaries:

```python
[importlinter]
root_package = modules
include_external_packages = n

[importlinter:contract:modulith_modules]
name = Domain modules are independent
type = independence
modules = 
    users
    products
    orders
```

## Advanced Usage
### Type Hints
A stub file (interface_registry.pyi) is automatically generated to provide proper type hints for registered interfaces.

## Example: Using the Interface Registry

### Step 1: Register an Interface in `modulith.py`

In the `users` module, define and register an interface in `modulith.py`:
```python
# users/modulith.py
from django_modulith.interface_decorator import interface

@interface
def get_user_profile(user_id: int) -> dict:
    # Implementation here
    pass
```

### Step 2: Use the Registered Interface in Another Module

In the `profiles` module, use the registered interface via the registry:
```python
# profiles/some_module.py
from django_modulith.interface_registry import InterfaceRegistry

user_profile = InterfaceRegistry.get_user_profile(user_id=1)
```

## Contributing
Contributions are welcome! Please check the contribution guidelines for more details.

## License
This project is licensed under the MIT License - see the LICENSE file for details.