# Tasks

## Todo

## Done
- [x] create docs directory and document important information about the project as a knowledge base / context for future coding agent sessions
- [x] Add a docstring to the `spec` command in cli.py explaining what it does
- [x] Extract allow_paths handling logic - SKIPPED: Over-engineering. Each agent uses paths differently (Claude: Edit/Write permissions, Codex: --add-dir, Gemini: raw string). Only 2 lines are common between Claude/Codex. Three similar lines is better than a premature abstraction.
- [x] Add validation for external dependencies (claude, codex, gemini, gh CLIs) before attempting to use them, with helpful error messages
- [x] Implement git safety feature (see specs/git-safety.md)
- [x] Add PRD/spec workflow support (see specs/prd-workflow.md)
- [x] git-ignoring wiggum files when init
