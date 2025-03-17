import configparser
import os
import tempfile

import pytest
from django.core.management import call_command

from django_modulith.management.commands.modulith import (
    IMPORTLINTER_FILE as IMPORTLINTER,
)


@pytest.fixture
def temp_project_dir():
    """
    Create a temporary directory and change to it for test execution,
    then return to the original directory after the test completes.
    """
    # Store original working directory
    original_cwd = os.getcwd()

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to the temporary directory
        os.chdir(temp_dir)

        # Ensure the IMPORTLINTER file doesn't exist in the temp dir
        if os.path.exists(IMPORTLINTER):
            os.remove(IMPORTLINTER)

        # Run the test
        yield temp_dir

        # Clean up - remove the config file if it exists
        if os.path.exists(IMPORTLINTER):
            os.remove(IMPORTLINTER)

    # Return to the original directory
    os.chdir(original_cwd)


def test_initialize_config_creates_file(db, temp_project_dir):
    """Test that the command creates a new config file if one doesn't exist"""
    # Verify file doesn't exist yet
    assert not os.path.exists(IMPORTLINTER)

    call_command("modulith", "new_test")

    # Verify file was created
    assert os.path.exists(IMPORTLINTER)

    # Verify content is correct
    config = configparser.ConfigParser()
    config.read(IMPORTLINTER)

    # Check sections exist
    assert "importlinter" in config
    assert "importlinter:contract:modulith_modules" in config

    # Check settings
    assert config["importlinter"]["root_package"] == "modules"
    assert config["importlinter"]["include_external_packages"] == "n"

    # Check modules
    modules = config["importlinter:contract:modulith_modules"]["modules"]
    assert "new_test" in modules


def test_add_module_updates_existing_config(db, temp_project_dir):
    """Test that the command updates an existing config file"""
    # Create an initial config file
    call_command("modulith", "first_module")

    # Verify first module was added
    config = configparser.ConfigParser()
    config.read(IMPORTLINTER)
    modules = config["importlinter:contract:modulith_modules"]["modules"]
    assert "first_module" in modules
    assert "second_module" not in modules

    # Add second module
    call_command("modulith", "second_module")

    # Verify second module was added
    config = configparser.ConfigParser()
    config.read(IMPORTLINTER)
    modules = config["importlinter:contract:modulith_modules"]["modules"]
    assert "first_module" in modules
    assert "second_module" in modules
