#!/usr/bin/env python3
"""
Kraftbot - Fantasy Football Assistant with Langchain and OpenRouter
"""

import os
import sys
import time
import json
import click
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from langchain.chat_models.base import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.callbacks import get_openai_callback
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

console = Console()


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
    """Main Kraftbot agent with memory and OpenRouter support"""

    def __init__(self, model_name: str, api_key: str, system_prompt: str):
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.memory = ConversationBufferMemory(return_messages=True)
        self.token_counter = TokenCounter()

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

    def get_current_week(self) -> str:
        """Estimate current fantasy football week"""
        # Fantasy season typically starts early September
        # This is a simple estimation - you can make it more sophisticated
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


def load_prompt_file(filepath: str) -> str:
    """Load system prompt from markdown file"""
    try:
        path = Path(filepath)
        if not path.exists():
            console.print(f"[yellow]Warning: Prompt file '{filepath}' not found. Using default prompt.[/yellow]")
            return "You are Kraftbot, an expert fantasy football assistant. Provide strategic advice for winning fantasy football leagues."

        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        console.print(f"[yellow]Warning: Error reading prompt file: {e}. Using default prompt.[/yellow]")
        return "You are Kraftbot, an expert fantasy football assistant. Provide strategic advice for winning fantasy football leagues."


@click.command()
@click.option(
    '--prompt-file', '-p',
    type=click.Path(exists=False),
    default='system_prompt.md',
    help='Path to markdown file containing system prompt'
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
def main(prompt_file: str, model: str, api_key: str):
    """Kraftbot - Your Fantasy Football AI Assistant"""

    if not api_key:
        console.print("[red]Error: OpenRouter API key required. Set OPENROUTER_API_KEY or use --api-key[/red]")
        sys.exit(1)

    # Load system prompt
    system_prompt = load_prompt_file(prompt_file)

    # Initialize agent
    console.print(Panel.fit(
        f"[bold green]Kraftbot Fantasy Football Assistant[/bold green]\n"
        f"Model: [cyan]{model}[/cyan]\n"
        f"Type 'exit' or 'quit' to end session\n"
        f"Type 'clear' to clear conversation history",
        title="Welcome"
    ))

    agent = KraftbotAgent(model, api_key, system_prompt)

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
    main()