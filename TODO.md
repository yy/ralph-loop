# Tasks

## Todo

- [ ] Validate spec file references in tasks — warn when a task references a non-existent spec
- [ ] Handle branch name collisions in `generate_branch_name()` by checking existence and appending a counter
- [ ] Split `cli.py` (1400+ lines) into per-command modules under a `commands/` package

## Done
- [x] create docs directory and document important information about the project as a knowledge base / context for future coding agent sessions
- [x] Add a docstring to the `spec` command in cli.py explaining what it does
- [x] Extract allow_paths handling logic - SKIPPED: Over-engineering. Each agent uses paths differently (Claude: Edit/Write permissions, Codex: --add-dir, Gemini: raw string). Only 2 lines are common between Claude/Codex. Three similar lines is better than a premature abstraction.
- [x] Add validation for external dependencies (claude, codex, gemini, gh CLIs) before attempting to use them, with helpful error messages
- [x] Implement git safety feature (see specs/git-safety.md)
- [x] Add PRD/spec workflow support (see specs/prd-workflow.md)
- [x] git-ignoring wiggum files when init
- [ ] **Test the `spec` command** - It's the only command with zero test coverage. Tests for creation, overwrite protection, `--force`, placeholder substitution, and directory creation.
- [ ] **Add `wiggum specs` list command** - The `prd-workflow.md` spec calls for this but it was never implemented. Lists spec files and shows which tasks reference them.
- [ ] **Unit tests for `runner.py`** - The retry logic, planning failures, and file change parsing have no dedicated tests (only indirect coverage through integration tests).
- [ ] **Split cli.py into subcommand modules** - At 1,545 lines it's the largest file by far. Breaking it into `cli_run.py`, `cli_init.py`, etc. improves maintainability.
- [x] **`--timeout` flag for `wiggum run`** - Added timeout propagation to agent subprocess calls, plus timeout handling for git/planning subprocesses.
