"""Tests for the learning diary feature."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from wiggum.learning import (
    clear_diary,
    consolidate_learnings,
    ensure_diary_dir,
    has_diary_content,
    read_diary,
)


@pytest.fixture(autouse=True)
def restore_cwd():
    """Restore working directory after each test."""
    original_cwd = os.getcwd()
    yield
    os.chdir(original_cwd)


class TestEnsureDiaryDir:
    """Tests for ensure_diary_dir function."""

    def test_creates_diary_directory(self, tmp_path: Path) -> None:
        """Creates .wiggum/ directory if it doesn't exist."""
        ensure_diary_dir(base_path=tmp_path)

        assert (tmp_path / ".wiggum").exists()
        assert (tmp_path / ".wiggum").is_dir()

    def test_does_not_fail_if_directory_exists(self, tmp_path: Path) -> None:
        """Does not raise error if directory already exists."""
        (tmp_path / ".wiggum").mkdir()

        ensure_diary_dir(base_path=tmp_path)  # Should not raise

        assert (tmp_path / ".wiggum").exists()

    def test_raises_error_if_symlink(self, tmp_path: Path) -> None:
        """Raises RuntimeError if .wiggum is a symlink."""
        target = tmp_path / "other_dir"
        target.mkdir()
        (tmp_path / ".wiggum").symlink_to(target)

        with pytest.raises(RuntimeError, match="symlink"):
            ensure_diary_dir(base_path=tmp_path)


class TestHasDiaryContent:
    """Tests for has_diary_content function."""

    def test_returns_false_when_no_diary_file(self, tmp_path: Path) -> None:
        """Returns False when diary file doesn't exist."""
        assert has_diary_content(base_path=tmp_path) is False

    def test_returns_false_when_diary_is_empty(self, tmp_path: Path) -> None:
        """Returns False when diary file is empty."""
        (tmp_path / ".wiggum").mkdir()
        (tmp_path / ".wiggum" / "session-diary.md").write_text("")

        assert has_diary_content(base_path=tmp_path) is False

    def test_returns_false_when_diary_is_whitespace_only(self, tmp_path: Path) -> None:
        """Returns False when diary file contains only whitespace."""
        (tmp_path / ".wiggum").mkdir()
        (tmp_path / ".wiggum" / "session-diary.md").write_text("   \n\n  ")

        assert has_diary_content(base_path=tmp_path) is False

    def test_returns_true_when_diary_has_content(self, tmp_path: Path) -> None:
        """Returns True when diary file has actual content."""
        (tmp_path / ".wiggum").mkdir()
        (tmp_path / ".wiggum" / "session-diary.md").write_text(
            "### Learning: Test\n**Context**: Test context"
        )

        assert has_diary_content(base_path=tmp_path) is True

    def test_returns_false_on_read_error(self, tmp_path: Path) -> None:
        """Returns False when diary file cannot be read."""
        (tmp_path / ".wiggum").mkdir()
        diary_file = tmp_path / ".wiggum" / "session-diary.md"
        diary_file.write_text("content")
        # Make file unreadable
        diary_file.chmod(0o000)
        try:
            assert has_diary_content(base_path=tmp_path) is False
        finally:
            # Restore permissions for cleanup
            diary_file.chmod(0o644)


class TestReadDiary:
    """Tests for read_diary function."""

    def test_returns_empty_string_when_no_diary(self, tmp_path: Path) -> None:
        """Returns empty string when diary file doesn't exist."""
        assert read_diary(base_path=tmp_path) == ""

    def test_returns_diary_content(self, tmp_path: Path) -> None:
        """Returns the content of the diary file."""
        (tmp_path / ".wiggum").mkdir()
        content = "### Learning: Test\n**Context**: Test context"
        (tmp_path / ".wiggum" / "session-diary.md").write_text(content)

        assert read_diary(base_path=tmp_path) == content

    def test_returns_empty_string_on_read_error(self, tmp_path: Path) -> None:
        """Returns empty string when diary file cannot be read."""
        (tmp_path / ".wiggum").mkdir()
        diary_file = tmp_path / ".wiggum" / "session-diary.md"
        diary_file.write_text("content")
        # Make file unreadable
        diary_file.chmod(0o000)
        try:
            assert read_diary(base_path=tmp_path) == ""
        finally:
            # Restore permissions for cleanup
            diary_file.chmod(0o644)


class TestClearDiary:
    """Tests for clear_diary function."""

    def test_deletes_diary_file(self, tmp_path: Path) -> None:
        """Deletes the diary file when it exists."""
        (tmp_path / ".wiggum").mkdir()
        diary_file = tmp_path / ".wiggum" / "session-diary.md"
        diary_file.write_text("some content")

        clear_diary(base_path=tmp_path)

        assert not diary_file.exists()

    def test_does_not_fail_when_no_diary(self, tmp_path: Path) -> None:
        """Does not raise error when diary file doesn't exist."""
        clear_diary(base_path=tmp_path)  # Should not raise


class TestSanitizeForPrompt:
    """Tests for sanitize_for_prompt function."""

    def test_wraps_content_with_delimiters(self) -> None:
        """Wraps content in labeled delimiters."""
        from wiggum.learning import sanitize_for_prompt

        result = sanitize_for_prompt("some content", "test-label")

        assert "<test-label>" in result
        assert "</test-label>" in result
        assert "some content" in result
        assert "=" * 40 in result

    def test_preserves_content_exactly(self) -> None:
        """Preserves content without modification."""
        from wiggum.learning import sanitize_for_prompt

        content = "### Learning\n**Context**: Test\n```python\ncode```"
        result = sanitize_for_prompt(content, "label")

        assert content in result


class TestConsolidateLearnings:
    """Tests for consolidate_learnings function."""

    def test_returns_failure_with_reason_when_no_diary_content(
        self, tmp_path: Path
    ) -> None:
        """Returns (False, reason) when diary has no content."""
        os.chdir(tmp_path)

        success, reason = consolidate_learnings(agent_name=None, yolo=True)

        assert success is False
        assert reason == "no diary content"

    def test_calls_agent_with_correct_prompt(self, tmp_path: Path) -> None:
        """Calls agent with diary content and CLAUDE.md content."""
        os.chdir(tmp_path)
        # Set up diary
        (tmp_path / ".wiggum").mkdir()
        diary_content = "### Learning: Test\n**Context**: Test"
        (tmp_path / ".wiggum" / "session-diary.md").write_text(diary_content)
        # Set up CLAUDE.md
        claude_md_content = "# Project\n\nExisting content"
        (tmp_path / "CLAUDE.md").write_text(claude_md_content)

        mock_agent = MagicMock()
        mock_agent.run.return_value = MagicMock(return_code=0)

        with patch("wiggum.learning.get_agent", return_value=mock_agent):
            with patch(
                "wiggum.learning.resolve_templates_dir",
                return_value=Path(__file__).parent.parent
                / "src"
                / "wiggum"
                / "templates",
            ):
                success, reason = consolidate_learnings(agent_name="claude", yolo=True)

        assert success is True
        assert reason is None
        mock_agent.run.assert_called_once()
        config = mock_agent.run.call_args[0][0]
        assert diary_content in config.prompt
        assert claude_md_content in config.prompt
        assert config.yolo is True

    def test_prompt_uses_delimiters_for_injection_protection(
        self, tmp_path: Path
    ) -> None:
        """Prompt wraps content in delimiters to prevent prompt injection."""
        os.chdir(tmp_path)
        (tmp_path / ".wiggum").mkdir()
        (tmp_path / ".wiggum" / "session-diary.md").write_text("diary content")
        (tmp_path / "CLAUDE.md").write_text("claude content")

        mock_agent = MagicMock()
        mock_agent.run.return_value = MagicMock(return_code=0)

        with patch("wiggum.learning.get_agent", return_value=mock_agent):
            with patch(
                "wiggum.learning.resolve_templates_dir",
                return_value=Path(__file__).parent.parent
                / "src"
                / "wiggum"
                / "templates",
            ):
                consolidate_learnings(agent_name="claude", yolo=True)

        config = mock_agent.run.call_args[0][0]
        # Should have delimiters around content
        assert "<diary-content>" in config.prompt
        assert "</diary-content>" in config.prompt
        assert "<claude-md-content>" in config.prompt
        assert "</claude-md-content>" in config.prompt
        # Should have line delimiters
        assert "=" * 40 in config.prompt

    def test_returns_failure_with_reason_on_agent_failure(self, tmp_path: Path) -> None:
        """Returns (False, reason) when agent returns non-zero exit code."""
        os.chdir(tmp_path)
        (tmp_path / ".wiggum").mkdir()
        (tmp_path / ".wiggum" / "session-diary.md").write_text("some content")

        mock_agent = MagicMock()
        mock_agent.run.return_value = MagicMock(return_code=1)

        with patch("wiggum.learning.get_agent", return_value=mock_agent):
            with patch(
                "wiggum.learning.resolve_templates_dir",
                return_value=Path(__file__).parent.parent
                / "src"
                / "wiggum"
                / "templates",
            ):
                success, reason = consolidate_learnings(agent_name="claude", yolo=True)

        assert success is False
        assert reason == "agent failed with exit code 1"

    def test_returns_failure_with_reason_when_template_missing(
        self, tmp_path: Path
    ) -> None:
        """Returns (False, reason) when CONSOLIDATE-PROMPT.md template is missing."""
        os.chdir(tmp_path)
        (tmp_path / ".wiggum").mkdir()
        (tmp_path / ".wiggum" / "session-diary.md").write_text("some content")

        # Use a directory without the template
        empty_templates = tmp_path / "templates"
        empty_templates.mkdir()

        with patch(
            "wiggum.learning.resolve_templates_dir", return_value=empty_templates
        ):
            success, reason = consolidate_learnings(agent_name="claude", yolo=True)

        assert success is False
        assert reason == "consolidation template not found"

    def test_handles_missing_claude_md(self, tmp_path: Path) -> None:
        """Works when CLAUDE.md doesn't exist."""
        os.chdir(tmp_path)
        (tmp_path / ".wiggum").mkdir()
        (tmp_path / ".wiggum" / "session-diary.md").write_text("diary content")

        mock_agent = MagicMock()
        mock_agent.run.return_value = MagicMock(return_code=0)

        with patch("wiggum.learning.get_agent", return_value=mock_agent):
            with patch(
                "wiggum.learning.resolve_templates_dir",
                return_value=Path(__file__).parent.parent
                / "src"
                / "wiggum"
                / "templates",
            ):
                success, reason = consolidate_learnings(agent_name="claude", yolo=True)

        assert success is True
        assert reason is None
        config = mock_agent.run.call_args[0][0]
        assert "(No CLAUDE.md exists)" in config.prompt


class TestLearningConfigResolution:
    """Tests for learning config resolution in resolve_run_config."""

    def _base_config_args(self) -> dict:
        """Return base arguments for resolve_run_config."""
        return {
            "yolo": False,
            "allow_paths": None,
            "max_iterations": None,
            "tasks_file": None,
            "prompt_file": None,
            "agent": None,
            "log_file": None,
            "show_progress": False,
            "continue_session": False,
            "reset_session": False,
            "keep_running": False,
            "stop_when_done": False,
            "create_pr": False,
            "no_branch": False,
            "force": False,
            "branch_prefix": None,
            "diary": False,
            "no_diary": False,
            "no_consolidate": False,
            "keep_diary_flag": False,
            "no_keep_diary": False,
        }

    def test_diary_and_no_diary_mutually_exclusive(self, tmp_path: Path) -> None:
        """Cannot use --diary and --no-diary together."""
        from wiggum.config import resolve_run_config

        os.chdir(tmp_path)
        args = self._base_config_args()
        args["diary"] = True
        args["no_diary"] = True

        with pytest.raises(ValueError, match="mutually exclusive"):
            resolve_run_config(**args)

    def test_keep_diary_and_no_keep_diary_mutually_exclusive(
        self, tmp_path: Path
    ) -> None:
        """Cannot use --keep-diary and --no-keep-diary together."""
        from wiggum.config import resolve_run_config

        os.chdir(tmp_path)
        args = self._base_config_args()
        args["keep_diary_flag"] = True
        args["no_keep_diary"] = True

        with pytest.raises(ValueError, match="mutually exclusive"):
            resolve_run_config(**args)

    def test_diary_flag_enables_learning(self, tmp_path: Path) -> None:
        """--diary flag enables learning even when config disables it."""
        from wiggum.config import resolve_run_config, write_config

        os.chdir(tmp_path)
        write_config({"learning": {"enabled": False}})
        args = self._base_config_args()
        args["diary"] = True

        cfg = resolve_run_config(**args)

        assert cfg.learning_enabled is True

    def test_no_diary_flag_disables_learning(self, tmp_path: Path) -> None:
        """--no-diary flag disables learning."""
        from wiggum.config import resolve_run_config

        os.chdir(tmp_path)
        args = self._base_config_args()
        args["no_diary"] = True

        cfg = resolve_run_config(**args)

        assert cfg.learning_enabled is False

    def test_keep_diary_flag_overrides_config(self, tmp_path: Path) -> None:
        """--keep-diary flag overrides config setting."""
        from wiggum.config import resolve_run_config, write_config

        os.chdir(tmp_path)
        write_config({"learning": {"keep_diary": False}})
        args = self._base_config_args()
        args["keep_diary_flag"] = True

        cfg = resolve_run_config(**args)

        assert cfg.keep_diary is True

    def test_no_keep_diary_flag_overrides_config(self, tmp_path: Path) -> None:
        """--no-keep-diary flag overrides config setting."""
        from wiggum.config import resolve_run_config

        os.chdir(tmp_path)
        args = self._base_config_args()
        args["no_keep_diary"] = True

        cfg = resolve_run_config(**args)

        assert cfg.keep_diary is False

    def test_learning_defaults_enabled(self, tmp_path: Path) -> None:
        """Learning is enabled by default, but keep_diary is False."""
        from wiggum.config import resolve_run_config

        os.chdir(tmp_path)
        args = self._base_config_args()

        cfg = resolve_run_config(**args)

        assert cfg.learning_enabled is True
        assert cfg.keep_diary is False  # Default false to reduce information leakage
        assert cfg.auto_consolidate is True


class TestGetDiaryLineCount:
    """Tests for get_diary_line_count function."""

    def test_returns_zero_when_no_diary(self, tmp_path: Path) -> None:
        """Returns 0 when diary file doesn't exist."""
        from wiggum.learning import get_diary_line_count

        assert get_diary_line_count(base_path=tmp_path) == 0

    def test_returns_line_count(self, tmp_path: Path) -> None:
        """Returns the number of lines in the diary."""
        from wiggum.learning import get_diary_line_count

        (tmp_path / ".wiggum").mkdir()
        (tmp_path / ".wiggum" / "session-diary.md").write_text("line 1\nline 2\nline 3")

        assert get_diary_line_count(base_path=tmp_path) == 3
