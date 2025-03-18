from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase


class GenerateStubsCommandTests(TestCase):
    @patch("django_modulith.management.commands.generatestubs.Path.write_text")
    @patch("django_modulith.management.commands.generatestubs.Path.mkdir")
    @patch("django_modulith.management.commands.generatestubs.Command._generate_stubs")
    @patch(
        "django_modulith.management.commands.generatestubs.Command._find_and_import_modulith_files"
    )
    def test_handle_generates_stubs(
        self, mock_find_and_import, mock_generate_stubs, mock_mkdir, mock_write_text
    ):
        """Test that the handle method generates stubs correctly"""
        mock_find_and_import.return_value = ["app1.modulith", "app2.modulith"]
        mock_generate_stubs.return_value = "stub content"

        call_command("generatestubs")

        mock_find_and_import.assert_called_once()
        mock_generate_stubs.assert_called_once()
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_write_text.assert_called_once_with("stub content")
