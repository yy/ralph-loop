"""Upgrade logic for wiggum managed files."""

import re
from pathlib import Path
from typing import Optional


# Config schema - all known config options with defaults
WIGGUM_CONFIG_DEFAULTS = {
    "security": {"yolo": True, "allow_paths": ""},
    "loop": {
        "max_iterations": 10,
        "agent": "claude",
        "keep_running": False,
        "tasks_file": "TASKS.md",
        "prompt_file": "LOOP-PROMPT.md",
    },
    "git": {"enabled": False, "branch_prefix": "wiggum", "auto_pr": False},
    "output": {"verbose": False, "log_file": ""},
    "session": {"continue_session": False},
    "learning": {"enabled": True, "keep_diary": False, "auto_consolidate": True},
}


def extract_template_version(content: str) -> Optional[str]:
    """Extract version from template file.

    Looks for: <!-- wiggum-template: X.Y.Z -->

    Args:
        content: File content to search.

    Returns:
        Version string if found, None otherwise.
    """
    match = re.search(r"<!--\s*wiggum-template:\s*(\d+\.\d+\.\d+)\s*-->", content)
    if match:
        return match.group(1)
    return None


def is_version_outdated(current: Optional[str], target: str) -> bool:
    """Check if current version is older than target.

    Args:
        current: Current version string (or None if no version).
        target: Target version to compare against.

    Returns:
        True if current is older than target or None.
    """
    if current is None:
        return True

    def parse_version(v: str) -> tuple:
        parts = v.split(".")
        return tuple(int(p) for p in parts)

    try:
        return parse_version(current) < parse_version(target)
    except (ValueError, AttributeError):
        return True


def get_missing_config_options(existing: dict) -> list[tuple[str, str, object]]:
    """Detect missing config options.

    Args:
        existing: Existing configuration dict.

    Returns:
        List of (section, key, default_value) tuples for missing options.
    """
    missing = []
    for section, options in WIGGUM_CONFIG_DEFAULTS.items():
        existing_section = existing.get(section, {})
        for key, default in options.items():
            if key not in existing_section:
                missing.append((section, key, default))
    return missing


def merge_config_with_defaults(existing: dict) -> dict:
    """Merge existing config with defaults, preserving user values.

    Args:
        existing: Existing configuration dict.

    Returns:
        Merged configuration with all defaults filled in.
    """
    merged = {}
    for section, options in WIGGUM_CONFIG_DEFAULTS.items():
        existing_section = existing.get(section, {})
        merged[section] = {}
        for key, default in options.items():
            # Preserve existing value, use default if missing
            if key in existing_section:
                merged[section][key] = existing_section[key]
            else:
                merged[section][key] = default
    # Preserve any unknown sections/keys (user extensions)
    for section, options in existing.items():
        if section not in merged:
            merged[section] = options
        elif isinstance(options, dict):
            for key, value in options.items():
                if key not in merged[section]:
                    merged[section][key] = value
    return merged


def tasks_file_needs_upgrade(content: str) -> bool:
    """Check if TODO.md needs structural upgrade.

    Args:
        content: Current TODO.md content.

    Returns:
        True if file is missing required sections.
    """
    required_sections = ["## Todo", "## Done"]
    for section in required_sections:
        if section not in content:
            return True
    return False


def add_missing_task_sections(content: str) -> str:
    """Add missing sections to TODO.md.

    Args:
        content: Current TODO.md content.

    Returns:
        Content with missing sections added.
    """
    lines = content.split("\n")
    has_todo = any("## Todo" in line for line in lines)
    has_done = any("## Done" in line for line in lines)

    # If both exist, return unchanged
    if has_todo and has_done:
        return content

    # Build new content preserving existing structure
    new_lines = []
    inserted_header = False

    for line in lines:
        # Ensure we have the header
        if line.startswith("# ") and not inserted_header:
            new_lines.append(line)
            new_lines.append("")
            if not has_done:
                new_lines.append("## Done")
                new_lines.append("")
            if not has_todo:
                new_lines.append("## Todo")
                new_lines.append("")
            inserted_header = True
        elif line == "## Done" or line == "## Todo":
            new_lines.append(line)
        else:
            new_lines.append(line)

    # If no header was found, add structure at the top
    if not inserted_header:
        result = ["# Tasks", ""]
        if not has_done:
            result.extend(["## Done", ""])
        if not has_todo:
            result.extend(["## Todo", ""])
        result.extend(lines)
        return "\n".join(result)

    return "\n".join(new_lines)


def needs_tasks_rename() -> bool:
    """Check if TASKS.md exists without TODO.md (needs migration)."""
    return Path("TASKS.md").exists() and not Path("TODO.md").exists()


def migrate_tasks_to_todo() -> list[str]:
    """Migrate TASKS.md → TODO.md and clean up related files.

    Returns:
        List of actions taken.
    """
    actions = []
    tasks_path = Path("TASKS.md")
    todo_path = Path("TODO.md")

    if tasks_path.exists() and not todo_path.exists():
        tasks_path.rename(todo_path)
        actions.append("Renamed TASKS.md → TODO.md")

    # Clean up .gitignore: remove /TASKS.md and /DONE.md entries
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        new_content = content
        for entry in ["/TASKS.md\n", "/DONE.md\n"]:
            new_content = new_content.replace(entry, "")
        if new_content != content:
            gitignore_path.write_text(new_content)
            actions.append("Removed /TASKS.md and /DONE.md from .gitignore")

    # Update .wiggum.toml if it has tasks_file = "TASKS.md"
    config_path = Path(".wiggum.toml")
    if config_path.exists():
        config_content = config_path.read_text()
        if 'tasks_file = "TASKS.md"' in config_content:
            new_config = config_content.replace(
                'tasks_file = "TASKS.md"', 'tasks_file = "TODO.md"'
            )
            config_path.write_text(new_config)
            actions.append('Updated .wiggum.toml: tasks_file = "TODO.md"')

    return actions


def get_next_backup_path(path: Path) -> Path:
    """Get the next available backup path.

    Handles numbered backups: .bak, .bak.1, .bak.2, etc.

    Args:
        path: Original file path.

    Returns:
        Path for the backup file.
    """
    backup = path.with_suffix(path.suffix + ".bak")
    if not backup.exists():
        return backup

    # Try numbered backups
    counter = 1
    while True:
        numbered_backup = Path(f"{backup}.{counter}")
        if not numbered_backup.exists():
            return numbered_backup
        counter += 1
