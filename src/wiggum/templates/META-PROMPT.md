You are helping set up wiggum (an agent loop that iterates on tasks until done).

## Context

{{goal}}

## Your Task

Analyze this codebase and suggest concrete, actionable tasks.
Also suggest appropriate security constraints based on the project's needs.

## Output Format

Output ONLY a markdown block. No other text.

```markdown
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
- Break work into 3-7 concrete tasks
- Each task should be completable in one agent session
- Order by priority (most important first)
- Tasks should have clear done criteria
- Don't include vague tasks like "improve code quality"
- Do NOT suggest tasks that are already completed
- Build on existing work - suggest tasks that logically follow from what's done

### Testing guidance for tasks
- Tasks involving new behavior, logic, APIs, or bug fixes need tests (test-first)
- Tasks involving string changes, renames, config tweaks do NOT need tests
- Never write tests that just check string presence or file existence

### Constraints
- **conservative**: Agent asks permission for each action. Use when unsure.
- **path_restricted**: Allow writes to specific paths only (e.g., src/,tests/).
- **yolo**: Skip all permission prompts. Only for trusted projects.

For `internet_access`:
- `true` if tasks require web fetching, API calls, or package installation
- `false` for offline-only projects
