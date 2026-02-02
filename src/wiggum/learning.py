"""Learning diary operations for wiggum sessions."""

from pathlib import Path
from typing import Optional

from wiggum.agents import AgentConfig, get_agent
from wiggum.config import resolve_templates_dir

DEFAULT_DIARY_DIR = Path(".wiggum")
DEFAULT_DIARY_FILENAME = "session-diary.md"


def _get_diary_dir(base_path: Optional[Path] = None) -> Path:
    """Get the diary directory path."""
    return DEFAULT_DIARY_DIR if base_path is None else base_path / ".wiggum"


def _get_diary_path(base_path: Optional[Path] = None) -> Path:
    """Get the diary file path."""
    return _get_diary_dir(base_path) / DEFAULT_DIARY_FILENAME


def sanitize_for_prompt(content: str, label: str) -> str:
    """Wrap content in delimiters to prevent prompt injection.

    This wraps user content in clearly labeled delimiters that signal
    to the LLM that the enclosed text is data, not instructions.

    Args:
        content: The content to wrap.
        label: A label identifying the content (e.g., "diary-content").

    Returns:
        The content wrapped in labeled delimiters.
    """
    delimiter = "=" * 40
    return f"""
<{label}>
{delimiter}
{content}
{delimiter}
</{label}>
"""


def ensure_diary_dir(base_path: Optional[Path] = None) -> None:
    """Create .wiggum/ directory if needed. Raises RuntimeError if symlink."""
    diary_dir = _get_diary_dir(base_path)
    if diary_dir.is_symlink():
        raise RuntimeError(f"{diary_dir} is a symlink - refusing for security")
    diary_dir.mkdir(exist_ok=True)


def has_diary_content(base_path: Optional[Path] = None) -> bool:
    """Check if diary exists and has content beyond whitespace."""
    diary_path = _get_diary_path(base_path)
    if not diary_path.exists():
        return False
    try:
        return bool(diary_path.read_text().strip())
    except OSError:
        return False


def read_diary(base_path: Optional[Path] = None) -> str:
    """Read diary content, or empty string if no diary exists."""
    diary_path = _get_diary_path(base_path)
    if not diary_path.exists():
        return ""
    try:
        return diary_path.read_text()
    except OSError:
        return ""


def get_diary_line_count(base_path: Optional[Path] = None) -> int:
    """Get the number of lines in the diary file, or 0 if no diary exists."""
    content = read_diary(base_path)
    return len(content.splitlines()) if content else 0


def clear_diary(base_path: Optional[Path] = None) -> None:
    """Delete diary file if it exists."""
    diary_path = _get_diary_path(base_path)
    if diary_path.exists():
        diary_path.unlink()


def consolidate_learnings(
    agent_name: Optional[str], yolo: bool, base_path: Optional[Path] = None
) -> tuple[bool, Optional[str]]:
    """Run agent to consolidate diary into CLAUDE.md.

    Returns (True, None) on success, or (False, reason) on failure.
    """
    if not has_diary_content(base_path):
        return False, "no diary content"

    diary_content = read_diary(base_path)
    claude_md_path = Path("CLAUDE.md") if base_path is None else base_path / "CLAUDE.md"
    claude_md_content = claude_md_path.read_text() if claude_md_path.exists() else ""

    # Read consolidation prompt template
    templates_dir = resolve_templates_dir()
    consolidate_template_path = templates_dir / "CONSOLIDATE-PROMPT.md"

    if not consolidate_template_path.exists():
        return False, "consolidation template not found"

    # Build the consolidation prompt with sanitized content
    prompt_template = consolidate_template_path.read_text()
    prompt = prompt_template.replace(
        "{diary_content}", sanitize_for_prompt(diary_content, "diary-content")
    )
    prompt = prompt.replace(
        "{claude_md_content}",
        sanitize_for_prompt(
            claude_md_content or "(No CLAUDE.md exists)", "claude-md-content"
        ),
    )

    # Run the agent
    agent = get_agent(agent_name)
    agent_config = AgentConfig(
        prompt=prompt,
        yolo=yolo,
        allow_paths=None,
        continue_session=False,
    )

    result = agent.run(agent_config)
    if result.return_code == 0:
        return True, None
    return False, f"agent failed with exit code {result.return_code}"
