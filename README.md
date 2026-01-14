# ralph-loop

A Ralph Wiggum loop is the simplest possible agent loop:

```bash
while true; do cat PROMPT.md | claude --print; done
```

This package helps you set up and run these loops with proper guardrails.

## Why ralph-loop?

The raw loop above works, but you probably want:

- **Iteration limits** - stop after N runs
- **Stop conditions** - exit when a goal is reached
- **Session management** - continue or reset context between runs
- **Security settings** - control what the agent can do
- **Logging** - track what happened across iterations

ralph-loop provides an interactive setup assistant to configure these parameters, and a loop runner to execute with your settings.

## Installation

```bash
uv add ralph-loop
```

## Usage

```bash
# Interactive setup - creates a loop configuration
ralph-loop init

# Run a configured loop
ralph-loop run

# Run with overrides
ralph-loop run --max-iterations 10 --prompt "Review and improve this codebase"
```

## Configuration

ralph-loop stores configuration in `.ralph-loop.toml`:

```toml
[loop]
max_iterations = 10
prompt_file = "PROMPT.md"

[stop]
condition = "file_exists"
target = "DONE.md"

[security]
allow_write = true
allow_bash = false
```

## License

MIT
