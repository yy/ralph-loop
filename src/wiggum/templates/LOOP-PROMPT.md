## Principle

**Aim for simplicity.** The best code is code that doesn't exist. Before adding anything, ask: is this necessary? After implementing, ask: what can be removed?

## Workflow

1. Read TASKS.md to see the current task list
2. Choose the most important task
3. **Decide if this task needs tests**:
   - YES: New behavior, logic, APIs, bug fixes - write tests first, then implement
   - NO: String changes, renames, config tweaks - just implement and verify
4. Implement the task (test-first if tests are needed)
5. Run tests to verify nothing broke
6. **Simplify**: Review the code you touched and ask:
   - What can be removed? (dead code, unused imports, unnecessary features)
   - Is this over-engineered? (remove abstractions that aren't pulling their weight)
   - Are there silly tests? (e.g., tests that just check string presence)
   - Can this be simpler? (inline single-use functions, flatten unnecessary nesting)
   - Run tests again after simplifying
7. **Update docs**: Ensure documentation ({{doc_files}}) matches the implementation
8. Update TASKS.md: mark task as `[x]` and move it to the `## Done` section

## When tests are NOT needed

Don't write tests for:
- String/message/label changes
- Renames or config changes
- Anything where the "test" would just check that a string exists

If you can't describe what behavior would regress without the test, you don't need a test.

## Rules

- Only work on ONE task per session
- If blocked, update TASKS.md and work on the blocker first
- When in doubt, delete it
