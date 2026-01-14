"""CLI interface for ralph-loop."""

import subprocess
from pathlib import Path
from typing import Optional

import typer

app = typer.Typer(help="Ralph Wiggum loop for agents")


@app.command()
def run(
    prompt: Optional[str] = typer.Option(None, "-p", "--prompt", help="Inline prompt"),
    prompt_file: Optional[Path] = typer.Option(
        None, "-f", "--file", help="Prompt file (default: PROMPT.md)"
    ),
    max_iterations: int = typer.Option(
        10, "-n", "--max-iterations", help="Max iterations"
    ),
    stop_file: Optional[str] = typer.Option(
        None, "--stop-file", help="Stop when this file exists"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would run"),
) -> None:
    """Run the agent loop."""
    # Determine prompt source
    if prompt is None:
        if prompt_file is None:
            prompt_file = Path("PROMPT.md")
        if not prompt_file.exists():
            typer.echo(f"Error: Prompt file '{prompt_file}' not found", err=True)
            raise typer.Exit(1)
        prompt = prompt_file.read_text()

    if dry_run:
        typer.echo(f"Would run {max_iterations} iterations with prompt:")
        typer.echo(f"---\n{prompt}\n---")
        return

    for i in range(1, max_iterations + 1):
        typer.echo(f"\n{'=' * 60}")
        typer.echo(f"Iteration {i}/{max_iterations}")
        typer.echo(f"{'=' * 60}\n")

        # Run claude
        cmd = ["claude", "--print", "-p", prompt]
        try:
            result = subprocess.run(cmd, check=False)
        except FileNotFoundError:
            typer.echo(
                "Error: 'claude' command not found. Is Claude Code installed?", err=True
            )
            raise typer.Exit(1)

        # Check stop condition
        if stop_file and Path(stop_file).exists():
            typer.echo(f"\nStop file '{stop_file}' detected. Exiting.")
            break

    typer.echo(f"\n{'=' * 60}")
    typer.echo("Loop completed")
    typer.echo(f"{'=' * 60}")


@app.command()
def init() -> None:
    """Initialize a loop configuration (coming soon)."""
    typer.echo("Agent-assisted init coming soon!")
    typer.echo("For now, create PROMPT.md manually and run: ralph-loop run")


if __name__ == "__main__":
    app()
