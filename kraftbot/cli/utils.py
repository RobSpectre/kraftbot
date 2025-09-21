"""
CLI utility functions and shared components.
"""

import os
from typing import Any, Dict

import rich.box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..config.settings import settings

# Initialize Rich console with settings
console = Console(
    force_terminal=True,
    color_system="truecolor" if settings.cli_color else "standard",
    width=settings.cli_width,
    legacy_windows=False,
)


def print_banner():
    """Print the epic KraftBot banner"""
    banner = """
██╗  ██╗██████╗  █████╗ ███████╗████████╗██████╗  ██████╗ ████████╗
██║ ██╔╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔═══██╗╚══██╔══╝
█████╔╝ ██████╔╝███████║█████╗     ██║   ██████╔╝██║   ██║   ██║   
██╔═██╗ ██╔══██╗██╔══██║██╔══╝     ██║   ██╔══██╗██║   ██║   ██║   
██║  ██╗██║  ██║██║  ██║██║        ██║   ██████╔╝╚██████╔╝   ██║   
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝        ╚═╝   ╚═════╝  ╚═════╝    ╚═╝   
    """

    panel = Panel(
        Align.center(
            Text(banner, style="bold magenta")
            + Text(
                "\n🏈 Fantasy Football Management Agent\n",
                style="bold cyan",
            )
            + Text("Powered by AI insights for dominating your league!", style="dim")
        ),
        border_style="bright_blue",
        box=rich.box.DOUBLE_EDGE,
        padding=(1, 2),
    )
    console.print(panel)


def check_environment() -> bool:
    """Check and display environment status with style"""
    console.print("\n🔍 [bold cyan]Environment Check[/bold cyan]")

    status_table = Table(show_header=False, box=rich.box.SIMPLE, padding=(0, 2))
    status_table.add_column("Service", style="bold")
    status_table.add_column("Status", justify="center")

    env_status = settings.validate_environment()

    for service, info in env_status.items():
        service_name = service.replace("_", " ").title()
        status_text = info["status"]
        status_table.add_row(service_name, status_text)

    # Add Python version check
    import sys

    python_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    python_status = (
        "✅ [green]Compatible[/green]"
        if sys.version_info >= (3, 9)
        else "❌ [red]Too Old[/red]"
    )
    status_table.add_row("Python Version", f"{python_version} {python_status}")

    console.print(Panel(status_table, title="🔧 System Status", border_style="blue"))

    return settings.is_api_key_configured()


def display_response(response, thinking_time: float):
    """Display agent response with beautiful formatting"""
    from rich.markdown import Markdown

    # Create response panel with gradient-like effect
    # Safely get response text, handling method objects
    response_text = response.response
    if callable(response_text):
        response_text = response_text()

    response_panel = Panel(
        Markdown(str(response_text)),
        title=f"🧠 KraftBot Response ({thinking_time:.1f}s)",
        border_style="bright_green",
        padding=(1, 2),
    )
    console.print(response_panel)

    # Stats are now handled automatically by Logfire - no need for local display


def display_model_table():
    """Display available models in a beautiful table"""
    table = Table(
        title="🤖 Available Models via OpenRouter",
        box=rich.box.ROUNDED,
        title_style="bold magenta",
        header_style="bold cyan",
    )

    table.add_column("Model", style="bold white", width=35)
    table.add_column("Provider", style="blue", width=12)
    table.add_column("Strengths", style="green", width=25)
    table.add_column("Speed", style="yellow", width=10)
    table.add_column("Cost", style="red", width=10)

    for model_name, model_config in settings.available_models.items():
        table.add_row(
            model_name,
            model_config.provider,
            ", ".join(model_config.strengths[:3]),  # Limit to first 3 strengths
            model_config.speed,
            model_config.cost,
        )

    console.print(table)
    console.print("\n💡 [dim]Use --model flag to specify which model to use[/dim]")


def display_system_status():
    """Display detailed system status"""
    import platform
    import sys
    from datetime import datetime
    from pathlib import Path

    # System info
    system_info = Table(title="🖥️  System Information", box=rich.box.ROUNDED)
    system_info.add_column("Property", style="bold cyan")
    system_info.add_column("Value", style="white")

    system_info.add_row("Operating System", f"{platform.system()} {platform.release()}")
    system_info.add_row("Python Version", f"{sys.version.split()[0]}")
    system_info.add_row("Current Time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    system_info.add_row("Working Directory", str(Path.cwd()))

    console.print(system_info)

    # Environment variables
    env_info = Table(title="🔑 Environment Configuration", box=rich.box.ROUNDED)
    env_info.add_column("Variable", style="bold cyan")
    env_info.add_column("Status", style="white")

    env_vars = [
        ("OPENROUTER_API_KEY", "OpenRouter API access"),
        ("LOGFIRE_WRITE_TOKEN", "Logfire observability"),
        ("DEFAULT_MODEL", "Default model setting"),
        ("CLI_WIDTH", "Terminal width setting"),
    ]

    for var_name, description in env_vars:
        value = getattr(settings, var_name.lower(), None) or os.getenv(var_name)
        if value:
            if "KEY" in var_name or "TOKEN" in var_name:
                status = f"✅ Set ({str(value)[:8]}...)"
            else:
                status = f"✅ {str(value)[:50]}..."
        else:
            status = "❌ Not set"

        env_info.add_row(var_name, status)

    console.print(env_info)
