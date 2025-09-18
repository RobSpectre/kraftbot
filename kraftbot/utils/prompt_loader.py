"""
Simple prompt loading utilities for KraftBot.
"""

import os
from pathlib import Path
from typing import Optional, List
import re


class PromptLoader:
    """Simple utility class for loading system prompts from Markdown files"""
    
    def __init__(self, prompts_dir: Optional[Path] = None):
        """Initialize prompt loader with prompts directory"""
        self.prompts_dir = prompts_dir or self._get_default_prompts_dir()
    
    def _get_default_prompts_dir(self) -> Path:
        """Get the default prompts directory"""
        # Use package prompts directory
        package_dir = Path(__file__).parent.parent
        return package_dir / "prompts"
    
    def load_prompt(self, prompt_name_or_path: str) -> Optional[str]:
        """
        Load a system prompt from a Markdown file
        
        Args:
            prompt_name_or_path: Either:
                - Name of a prompt file in the prompts directory (with or without .md extension)
                - Full path to a prompt file anywhere on the filesystem
            
        Returns:
            str: The loaded prompt content, or None if not found
        """
        # Check if it's an absolute path
        if os.path.isabs(prompt_name_or_path) or '/' in prompt_name_or_path or '\\' in prompt_name_or_path:
            # It's a file path
            prompt_path = Path(prompt_name_or_path)
        else:
            # It's a prompt name - look in prompts directory
            if not prompt_name_or_path.endswith('.md'):
                prompt_name_or_path += '.md'
            prompt_path = self.prompts_dir / prompt_name_or_path
        
        if not prompt_path.exists():
            return None
        
        try:
            content = prompt_path.read_text(encoding='utf-8')
            # Clean markdown formatting for LLM consumption
            content = self._clean_markdown(content)
            return content.strip()
            
        except Exception as e:
            print(f"⚠️  Error loading prompt from {prompt_path}: {e}")
            return None
    
    def _clean_markdown(self, content: str) -> str:
        """Clean markdown formatting that might interfere with LLM processing"""
        # Remove markdown headers but keep the text
        content = re.sub(r'^#+\s*(.+)$', r'\1', content, flags=re.MULTILINE)
        
        # Convert markdown emphasis to plain text
        content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)  # Bold
        content = re.sub(r'\*(.+?)\*', r'\1', content)      # Italic
        content = re.sub(r'`(.+?)`', r'\1', content)        # Inline code
        
        # Remove code block markers but keep content
        content = re.sub(r'^```.*$', '', content, flags=re.MULTILINE)
        
        # Clean up excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        return content
    
    def list_available_prompts(self) -> List[str]:
        """Get list of available prompt files"""
        if not self.prompts_dir.exists():
            return []
        
        prompts = []
        for file_path in self.prompts_dir.glob('*.md'):
            prompts.append(file_path.stem)
        
        return sorted(prompts)
    
    def validate_prompt(self, prompt_name_or_path: str) -> tuple[bool, Optional[str]]:
        """
        Validate a prompt file exists and can be loaded
        
        Args:
            prompt_name_or_path: Either a prompt name or file path
        
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            content = self.load_prompt(prompt_name_or_path)
            if content is None:
                return False, f"Prompt file '{prompt_name_or_path}' not found"
            
            if len(content.strip()) == 0:
                return False, f"Prompt file '{prompt_name_or_path}' is empty"
            
            return True, None
            
        except Exception as e:
            return False, f"Error validating prompt: {e}"


# Global prompt loader instance
prompt_loader = PromptLoader()