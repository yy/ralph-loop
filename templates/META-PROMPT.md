You are helping set up a ralph-loop (an agent loop that iterates on tasks until done).

## User's Goal

{{goal}}

## Your Task

Analyze this codebase and break down the user's goal into concrete, actionable tasks.
Also suggest appropriate security constraints based on the project's needs.

## Output Format

Output ONLY a markdown block. No other text.

```markdown
## Goal

One line summary of the goal

## Tasks

- [ ] First task description
- [ ] Second task description
- [ ] Third task description

## Constraints

security_mode: <conservative|path_restricted|yolo>
allow_paths: <comma-separated paths if path_restricted, empty otherwise>
internet_access: <true|false>
```

{{existing_tasks}}

## Guidelines

### Tasks
- Break the goal into 3-7 concrete tasks
- Each task should be completable in one agent session
- Order by priority (most important first)
- Tasks should be testable (have clear done criteria)
- Consider what already exists in the codebase
- Don't include vague tasks like "improve code quality"
- Do NOT suggest tasks that are already completed or in progress
- Build on existing work - suggest tasks that logically follow from what's done

### Constraints
Choose security constraints based on the project:
- **conservative**: Safest option - Claude will ask permission for each action. Use for sensitive projects or when unsure.
- **path_restricted**: Allow writes to specific paths only (e.g., src/,tests/). Good balance of safety and convenience.
- **yolo**: Skip all permission prompts. Only for trusted projects in isolated environments.

For `internet_access`:
- Set to `true` if tasks require web fetching, API calls, or package installation
- Set to `false` for offline-only projects
