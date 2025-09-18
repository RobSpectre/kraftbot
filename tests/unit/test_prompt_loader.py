"""Tests for prompt loader utility."""

import tempfile
from pathlib import Path
import pytest
from kraftbot.utils.prompt_loader import PromptLoader


class TestPromptLoader:
    """Test PromptLoader utility."""

    def setup_method(self):
        """Set up test environment."""
        # Create a temporary directory for test prompts
        self.temp_dir = tempfile.mkdtemp()
        self.prompt_loader = PromptLoader(prompts_dir=Path(self.temp_dir))

    def test_load_prompt_from_file(self):
        """Test loading a prompt from a file."""
        # Create a test prompt file
        prompt_content = "# Test Prompt\n\nThis is a test prompt."
        prompt_file = Path(self.temp_dir) / "test.md"
        prompt_file.write_text(prompt_content)

        # Load the prompt
        loaded_content = self.prompt_loader.load_prompt("test")
        assert loaded_content is not None
        assert "This is a test prompt" in loaded_content

    def test_load_prompt_nonexistent(self):
        """Test loading a non-existent prompt."""
        result = self.prompt_loader.load_prompt("nonexistent")
        assert result is None

    def test_load_prompt_absolute_path(self):
        """Test loading a prompt from absolute path."""
        # Create a test prompt file
        prompt_content = "# Absolute Path Test\n\nThis is from absolute path."
        prompt_file = Path(self.temp_dir) / "absolute.md"
        prompt_file.write_text(prompt_content)

        # Load using absolute path
        loaded_content = self.prompt_loader.load_prompt(str(prompt_file))
        assert loaded_content is not None
        assert "This is from absolute path" in loaded_content

    def test_list_available_prompts(self):
        """Test listing available prompts."""
        # Create some test prompt files
        (Path(self.temp_dir) / "prompt1.md").write_text("Prompt 1")
        (Path(self.temp_dir) / "prompt2.md").write_text("Prompt 2")
        (Path(self.temp_dir) / "not_md.txt").write_text("Not markdown")

        prompts = self.prompt_loader.list_available_prompts()
        assert "prompt1" in prompts
        assert "prompt2" in prompts
        assert "not_md" not in prompts

    def test_validate_prompt(self):
        """Test prompt validation."""
        # Create valid prompt
        (Path(self.temp_dir) / "valid.md").write_text("Valid prompt content")

        is_valid, error = self.prompt_loader.validate_prompt("valid")
        assert is_valid is True
        assert error is None

        # Test invalid prompt
        is_valid, error = self.prompt_loader.validate_prompt("nonexistent")
        assert is_valid is False
        assert error is not None

    def test_clean_markdown(self):
        """Test markdown cleaning functionality."""
        markdown_content = "# Title\n\n**Bold text** and *italic text*\n\n- List item"
        cleaned = self.prompt_loader._clean_markdown(markdown_content)

        # Should remove markdown formatting but keep content
        assert "Title" in cleaned
        assert "Bold text" in cleaned
        assert "italic text" in cleaned
        assert "List item" in cleaned
        # Should not contain markdown symbols
        assert "**" not in cleaned