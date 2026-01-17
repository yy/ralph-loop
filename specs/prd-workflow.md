# PRD Integration in Wiggum

## Problem

Simple tasks work well with TASKS.md, but complex features need:
- Detailed requirements
- Edge cases
- Acceptance criteria
- Design decisions

Currently there's no standard way to provide this context to the agent.

## Proposal

### Directory Structure

```
project/
├── TASKS.md           # Task list (simple descriptions)
├── LOOP-PROMPT.md     # Agent instructions
├── specs/             # Detailed specs for complex tasks
│   ├── feature-a.md
│   └── feature-b.md
└── .wiggum.toml
```

### Task Format Extension

Tasks can reference specs:

```markdown
## Todo

- [ ] Add git safety feature (see specs/git-safety.md)
- [ ] Simple rename  <!-- no spec needed -->
```

### LOOP-PROMPT.md Addition

Add to workflow:

```markdown
## Workflow

1. Read TASKS.md to see the current task list
2. Choose the most important task
3. **If task references a spec file, read it first**
4. ...
```

### Spec File Format

Simple markdown with sections:

```markdown
# Feature Name

## Overview
Brief description

## Behavior
Detailed behavior, flowcharts, examples

## Edge Cases
List of edge cases and how to handle them

## Out of Scope
What this feature does NOT do
```

### Commands

```bash
# Create a new spec from template
wiggum spec <name>

# List specs and their linked tasks
wiggum specs
```

## Alternative Considered

**Inline specs in TASKS.md**: Rejected because:
- Makes TASKS.md unwieldy
- Hard to version/review specs separately
- No clear ownership per feature

## Implementation

1. Update LOOP-PROMPT.md template to mention specs
2. Add `wiggum spec` command to create spec from template
3. Add spec template to templates/
4. Document in CLAUDE.md
