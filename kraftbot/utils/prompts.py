"""
Prompt loading and management utilities
"""

from pathlib import Path
from typing import List, Optional


def get_prompts_dir() -> Path:
    """Get the prompts directory path"""
    # Try to find prompts directory relative to package
    package_dir = Path(__file__).parent.parent.parent
    prompts_dir = package_dir / "prompts"

    if prompts_dir.exists():
        return prompts_dir

    # Fallback to current directory
    return Path("prompts")


def list_prompts() -> List[str]:
    """List all available prompt names"""
    prompts_dir = get_prompts_dir()

    if not prompts_dir.exists():
        return []

    return sorted([p.stem for p in prompts_dir.glob("*.md")])


def get_prompt_path(prompt_name: str) -> Optional[Path]:
    """
    Get the full path to a prompt file

    Args:
        prompt_name: Name of the prompt (without .md extension) or full path

    Returns:
        Path to the prompt file, or None if not found
    """
    # Check if it's already a full path
    prompt_path = Path(prompt_name)
    print(f"[DEBUG] get_prompt_path: checking path '{prompt_path}', exists={prompt_path.exists()}")
    if prompt_path.exists() and prompt_path.is_file():
        return prompt_path

    # Look in prompts directory
    prompts_dir = get_prompts_dir()
    prompt_path = prompts_dir / f"{prompt_name}.md"
    print(f"[DEBUG] get_prompt_path: checking in prompts_dir '{prompt_path}', exists={prompt_path.exists()}")

    if prompt_path.exists():
        return prompt_path

    return None


def load_prompt(prompt_name: str) -> str:
    """
    Load a system prompt from file

    Args:
        prompt_name: Name of the prompt (e.g., 'default', 'aggressive') or path to file

    Returns:
        Content of the prompt file
    """
    prompt_path = get_prompt_path(prompt_name)
    print(f"[DEBUG] load_prompt: prompt_name='{prompt_name}', resolved_path={prompt_path}")

    if prompt_path is None:
        print(f"[DEBUG] Prompt not found, using fallback")
        # Return default fallback prompt
        return get_default_prompt()

    try:
        with open(prompt_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Error reading prompt file: {e}")
        return get_default_prompt()


def get_default_prompt() -> str:
    """Get the default fallback prompt"""
    return """You are Kraftbot, an expert fantasy football assistant.

## Core Competencies
- Draft strategy and player valuation
- Weekly lineup optimization based on matchups
- Waiver wire recommendations
- Trade evaluation and negotiation
- Injury impact assessment

## Communication Style
- Provide confident, actionable advice
- Acknowledge uncertainty when appropriate
- Support recommendations with data and reasoning
- Focus on practical, implementable strategies

Remember: Your goal is to help managers make informed decisions that lead to fantasy football championships."""


def get_prompt_description(prompt_name: str) -> str:
    """Get a description for a prompt"""
    descriptions = {
        'default': 'Comprehensive strategy for league 1266471057523490816 with tokenbowl tools',
        'aggressive': 'High-risk/high-reward approach for championship runs',
        'conservative': 'Risk-averse strategy focusing on consistency',
        'analytical': 'Data-driven approach with statistical analysis',
        'few_shot': 'Example-based learning approach',
        'kimi_k2': 'Custom configuration strategy'
    }

    return descriptions.get(prompt_name, 'Custom prompt strategy')
