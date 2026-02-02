# Learning Diary Security Hardening

## Problem

The learning diary feature has prompt injection vulnerabilities. Diary content and CLAUDE.md content are injected directly into the consolidation prompt without sanitization, allowing malicious content to manipulate agent behavior.

## Attack Vectors

1. **Diary injection**: Attacker modifies `.wiggum/session-diary.md` with prompt override instructions
2. **CLAUDE.md injection**: Malicious CLAUDE.md content affects consolidation
3. **Symlink attack**: `.wiggum` created as symlink to write/delete files elsewhere

## Proposed Mitigations

### 1. Content Delimiters (Required)

Wrap injected content in clear delimiters that signal "this is data, not instructions":

```python
def sanitize_for_prompt(content: str, label: str) -> str:
    """Wrap content in delimiters to prevent prompt injection."""
    delimiter = "=" * 40
    return f"""
<{label}>
{delimiter}
{content}
{delimiter}
</{label}>
"""
```

Update `consolidate_learnings()`:
```python
prompt = prompt_template.replace(
    "{diary_content}",
    sanitize_for_prompt(diary_content, "diary-content")
)
```

### 2. Confirmation Before Consolidation (Required)

Add confirmation unless `--force` or `yolo` is set:

```python
if cfg.auto_consolidate and has_diary_content():
    if not cfg.yolo:
        typer.echo(f"\nDiary has {line_count} lines to consolidate into CLAUDE.md")
        if not typer.confirm("Proceed?", default=True):
            typer.echo("Skipped consolidation. Diary preserved.")
            return
```

### 3. Symlink Protection (Required)

Check for symlinks before diary operations:

```python
def ensure_diary_dir() -> None:
    """Create .wiggum/ directory if needed."""
    if DIARY_DIR.exists() and DIARY_DIR.is_symlink():
        raise RuntimeError(f"{DIARY_DIR} is a symlink - refusing for security")
    DIARY_DIR.mkdir(exist_ok=True)
```

### 4. Add .wiggum to .gitignore (Recommended)

During `wiggum init`, append to `.gitignore` if not present:

```python
gitignore = Path(".gitignore")
if gitignore.exists():
    content = gitignore.read_text()
    if ".wiggum/" not in content:
        gitignore.write_text(content.rstrip() + "\n.wiggum/\n")
```

### 5. Default keep_diary to False (Recommended)

Change default to reduce information leakage:

```python
"keep_diary": (False, bool),  # was True
```

## Implementation Order

1. Content delimiters (blocks injection)
2. Symlink protection (blocks file attacks)
3. Confirmation prompt (user awareness)
4. .gitignore addition (prevents accidental commits)
5. Default change (reduces exposure)

## Testing

- Test that delimiters are added to prompt
- Test symlink detection raises error
- Test confirmation appears when not yolo
- Test .gitignore is updated during init
