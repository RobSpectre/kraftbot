#!/usr/bin/env python3
"""
Kraftbot with MCP Integration - Fantasy Football Assistant with Langchain and OpenRouter
Includes support for MCP server tools and multiple prompt strategies
"""

import os
import sys
import time
import json
import yaml
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from langchain.chat_models.base import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.callbacks import get_openai_callback
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
import httpx

console = Console()


class MCPToolInfo:
    """Information about MCP server tools"""

    def __init__(self):
        self.tools = []
        self.server_status = {}

    async def check_tokenbowl_server(self) -> Dict:
        """Check if tokenbowl MCP server is available and get tool info"""
        try:
            # The SSE endpoint provides tool information
            url = "https://tokenbowl-mcp.haihai.ai/sse"
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, follow_redirects=True)
                if response.status_code == 200:
                    return {
                        'status': 'connected',
                        'server': 'tokenbowl',
                        'tools': [
                            'get_league_info',
                            'get_roster',
                            'get_matchup',
                            'get_players',
                            'get_transactions',
                            'get_trending_players'
                        ],
                        'description': 'Fantasy football data for Sleeper leagues'
                    }
        except Exception as e:
            console.print(f"[yellow]Note: Tokenbowl MCP server unavailable: {e}[/yellow]")

        return {
            'status': 'unavailable',
            'server': 'tokenbowl',
            'tools': [],
            'description': 'Tokenbowl MCP server not accessible'
        }

    def get_tools_description(self) -> str:
        """Generate a description of available MCP tools for the system prompt"""
        if not self.tools:
            return "No MCP tools currently available."

        tool_desc = "Available MCP Tools:\n"
        for tool in self.tools:
            tool_desc += f"- **{tool['server']}** ({tool['status']}): {tool['description']}\n"
            if tool['tools']:
                tool_desc += f"  Tools: {', '.join(tool['tools'])}\n"

        return tool_desc


class TokenCounter:
    """Track all token types for comprehensive reporting"""

    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0
        self.reasoning_tokens = 0
        self.tool_use_tokens = 0
        self.total_tokens = 0

    def update(self, response_data: Dict[str, Any]):
        """Update token counts from response metadata"""
        if hasattr(response_data, 'response_metadata'):
            metadata = response_data.response_metadata
            usage = metadata.get('token_usage', {})

            # Standard tokens
            self.input_tokens = usage.get('prompt_tokens', 0)
            self.output_tokens = usage.get('completion_tokens', 0)
            self.total_tokens = usage.get('total_tokens', 0)

            # Extended token tracking for models that support it
            if 'reasoning_tokens' in usage:
                self.reasoning_tokens = usage.get('reasoning_tokens', 0)
            if 'tool_use_tokens' in usage:
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


class KraftbotAgent:
    """Main Kraftbot agent with memory, MCP awareness, and OpenRouter support"""

    def __init__(self, model_name: str, api_key: str, system_prompt: str, mcp_enabled: bool = True):
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.memory = ConversationBufferMemory(return_messages=True)
        self.token_counter = TokenCounter()
        self.mcp_info = MCPToolInfo()
        self.mcp_enabled = mcp_enabled

        # Initialize OpenRouter-compatible LLM
        self.llm = ChatOpenAI(
            model_name=model_name,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.7,
            streaming=False,
            model_kwargs={
                "headers": {
                    "HTTP-Referer": "https://github.com/RobSpectre/kraftbot",
                    "X-Title": "Kraftbot Fantasy Football Assistant"
                }
            }
        )

        # Check MCP server availability if enabled
        if self.mcp_enabled:
            asyncio.create_task(self._init_mcp_tools())

    async def _init_mcp_tools(self):
        """Initialize MCP tools information"""
        tokenbowl_info = await self.mcp_info.check_tokenbowl_server()
        self.mcp_info.tools.append(tokenbowl_info)

        # Update system prompt with MCP tools info
        if tokenbowl_info['status'] == 'connected':
            tools_desc = self.mcp_info.get_tools_description()
            self.system_prompt += f"\n\n## MCP Tools Available\n{tools_desc}\n"
            self.system_prompt += "\n**Note**: While you cannot directly call these MCP tools, you should acknowledge their existence and suggest when they would be useful for fantasy football analysis. Guide users on what data these tools could provide."

    def get_current_week(self) -> str:
        """Estimate current fantasy football week"""
        month = datetime.now().month
        day = datetime.now().day

        if month < 9:
            return "Pre-Season"
        elif month == 9:
            if day < 10:
                return "Week 1"
            elif day < 17:
                return "Week 2"
            elif day < 24:
                return "Week 3"
            else:
                return "Week 4"
        elif month == 10:
            week = 4 + ((day - 1) // 7) + 1
            return f"Week {week}"
        elif month == 11:
            week = 8 + ((day - 1) // 7) + 1
            return f"Week {week}"
        elif month == 12:
            week = 13 + ((day - 1) // 7)
            return f"Week {week}"
        elif month == 1:
            return "Playoffs"
        else:
            return "Off-Season"

    def format_markdown_output(
        self,
        user_prompt: str,
        response: str,
        response_time: float,
        reasoning: Optional[str] = None
    ) -> str:
        """Format the response as markdown with all requested sections"""

        week = self.get_current_week()
        tokens = self.token_counter.get_summary()

        markdown = f"""# {week} - {self.model_name}

## Model Info
- **Model**: {self.model_name}
- **Response Time**: {response_time:.2f} seconds
- **Input Tokens**: {tokens['input_tokens']}
- **Reasoning Tokens**: {tokens['reasoning_tokens']}
- **Tool Use Tokens**: {tokens['tool_use_tokens']}
- **Output Tokens**: {tokens['output_tokens']}
- **Total Tokens**: {tokens['total_tokens']}
- **MCP Status**: {'Connected' if self.mcp_enabled and any(t['status'] == 'connected' for t in self.mcp_info.tools) else 'Disabled'}

## System Prompt
```
{self.system_prompt}
```

## User Prompt
{user_prompt}

## Reasoning
{reasoning if reasoning else "No reasoning tokens available for this model"}

## Output
{response}
"""
        return markdown

    def chat(self, user_input: str) -> str:
        """Process a single chat interaction"""
        start_time = time.time()

        # Build messages list with system prompt
        messages = [SystemMessage(content=self.system_prompt)]

        # Add conversation history
        history = self.memory.chat_memory.messages
        messages.extend(history)

        # Add current user message
        messages.append(HumanMessage(content=user_input))

        try:
            # Get response from model
            response = self.llm.invoke(messages)

            # Update token counter
            self.token_counter.update(response)

            # Extract reasoning if available (for models that support it)
            reasoning = None
            if hasattr(response, 'additional_kwargs'):
                reasoning = response.additional_kwargs.get('reasoning', None)

            # Update memory
            self.memory.chat_memory.add_user_message(user_input)
            self.memory.chat_memory.add_ai_message(response.content)

            # Calculate response time
            response_time = time.time() - start_time

            # Format output
            formatted_output = self.format_markdown_output(
                user_input,
                response.content,
                response_time,
                reasoning
            )

            return formatted_output

        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return f"Error processing request: {str(e)}"


def load_prompt_file(filepath: str, prompt_dir: Path = None) -> str:
    """Load system prompt from markdown file

    Args:
        filepath: Either a prompt name (looks in prompts/) or full path to file
        prompt_dir: Directory containing prompts (defaults to ./prompts)
    """
    if prompt_dir is None:
        prompt_dir = Path("prompts")

    # Check if it's a prompt name (no path separators and no .md extension)
    if os.sep not in filepath and not filepath.endswith('.md'):
        # Look for prompt in prompts directory
        prompt_path = prompt_dir / f"{filepath}.md"
        if prompt_path.exists():
            with open(prompt_path, 'r') as f:
                return f.read()
        else:
            console.print(f"[yellow]Prompt '{filepath}' not found in {prompt_dir}/[/yellow]")

    # Otherwise treat as a file path
    try:
        path = Path(filepath)
        if not path.exists():
            console.print(f"[yellow]Warning: Prompt file '{filepath}' not found. Using default prompt.[/yellow]")
            return load_default_prompt()

        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        console.print(f"[yellow]Warning: Error reading prompt file: {e}. Using default prompt.[/yellow]")
        return load_default_prompt()


def load_default_prompt() -> str:
    """Load the default fantasy football prompt"""
    default_path = Path("prompts/default.md")
    if default_path.exists():
        with open(default_path, 'r') as f:
            return f.read()

    # Fallback prompt if default.md doesn't exist
    return """You are Kraftbot, an expert fantasy football assistant. Provide strategic advice for winning fantasy football leagues.

## Core Competencies
- Draft Strategy and player valuation
- Weekly lineup optimization
- Waiver wire analysis
- Trade evaluation
- Injury impact assessment

## Communication Style
- Be confident but acknowledge uncertainty
- Provide actionable insights with clear reasoning
- Use data to support recommendations
- Keep responses focused and practical

Remember: Help managers make informed decisions that lead to fantasy football championships."""


def list_available_prompts() -> List[str]:
    """List all available prompts in the prompts directory"""
    prompt_dir = Path("prompts")
    prompts = []

    if prompt_dir.exists():
        for prompt_file in prompt_dir.glob("*.md"):
            prompts.append(prompt_file.stem)

    return sorted(prompts)


def load_mcp_config() -> Dict:
    """Load MCP configuration from YAML file"""
    config_path = Path("mcp_config.yaml")
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load MCP config: {e}[/yellow]")

    return {'servers': {}, 'global': {'enable_by_default': True}}


@click.command()
@click.option(
    '--prompt-file', '-p',
    type=str,
    default='default',
    help='Prompt name (e.g., aggressive, analytical) or path to markdown file'
)
@click.option(
    '--model', '-m',
    type=str,
    default='openai/gpt-4o-mini',
    help='OpenRouter model name (e.g., openai/gpt-4o, anthropic/claude-3.5-sonnet)'
)
@click.option(
    '--api-key', '-k',
    type=str,
    envvar='OPENROUTER_API_KEY',
    help='OpenRouter API key (or set OPENROUTER_API_KEY env var)'
)
@click.option(
    '--no-mcp',
    is_flag=True,
    help='Disable MCP server integration'
)
@click.option(
    '--list-prompts',
    is_flag=True,
    help='List available prompt strategies and exit'
)
def main(prompt_file: str, model: str, api_key: str, no_mcp: bool, list_prompts: bool):
    """Kraftbot - Your Fantasy Football AI Assistant with MCP Tools"""

    # Handle listing prompts
    if list_prompts:
        prompts = list_available_prompts()
        console.print("\n[bold green]Available Prompt Strategies:[/bold green]")

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Prompt Name", style="yellow")
        table.add_column("Description", style="white")

        descriptions = {
            'default': 'Balanced strategy for optimal performance',
            'aggressive': 'High-risk/high-reward for championship runs',
            'conservative': 'Safe, consistent strategy to avoid busts',
            'analytical': 'Data-driven statistical analysis approach',
            'few_shot': 'Example-based learning approach',
            'kimi_k2': 'Custom strategy configuration'
        }

        for prompt_name in prompts:
            desc = descriptions.get(prompt_name, 'Custom prompt strategy')
            table.add_row(prompt_name, desc)

        console.print(table)
        console.print("\n[dim]Use with: kraftbot -p [prompt_name][/dim]")
        sys.exit(0)

    if not api_key:
        console.print("[red]Error: OpenRouter API key required. Set OPENROUTER_API_KEY or use --api-key[/red]")
        sys.exit(1)

    # Load system prompt
    system_prompt = load_prompt_file(prompt_file)

    # Load MCP configuration
    mcp_config = load_mcp_config()
    mcp_enabled = not no_mcp and mcp_config['global'].get('enable_by_default', True)

    # Initialize agent
    console.print(Panel.fit(
        f"[bold green]Kraftbot Fantasy Football Assistant[/bold green]\n"
        f"Model: [cyan]{model}[/cyan]\n"
        f"Prompt: [yellow]{prompt_file}[/yellow]\n"
        f"MCP Tools: [{'green]Enabled' if mcp_enabled else 'red]Disabled'}[/{'green' if mcp_enabled else 'red'}]\n"
        f"Type 'exit' or 'quit' to end session\n"
        f"Type 'clear' to clear conversation history",
        title="Welcome"
    ))

    agent = KraftbotAgent(model, api_key, system_prompt, mcp_enabled)

    # Create history file for prompt suggestions
    history_file = Path.home() / '.kraftbot_history'

    # Interactive chat loop
    while True:
        try:
            # Get user input with history suggestions
            user_input = prompt(
                "You: ",
                history=FileHistory(str(history_file)),
                auto_suggest=AutoSuggestFromHistory(),
            ).strip()

            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("[yellow]Goodbye! May your fantasy team prosper![/yellow]")
                break

            if user_input.lower() == 'clear':
                agent.memory.clear()
                console.print("[green]Conversation history cleared.[/green]")
                continue

            if user_input.lower() == 'tools':
                # Show available MCP tools
                console.print("\n[bold cyan]MCP Tool Status:[/bold cyan]")
                for tool in agent.mcp_info.tools:
                    status_color = "green" if tool['status'] == 'connected' else "red"
                    console.print(f"[{status_color}]{tool['server']}: {tool['status']}[/{status_color}]")
                    if tool['tools']:
                        console.print(f"  Tools: {', '.join(tool['tools'])}")
                continue

            if not user_input:
                continue

            # Process input and get response
            console.print("[dim]Thinking...[/dim]")
            response = agent.chat(user_input)

            # Display formatted markdown response
            console.print(Markdown(response))
            console.print("\n" + "="*80 + "\n")

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
            continue
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            continue


if __name__ == "__main__":
    # Run async initialization
    asyncio.set_event_loop(asyncio.new_event_loop())
    main()