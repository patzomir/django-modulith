import configparser
import os

from django.core.management.commands.startapp import Command as StartAppCommand

IMPORTLINTER_FILE = ".importlinter"


class Command(StartAppCommand):
    help = f"Add a new module to the {IMPORTLINTER_FILE} configuration"
    contract_key = "importlinter:contract:modulith_modules"

    def handle(self, *args, **options):
        super().handle(*args, **options)
        config_path = IMPORTLINTER_FILE
        config = configparser.ConfigParser()

        # Initialize or read existing config
        if os.path.exists(config_path):
            config.read(config_path)
        else:
            self._initialize_config(config)

        module_name = options["name"]
        self._add_module_to_config(config, module_name)

        # Write configuration back to file
        with open(config_path, "w") as f:
            config.write(f)

        self.stdout.write(
            self.style.SUCCESS(f"✅ {IMPORTLINTER_FILE} updated successfully!")
        )

    def _initialize_config(self, config):
        """Initialize a basic importlinter configuration"""
        config["importlinter"] = {
            "root_package": "modules",
            "include_external_packages": "n",
        }

        config[self.contract_key] = {
            "name": "Domain modules are independent",
            "type": "independence",
            "modules": "",
        }

        self.stdout.write(
            self.style.SUCCESS("Created initial importlinter configuration")
        )

    def _add_module_to_config(self, config, module_name):
        """Add a new module to the modules independence contract"""
        if self.contract_key not in config:
            self.stdout.write(
                self.style.ERROR("Modules contract section not found in config")
            )
            return

        contract_section = config[self.contract_key]
        modules = contract_section.get("modules", "")

        # Add the new module if it's not already there
        module_list = [m.strip() for m in modules.split("\n") if m.strip()]
        if module_name not in module_list:
            module_list.append(module_name)
            contract_section["modules"] = "\n".join(module_list)
            self.stdout.write(
                f"Added module '{module_name}' to importlinter configuration"
            )
        else:
            self.stdout.write(f"Module '{module_name}' already in configuration")
