# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

wiggum is a Python package for setting up and running "Ralph Wiggum loops" for Claude Code and similar AI agent tools. The package provides:

1. **Setup Assistant**: An interactive helper that guides users through configuring loop parameters including prompts, conditions, and security settings
2. **Loop Runner**: Executes loops with configurable parameters like iteration count (stops when all tasks in TASKS.md are complete)

## Development

This is a Python project. Use `uv` for package management:

```bash
# Install dependencies
uv sync

# Run the package
uv run python -m wiggum

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/test_file.py::test_name -v

# Build (always remove old dist files first)
rm -rf dist && uv build

# Publish
uv publish --token <token>
```

## Architecture

### CLI Commands
- `wiggum init`: Interactive setup that creates `LOOP-PROMPT.md`, `TASKS.md`, and `.wiggum.toml`. Claude analyzes the codebase and suggests both tasks and security constraints. If `TASKS.md` already exists, new tasks are merged (without duplicates) rather than overwriting.
- `wiggum run`: Executes the loop, reading prompt from file and iterating until all tasks in TASKS.md are complete (or max iterations reached). Use `--keep-running` to continue even when tasks are complete (agent can add new tasks). Use `--identify-tasks` to analyze the codebase and populate TASKS.md with refactoring/cleanup tasks without running the loop. Use `--git` to enable git workflow (fetch/merge main, create branch, create PR at end).
- `wiggum add`: Adds tasks to `TASKS.md`
- `wiggum list`: Lists all tasks from `TASKS.md` grouped by status (todo/done)
- `wiggum suggest`: Interactively discovers and suggests tasks using Claude's planning mode. Use `-y`/`--yes` to accept all suggestions without prompting.

### Configuration
Settings are stored in `.wiggum.toml` and read by the `run` command:

**[security] section:**
- `yolo`: Skip all permission prompts
- `allow_paths`: Comma-separated paths to allow writing

**[loop] section:**
- `max_iterations`: Default number of loop iterations (default: 10)
- `agent`: Which agent to use (default: "claude"). Options: claude, codex, gemini

**[git] section:**
- `enabled`: Enable git workflow (default: false)
- `branch_prefix`: Prefix for auto-generated branch names (default: "wiggum")

CLI flags override config file settings.

### Agent Abstraction Layer
The `agents` module provides a pluggable architecture for different coding agents:

- `Agent`: Protocol (interface) that all agents must implement
- `AgentConfig`: Dataclass for passing configuration (prompt, yolo, allow_paths, continue_session)
- `AgentResult`: Dataclass for agent output (stdout, stderr, return_code)
- `get_agent(name)`: Get an agent by name (default: "claude")
- `get_available_agents()`: List registered agents

Agent implementations live in separate files (e.g., `agents_claude.py`, `agents_codex.py`).

**Available agents:**
- `claude`: Claude Code CLI (default)
- `codex`: OpenAI Codex CLI
- `gemini`: Google Gemini CLI
