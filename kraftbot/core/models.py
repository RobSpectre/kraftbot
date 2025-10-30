"""
Data models and structures for Kraftbot
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class TokenCounter:
    """Track all token types for comprehensive reporting"""

    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    tool_use_tokens: int = 0
    total_tokens: int = 0

    def update(self, response_data: Any, accumulate: bool = False):
        """
        Update token counts from response metadata

        Args:
            response_data: Response object with token metadata
            accumulate: If True, add to existing counts. If False, replace counts.
        """
        if hasattr(response_data, 'response_metadata'):
            metadata = response_data.response_metadata
            usage = metadata.get('token_usage', {})

            # Standard tokens
            if accumulate:
                self.input_tokens += usage.get('prompt_tokens', 0)
                self.output_tokens += usage.get('completion_tokens', 0)
                self.total_tokens += usage.get('total_tokens', 0)
            else:
                self.input_tokens = usage.get('prompt_tokens', 0)
                self.output_tokens = usage.get('completion_tokens', 0)
                self.total_tokens = usage.get('total_tokens', 0)

            # Extended token tracking for models that support it
            if 'reasoning_tokens' in usage:
                if accumulate:
                    self.reasoning_tokens += usage.get('reasoning_tokens', 0)
                else:
                    self.reasoning_tokens = usage.get('reasoning_tokens', 0)
            if 'tool_use_tokens' in usage:
                if accumulate:
                    self.tool_use_tokens += usage.get('tool_use_tokens', 0)
                else:
                    self.tool_use_tokens = usage.get('tool_use_tokens', 0)

    def get_summary(self) -> Dict[str, int]:
        """Return token count summary"""
        return {
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'reasoning_tokens': self.reasoning_tokens,
            'tool_use_tokens': self.tool_use_tokens,
            'total_tokens': self.total_tokens
        }

    def reset(self):
        """Reset all counters"""
        self.input_tokens = 0
        self.output_tokens = 0
        self.reasoning_tokens = 0
        self.tool_use_tokens = 0
        self.total_tokens = 0


@dataclass
class AgentResponse:
    """Response from the Kraftbot agent"""

    content: str
    response_time: float
    tokens: Dict[str, int]
    week: str
    model_name: str
    system_prompt: str
    user_prompt: str
    reasoning: Optional[str] = None
    mcp_status: str = "Disabled"
    error: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None

    def to_markdown(self) -> str:
        """Format response as markdown"""
        markdown = f"""## Model: {self.model_name}
- **Input Tokens**: {self.tokens['input_tokens']}
- **Reasoning Tokens**: {self.tokens['reasoning_tokens']}
- **Output Tokens**: {self.tokens['output_tokens']}

## System Prompt
{self.system_prompt}

## User Prompt
{self.user_prompt}

"""
        # Add tool calls section if present (just mark which tools were used)
        if self.tool_calls and len(self.tool_calls) > 0:
            markdown += "## Tools Used\n"
            for call in self.tool_calls:
                markdown += f"- {call['tool']}\n"
            markdown += "\n"

        # Add reasoning section if present
        if self.reasoning:
            markdown += f"""## Reasoning
{self.reasoning}

"""

        markdown += f"""## Output
{self.content}
"""
        if self.error:
            markdown += f"\n\n## Error\n{self.error}\n"

        return markdown


@dataclass
class MCPServerInfo:
    """Information about an MCP server"""

    name: str
    status: str  # "connected", "unavailable", "error"
    url: Optional[str] = None
    tools: list = field(default_factory=list)
    description: str = ""
    error_message: Optional[str] = None
