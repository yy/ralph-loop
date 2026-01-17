# Git Safety Feature

## Overview

Wiggum should protect users from losing work by automatically using git branches and requiring a clean working directory before running loops.

## Behavior

### When user runs `wiggum run`:

```
Is this a git repo?
├── NO → Warn: "Not a git repo. Changes cannot be undone. Continue? [y/N]"
│        └── User declines → Exit
│        └── User accepts → Run loop (no safety net)
│
└── YES → Check working directory status
          │
          ├── CLEAN → Create branch, run loop
          │
          └── DIRTY → Ask user:
                      "You have uncommitted changes. What would you like to do?"
                      [S]tash - Stash changes and continue
                      [C]ommit - Commit changes with a message
                      [A]bort - Exit without running

                      └── After handling → Create branch, run loop
```

### Branch creation:

- Branch name format: `wiggum/<timestamp>` (e.g., `wiggum/2026-01-17-143022`)
- Configurable prefix via `--branch-prefix` or `[git] branch_prefix` in config
- Branch is created from current HEAD (after stash/commit if needed)

### After loop completes:

- Stay on the wiggum branch
- Show summary: "Changes are on branch `wiggum/2026-01-17-143022`"
- Suggest next steps:
  - "To create a PR: `wiggum pr` or `gh pr create`"
  - "To merge to main: `git checkout main && git merge wiggum/...`"
  - "To discard: `git checkout main && git branch -D wiggum/...`"

### Flags:

| Flag | Behavior |
|------|----------|
| `--pr` | Create PR after loop completes (replaces current `--git`) |
| `--no-branch` | Skip branch creation (run on current branch, still require clean dir) |
| `--force` | Skip all safety checks (for experienced users) |

### Config (`.wiggum.toml`):

```toml
[git]
branch_prefix = "wiggum"  # Branch name prefix
auto_pr = false           # Auto-create PR after loop (like --pr)
require_clean = true      # Require clean working dir (default: true)
```

## Edge Cases

1. **User is already on a wiggum branch**: Continue on that branch (don't create nested branch)
2. **User has staged but uncommitted changes**: Treat as dirty
3. **Stash fails** (e.g., conflicts): Show error, suggest manual resolution
4. **Branch name already exists**: Append counter (e.g., `wiggum/2026-01-17-143022-2`)
5. **No remote configured**: Skip PR creation, just stay on branch

## Migration

- Deprecate `--git` flag (show warning, map to `--pr`)
- Default behavior changes: loops now always create branches in git repos

## Out of Scope

- Auto-merging branches
- Conflict resolution
- Multi-repo support
