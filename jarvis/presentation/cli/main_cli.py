"""
Typer CLI Interface for JARVIS AI Operating System.
Provides command-line management for starting the kernel, submitting processes, and querying system metrics.
"""

import asyncio
import json
import sys
import httpx
import typer
import uvicorn
from jarvis import __version__
from jarvis.config import settings

app = typer.Typer(
    name="jarvis",
    help="JARVIS AI Operating System Command-Line Control Center",
    add_completion=False
)

process_app = typer.Typer(help="Manage Agent Processes")
memory_app = typer.Typer(help="Query and Manage Vector Memory")
app.add_typer(process_app, name="process")
app.add_typer(memory_app, name="memory")


@app.command()
def start(
    host: str = typer.Option(settings.HOST, "--host", "-h", help="Bind host address"),
    port: int = typer.Option(settings.PORT, "--port", "-p", help="Bind port number"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload for development")
) -> None:
    """Starts the JARVIS AI OS Kernel API & Telemetry Server."""
    typer.echo(f"🤖 Launching JARVIS AI Operating System Kernel v{__version__}...")
    uvicorn.run("jarvis.presentation.api.server:app", host=host, port=port, reload=reload)


@app.command()
def health() -> None:
    """Checks real-time health of running kernel server."""
    url = f"http://{settings.HOST}:{settings.PORT}/api/v1/health"
    try:
        response = httpx.get(url, timeout=5.0)
        if response.status_code == 200:
            typer.echo("✅ System Status: HEALTHY")
            typer.echo(json.dumps(response.json(), indent=2))
        else:
            typer.echo(f"⚠️ Health check failed: {response.status_code}")
    except Exception as e:
        typer.echo(f"❌ Could not connect to running JARVIS Kernel at {url}: {e}")
        typer.echo("Hint: Run 'jarvis start' in a separate terminal.")


@process_app.command("submit")
def submit_process(
    agent: str = typer.Option("Agent-01", "--agent", "-a", help="Agent name"),
    goal: str = typer.Option(..., "--goal", "-g", help="Task objective goal"),
    priority: int = typer.Option(2, "--priority", "-p", help="Priority (0=CRITICAL, 1=HIGH, 2=NORMAL, 3=LOW)")
) -> None:
    """Submits a new agent process to the OS kernel."""
    url = f"http://{settings.HOST}:{settings.PORT}/api/v1/processes"
    payload = {
        "agent_name": agent,
        "role": "Autonomous Operator",
        "goal": goal,
        "priority": priority,
        "max_steps": 10,
        "permissions": ["READ_ONLY", "FILE_WRITE", "SYSTEM_EXECUTE"]
    }
    try:
        resp = httpx.post(url, json=payload, timeout=10.0)
        if resp.status_code in (200, 201):
            typer.echo("🚀 Agent Process Successfully Submitted!")
            typer.echo(json.dumps(resp.json(), indent=2))
        else:
            typer.echo(f"❌ Process Submission Error: {resp.status_code} - {resp.text}")
    except Exception as e:
        typer.echo(f"❌ Failed to reach kernel at {url}: {e}")


@process_app.command("list")
def list_processes() -> None:
    """Lists all active and completed processes."""
    url = f"http://{settings.HOST}:{settings.PORT}/api/v1/processes"
    try:
        resp = httpx.get(url, timeout=5.0)
        if resp.status_code == 200:
            typer.echo(json.dumps(resp.json(), indent=2))
        else:
            typer.echo(f"❌ Error fetching processes: {resp.text}")
    except Exception as e:
        typer.echo(f"❌ Connection error: {e}")


@memory_app.command("search")
def search_memory(
    query: str = typer.Option(..., "--query", "-q", help="Search query text"),
    top_k: int = typer.Option(5, "--top-k", "-k", help="Top-K memory results")
) -> None:
    """Performs semantic similarity search over vector memory store."""
    url = f"http://{settings.HOST}:{settings.PORT}/api/v1/memory/search"
    payload = {"query": query, "top_k": top_k, "min_similarity": 0.3}
    try:
        resp = httpx.post(url, json=payload, timeout=10.0)
        if resp.status_code == 200:
            typer.echo(json.dumps(resp.json(), indent=2))
        else:
            typer.echo(f"❌ Memory Search Error: {resp.text}")
    except Exception as e:
        typer.echo(f"❌ Connection error: {e}")


if __name__ == "__main__":
    app()
