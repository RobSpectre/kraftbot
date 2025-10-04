"""
CLI utility functions and shared components.
"""

import os
from typing import Any, Dict

import rich.box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
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
    console.print("\n🔍 [bold cyan]Environment Check[/bold cyan]\n")

    env_status = settings.validate_environment()

    for service, info in env_status.items():
        service_name = service.replace("_", " ").title()
        status_text = info["status"]
        console.print(f"**{service_name}**: {status_text}")

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
    console.print(f"**Python Version**: {python_version} {python_status}\n")

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
    """Display available models in markdown format"""
    console.print("\n## 🤖 Available Models via OpenRouter\n")

    for model_name, model_config in settings.available_models.items():
        strengths = ", ".join(model_config.strengths[:3])
        console.print(f"### {model_name}")
        console.print(f"- **Provider**: {model_config.provider}")
        console.print(f"- **Strengths**: {strengths}")
        console.print(f"- **Speed**: {model_config.speed}")
        console.print(f"- **Cost**: {model_config.cost}")
        console.print()

    console.print("💡 [dim]Use --model flag to specify which model to use[/dim]")


def display_system_status():
    """Display detailed system status"""
    import platform
    import sys
    from datetime import datetime
    from pathlib import Path

    # System info
    console.print("\n## 🖥️  System Information\n")
    console.print(f"- **Operating System**: {platform.system()} {platform.release()}")
    console.print(f"- **Python Version**: {sys.version.split()[0]}")
    console.print(f"- **Current Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    console.print(f"- **Working Directory**: {Path.cwd()}")

    # Environment variables
    console.print("\n## 🔑 Environment Configuration\n")

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

        console.print(f"- **{var_name}**: {status}")
