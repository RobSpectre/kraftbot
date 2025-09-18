"""
CLI command implementations for KraftBot.
"""

import asyncio
import time
from typing import List, Optional

import typer
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.rule import Rule
from rich.status import Status

from ..config.settings import settings
from ..core.agent import PydanticAIAgent
from ..utils.prompt_loader import prompt_loader
from .utils import (
    check_environment,
    console,
    display_model_table,
    display_response,
    display_system_status,
    print_banner,
)

# Global agent instance
agent: Optional[PydanticAIAgent] = None


async def display_streaming_response(
    user_input: str,
    agent: PydanticAIAgent,
    user_id: str,
    session_id: str,
    start_time: float,
):
    """Display streaming response with markdown formatting"""
    from rich.live import Live
    from rich.markdown import Markdown
    from rich.panel import Panel

    accumulated_text = ""

    console.print("🧠 [cyan]KraftBot:[/cyan]")

    with Live(refresh_per_second=10, console=console) as live:
        try:
            async for token in agent.run_stream(user_input, user_id, session_id):
                accumulated_text += str(token)

                # Display current markdown content
                markdown_content = Markdown(accumulated_text)
                elapsed_time = time.time() - start_time
                panel = Panel(
                    markdown_content,
                    title=f"Response ({elapsed_time:.1f}s)",
                    border_style="green",
                    padding=(0, 1),
                )
                live.update(panel)

                # Timeout protection
                if elapsed_time > settings.request_timeout:
                    console.print(f"\n⏰ [yellow]Response timeout after {settings.request_timeout}s[/yellow]")
                    break

        except Exception as e:
            console.print(f"❌ [red]Streaming error: {e}[/red]")
            # Fallback to non-streaming
            try:
                response = await agent.run(user_input, user_id, session_id)
                display_response(response, time.time() - start_time)
            except Exception as fallback_error:
                console.print(f"❌ [red]Fallback error: {fallback_error}[/red]")


async def initialize_agent(model: str = None, prompt: str = None) -> bool:
    """Initialize the agent with loading animation"""
    global agent

    if not settings.is_api_key_configured():
        console.print("❌ [red]OPENROUTER_API_KEY not found![/red]")
        console.print("💡 Get your API key from: https://openrouter.ai/")
        return False

    model_name = model or settings.default_model

    # Load system prompt if specified
    system_prompt = None
    if prompt:
        system_prompt = prompt_loader.load_prompt(prompt)
        if not system_prompt:
            console.print(
                f"⚠️  [yellow]Could not load prompt '{prompt}', using default[/yellow]"
            )
        else:
            console.print(f"✅ [green]Loaded system prompt: {prompt}[/green]")

    with Status("🚀 Initializing KraftBot agent...", console=console, spinner="dots"):
        try:
            agent = PydanticAIAgent(
                openrouter_api_key=settings.openrouter_api_key,
                model_name=model_name,
                system_prompt=system_prompt,
                enable_logfire=settings.enable_logfire,
            )
            if settings.cli_animations:
                await asyncio.sleep(1)  # Dramatic pause

        except Exception as e:
            console.print(f"❌ [red]Failed to initialize agent: {e}[/red]")
            return False

    # Success message
    console.print("✨ [green bold]KraftBot initialized successfully![/green bold]")

    # Display model info
    if settings.verbose_logging:
        model_config = settings.get_model_config(model_name)
        if model_config:
            import rich.box
            from rich.table import Table

            model_info = Table(show_header=False, box=rich.box.ROUNDED)
            model_info.add_column("Property", style="bold cyan")
            model_info.add_column("Value", style="white")

            model_info.add_row("🤖 Model", model_name)
            model_info.add_row("🏢 Provider", model_config.provider)
            model_info.add_row("🔌 Transport", "OpenRouter")
            model_info.add_row(
                "📊 Observability",
                "Enabled" if settings.is_logfire_configured() else "Disabled",
            )

            console.print(
                Panel(model_info, title="🔧 Agent Configuration", border_style="green")
            )

    return True


async def chat_async(
    model: str = typer.Option(
        None,
        "--model",
        "-m",
        help="Model to use (defaults to configured default model)",
    ),
    prompt: str = typer.Option(
        None,
        "--prompt",
        "-p",
        help="System prompt name (e.g., 'default', 'aggressive') or file path (e.g., '/path/to/prompt.md')",
    ),
    user_id: str = typer.Option(
        None,
        "--user",
        "-u",
        help="User ID for session tracking (defaults to configured default)",
    ),
):
    """🎯 Start an interactive chat session with KraftBot"""
    print_banner()

    if not check_environment():
        raise typer.Exit(1)

    # Initialize agent
    if not asyncio.run(initialize_agent(model, prompt)):
        raise typer.Exit(1)

    console.print(Rule("🎯 Interactive Chat Mode", style="bright_cyan"))
    console.print("[dim]Type 'quit', 'exit', or press Ctrl+C to end the session[/dim]")
    console.print("[dim]Use ↑/↓ arrow keys to navigate command history[/dim]\n")

    session_id = f"chat_{int(time.time())}"
    message_count = 0
    user_id = user_id or settings.default_user_id

    # Create command history
    history = InMemoryHistory()

    # Define style for prompt
    prompt_style = Style.from_dict(
        {
            "prompt": "#00aa00 bold",  # Green and bold
            "count": "#666666",  # Gray
        }
    )

    try:
        while True:
            # Interactive prompt with history support
            try:
                user_input = prompt(
                    f"You ({message_count + 1}): ", history=history, style=prompt_style
                ).strip()
            except EOFError:
                # Handle Ctrl+D
                console.print(
                    "\n👋 [yellow]Thanks for chatting with KraftBot![/yellow]"
                )
                break

            if user_input.lower() in ["quit", "exit", "q"]:
                console.print(
                    "\n👋 [yellow]Thanks for chatting with KraftBot![/yellow]"
                )
                break

            if not user_input:
                continue

            # Stream response
            start_time = time.time()
            try:
                await display_streaming_response(
                    user_input, agent, user_id, session_id, start_time
                )
            except Exception as e:
                console.print(f"❌ [red]Error: {e}[/red]")
                continue
            message_count += 1
            console.print()  # Add spacing

    except KeyboardInterrupt:
        console.print("\n👋 [yellow]Session ended by user[/yellow]")


def chat(
    model: str = typer.Option(
        None,
        "--model",
        "-m",
        help="Model to use (defaults to configured default model)",
    ),
    prompt: str = typer.Option(
        None,
        "--prompt",
        "-p",
        help="System prompt name (e.g., 'default', 'aggressive') or file path (e.g., '/path/to/prompt.md')",
    ),
    user_id: str = typer.Option(
        None,
        "--user",
        "-u",
        help="User ID for session tracking (defaults to configured default)",
    ),
):
    """🎯 Start an interactive chat session with KraftBot"""
    asyncio.run(chat_async(model, prompt, user_id))


def models():
    """📋 List available models and their capabilities"""
    print_banner()
    display_model_table()


def test(
    model: str = typer.Option(
        None, "--model", "-m", help="Model to test (defaults to configured default)"
    ),
    prompt: str = typer.Option(
        "Hello! Please introduce yourself briefly.",
        "--prompt",
        "-p",
        help="Test prompt to send",
    ),
    system_prompt: str = typer.Option(
        None,
        "--system-prompt",
        "-s",
        help="System prompt name (e.g., 'default', 'aggressive') or file path (e.g., '/path/to/prompt.md')",
    ),
):
    """🧪 Test a specific model with a prompt"""
    print_banner()

    if not check_environment():
        raise typer.Exit(1)

    model_name = model or settings.default_model
    console.print(f"🧪 [bold cyan]Testing model:[/bold cyan] {model_name}")
    console.print(f"📝 [bold cyan]Prompt:[/bold cyan] {prompt}\n")

    async def run_test():
        if not await initialize_agent(model_name, system_prompt):
            return False

        start_time = time.time()

        console.print("🔬 [cyan]Running test...[/cyan]\n")
        try:
            await display_streaming_response(
                prompt, agent, "test_user", "test_session", start_time
            )
            console.print("\n✅ [green]Test completed successfully![/green]")
        except Exception as e:
            console.print(f"❌ [red]Test failed: {e}[/red]")
            return False
        return True

    success = asyncio.run(run_test())
    if not success:
        raise typer.Exit(1)


def compare(
    prompt: str = typer.Option(
        "Explain quantum computing in simple terms",
        "--prompt",
        "-p",
        help="Prompt to compare across models",
    ),
    models: Optional[List[str]] = typer.Option(
        None, "--model", "-m", help="Models to compare (can be used multiple times)"
    ),
):
    """⚖️ Compare responses from different models"""
    print_banner()

    if not check_environment():
        raise typer.Exit(1)

    if not models:
        # Use top 3 models by default
        model_names = list(settings.available_models.keys())[:3]
    else:
        model_names = models

    console.print(f"⚖️  [bold cyan]Comparing {len(model_names)} models[/bold cyan]")
    console.print(f"📝 [bold cyan]Prompt:[/bold cyan] {prompt}\n")

    async def run_comparison():
        results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:

            task = progress.add_task("Testing models...", total=len(model_names))

            for model_name in model_names:
                progress.update(task, description=f"Testing {model_name}")

                try:
                    if not await initialize_agent(model_name):
                        results.append((model_name, None, "Initialization failed"))
                        continue

                    start_time = time.time()
                    response = await agent.run(
                        prompt, "compare_user", "compare_session"
                    )
                    duration = time.time() - start_time

                    results.append((model_name, response, duration))

                except Exception as e:
                    results.append((model_name, None, str(e)))

                progress.advance(task)

        # Display comparison results
        console.print("\n" + "=" * 80)
        console.print("📊 [bold cyan]Comparison Results[/bold cyan]")
        console.print("=" * 80)

        for i, (model_name, response, duration) in enumerate(results, 1):
            console.print(f"\n🤖 [bold yellow]Model {i}: {model_name}[/bold yellow]")

            if response is None:
                console.print(f"❌ [red]Error: {duration}[/red]")
                continue

            # Create a simple display - Logfire handles detailed stats automatically
            response_text = (
                str(response.response)
                if not callable(response.response)
                else str(response.response())
            )
            response_preview = (
                response_text[:200] + "..."
                if len(response_text) > 200
                else response_text
            )

            console.print(
                Panel(
                    response_preview,
                    title=f"Response Preview ({duration:.1f}s)",
                    border_style="dim",
                )
            )

    asyncio.run(run_comparison())


def prompts():
    """List and manage available system prompts"""
    console.print("\n📝 [bold cyan]Available System Prompts[/bold cyan]")
    console.print("=" * 60)

    available_prompts = prompt_loader.list_available_prompts()

    if not available_prompts:
        console.print("❌ [red]No prompt files found[/red]")
        console.print("💡 Add .md files to kraftbot/prompts/ directory")
        return

    for prompt_name in available_prompts:
        is_valid, error = prompt_loader.validate_prompt(prompt_name)
        status = "✅" if is_valid else "❌"

        # Load prompt to show preview
        content = prompt_loader.load_prompt(prompt_name)
        preview = (
            content[:100] + "..."
            if content and len(content) > 100
            else content or "Error loading"
        )

        console.print(f"\n{status} [bold]{prompt_name}[/bold]")
        console.print(f"   {preview}")

        if not is_valid and error:
            console.print(f"   [red]Error: {error}[/red]")

    console.print(f"\n💡 [dim]Usage: python main.py chat --prompt <name_or_path>[/dim]")
    console.print(f"💡 [dim]Example: python main.py chat --prompt aggressive[/dim]")
    console.print(
        f"💡 [dim]Example: python main.py chat --prompt /path/to/my_prompt.md[/dim]"
    )


def mcp_info():
    """🔌 Show MCP (Model Context Protocol) information"""
    print_banner()

    console.print(
        Panel(
            Markdown(
                """
# 🔌 Model Context Protocol (MCP) Integration

KraftBot supports connecting to external tools and services via MCP servers:

## Available Transport Types

### 🔄 STDIO (Standard Input/Output)
- Runs MCP server as subprocess
- Best for local tools and services
- Example: Python execution, file operations

### 🌐 SSE (Server-Sent Events)  
- Connects to HTTP-based MCP servers
- Best for web services and APIs
- Example: weather services, databases

### 📡 HTTP (RESTful API)
- Traditional HTTP request/response
- Best for simple integrations
- Example: calculators, converters

## Popular MCP Servers

- **🐍 MCP Run Python**: Execute Python code safely
- **🌤️  Weather Services**: Get real-time weather data  
- **💾 Database Connectors**: Query SQL databases
- **🔍 Web Search**: Search the internet
- **📁 File Operations**: Read/write files securely

## Adding MCP Servers (Programmatically)

```python
from kraftbot import PydanticAIAgent

agent = PydanticAIAgent(api_key="your-key")

# Add STDIO server
agent.add_mcp_server_stdio('deno', ['run', 'server.js'])

# Add SSE server  
agent.add_mcp_server_sse('http://localhost:3001/sse')
```
        """
            ),
            title="🔌 MCP Integration Guide",
            border_style="bright_blue",
            padding=(1, 2),
        )
    )


def status():
    """📊 Show detailed system status and configuration"""
    print_banner()
    display_system_status()
