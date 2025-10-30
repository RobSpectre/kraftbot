#!/usr/bin/env python3
"""
Kraftbot CLI Application
"""

import os
import sys
import asyncio
from pathlib import Path

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from kraftbot.core.agent import KraftbotAgent
from kraftbot.utils.prompts import load_prompt, list_prompts, get_prompt_description

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="kraftbot")
def cli():
    """Kraftbot - Fantasy Football AI Assistant

    A Langchain-based conversational AI agent with OpenRouter integration,
    MCP server support, and comprehensive token tracking.
    """
    pass


@cli.command()
@click.option(
    '--prompt', '-p',
    type=str,
    default='default',
    help='Prompt name or path to markdown file'
)
@click.option(
    '--model', '-m',
    type=str,
    default='openai/gpt-4o-mini',
    help='OpenRouter model name'
)
@click.option(
    '--api-key', '-k',
    type=str,
    envvar='OPENROUTER_API_KEY',
    help='OpenRouter API key'
)
@click.option(
    '--no-mcp',
    is_flag=True,
    help='Disable MCP server integration'
)
@click.option(
    '--no-stream',
    is_flag=True,
    help='Disable streaming output'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Enable verbose output'
)
def chat(prompt, model, api_key, no_mcp, no_stream, verbose):
    """Start an interactive chat session"""

    if not api_key:
        console.print("[red]Error: OpenRouter API key required.[/red]")
        console.print("Set OPENROUTER_API_KEY environment variable or use --api-key")
        sys.exit(1)

    # Load system prompt
    system_prompt = load_prompt(prompt)

    # Display welcome panel
    console.print(Panel.fit(
        f"[bold green]Kraftbot Fantasy Football Assistant[/bold green]\n"
        f"Model: [cyan]{model}[/cyan]\n"
        f"Prompt: [yellow]{prompt}[/yellow]\n"
        f"MCP: [{'green]Enabled' if not no_mcp else 'red]Disabled'}[/]\n"
        f"Streaming: [{'green]Enabled' if not no_stream else 'red]Disabled'}[/]\n\n"
        f"[dim]Commands: exit, quit, clear, tools, help[/dim]",
        title="Welcome"
    ))

    # Initialize agent
    agent = KraftbotAgent(
        model_name=model,
        api_key=api_key,
        system_prompt=system_prompt,
        mcp_enabled=not no_mcp,
        verbose=verbose
    )

    # Run async initialization
    asyncio.run(agent.initialize())

    # Show MCP status if verbose
    if verbose and not no_mcp:
        mcp_status = agent.get_mcp_status_info()
        if mcp_status.get('connected') and mcp_status.get('tools'):
            console.print("\n[bold cyan]MCP Server Status:[/bold cyan]")
            status_color = "green" if mcp_status['connected'] else "red"
            console.print(f"[{status_color}]• Connected with {mcp_status['tools_count']} tools[/]")
            console.print("  Available tools:")
            for tool in mcp_status['tools']:
                console.print(f"    - {tool}")

    # History file
    history_file = Path.home() / '.kraftbot_history'

    # Interactive chat loop
    while True:
        try:
            # Get user input
            user_input = pt_prompt(
                "You: ",
                history=FileHistory(str(history_file)),
                auto_suggest=AutoSuggestFromHistory(),
            ).strip()

            # Handle commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("[yellow]Goodbye! May your fantasy team prosper![/yellow]")
                break

            if user_input.lower() == 'clear':
                agent.clear_memory()
                console.print("[green]Conversation history cleared.[/green]")
                continue

            if user_input.lower() == 'tools':
                show_mcp_tools(agent)
                continue

            if user_input.lower() == 'help':
                show_help()
                continue

            if not user_input:
                continue

            # Process input
            console.print("[dim]Thinking...[/dim]")

            try:
                # Get response (always non-streaming for proper formatting)
                if verbose:
                    console.print("[dim]Calling agent.chat()...[/dim]")
                response = asyncio.run(agent.chat(user_input))

                if verbose:
                    console.print(f"[dim]Response received, type: {type(response)}[/dim]")
                    console.print(f"[dim]Response content length: {len(response.content) if response.content else 0}[/dim]")
                    console.print(f"[dim]Response content preview: {response.content[:200] if response.content else 'None'}[/dim]")

                # Output raw markdown
                print(response.to_markdown())

                console.print("\n" + "="*80 + "\n")

            except Exception as process_err:
                console.print(f"\n[red]Error processing request: {process_err}[/red]")
                if verbose:
                    import traceback
                    console.print(f"[dim]{traceback.format_exc()}[/dim]")
                console.print("\n" + "="*80 + "\n")

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
            continue
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            if verbose:
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
            continue


@cli.command()
@click.option(
    '--prompt', '-p',
    type=str,
    required=True,
    help='Prompt name or path to markdown file'
)
@click.option(
    '--model', '-m',
    type=str,
    default='openai/gpt-4o-mini',
    help='OpenRouter model name'
)
@click.option(
    '--api-key', '-k',
    type=str,
    envvar='OPENROUTER_API_KEY',
    help='OpenRouter API key'
)
@click.option(
    '--no-mcp',
    is_flag=True,
    help='Disable MCP server integration'
)
@click.option(
    '--stream/--no-stream',
    default=True,
    help='Enable/disable streaming'
)
@click.argument('message')
def ask(prompt, model, api_key, no_mcp, stream, message):
    """Ask a single question and exit"""

    if not api_key:
        console.print("[red]Error: OpenRouter API key required.[/red]")
        sys.exit(1)

    # Load system prompt
    system_prompt = load_prompt(prompt)

    # Initialize agent
    agent = KraftbotAgent(
        model_name=model,
        api_key=api_key,
        system_prompt=system_prompt,
        mcp_enabled=not no_mcp,
        verbose=False
    )

    asyncio.run(agent.initialize())

    # Get response and output raw markdown
    response = asyncio.run(agent.chat(message))
    print(response.to_markdown())


@cli.command()
def prompts():
    """List available prompt strategies"""

    available_prompts = list_prompts()

    if not available_prompts:
        console.print("[yellow]No prompts found in prompts directory[/yellow]")
        return

    console.print("\n[bold green]Available Prompt Strategies:[/bold green]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Name", style="yellow")
    table.add_column("Description", style="white")

    for prompt_name in available_prompts:
        desc = get_prompt_description(prompt_name)
        table.add_row(prompt_name, desc)

    console.print(table)
    console.print("\n[dim]Use with: kraftbot chat -p [prompt_name][/dim]\n")


@cli.command()
@click.option(
    '--api-key', '-k',
    type=str,
    envvar='OPENROUTER_API_KEY',
    help='OpenRouter API key'
)
def status(api_key):
    """Show system status and configuration"""

    console.print("\n[bold green]Kraftbot System Status[/bold green]\n")

    # Check API key
    api_key_status = "✅ Configured" if api_key else "❌ Not set"
    console.print(f"OpenRouter API Key: {api_key_status}")

    # Check prompts
    prompts_count = len(list_prompts())
    console.print(f"Available Prompts: {prompts_count}")

    # Check MCP config
    mcp_config_path = Path("mcp_config.yaml")
    mcp_config_status = "✅ Found" if mcp_config_path.exists() else "❌ Not found"
    console.print(f"MCP Configuration: {mcp_config_status}")

    console.print()


def show_mcp_tools(agent: KraftbotAgent):
    """Show MCP tools status"""
    status_info = agent.get_mcp_status_info()

    console.print("\n[bold cyan]MCP Server Status:[/bold cyan]\n")

    if not status_info['enabled']:
        console.print("[yellow]MCP integration is disabled[/yellow]")
        return

    if not status_info.get('connected'):
        console.print("[yellow]No MCP servers connected[/yellow]")
        return

    if not status_info.get('tools'):
        console.print("[yellow]No tools available[/yellow]")
        return

    status_color = "green" if status_info['connected'] else "red"
    console.print(f"[{status_color}]• Connected with {status_info['tools_count']} tools[/]")
    console.print("\n  Available tools:")
    for tool in status_info['tools']:
        console.print(f"    - {tool}")

    console.print()


def show_help():
    """Show in-chat help"""
    help_text = """
## Available Commands

- **exit**, **quit**, **q** - End the chat session
- **clear** - Clear conversation history
- **tools** - Show MCP server and tool status
- **help** - Show this help message

## Features

- Conversational memory - context is maintained throughout the session
- MCP integration - access to fantasy football data tools
- Multiple prompt strategies - switch between different AI personalities
- Streaming responses - see answers as they're generated

Type your fantasy football questions naturally!
"""
    console.print(Markdown(help_text))


if __name__ == "__main__":
    cli()
