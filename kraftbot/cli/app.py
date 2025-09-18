"""
Main CLI application setup for KraftBot.
"""

import typer

from .commands import chat, models, test, compare, mcp_info, status, prompts
from .utils import console


def create_app() -> typer.Typer:
    """Create and configure the main CLI application"""
    
    app = typer.Typer(
        name="kraftbot",
        help="🚀 KraftBot - Advanced PydanticAI Agent with OpenRouter & MCP Support",
        epilog="Built with ❤️  using PydanticAI, OpenRouter, and MCP",
        rich_markup_mode="rich",
        add_completion=False,
        no_args_is_help=True
    )
    
    # Register commands
    app.command(name="chat")(chat)
    app.command(name="models")(models) 
    app.command(name="test")(test)
    app.command(name="compare")(compare)
    app.command(name="mcp")(mcp_info)
    app.command(name="status")(status)
    app.command(name="prompts")(prompts)
    
    return app


def main():
    """Main entry point for the CLI"""
    app = create_app()
    
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n👋 [yellow]Goodbye![/yellow]")
    except Exception as e:
        console.print(f"\n💥 [red]Unexpected error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    main()