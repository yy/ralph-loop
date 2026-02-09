"""Tests for planning command execution in runner utilities."""

import subprocess
from unittest.mock import MagicMock, patch

from wiggum.runner import run_claude_for_planning


class TestRunClaudeForPlanning:
    """Tests for run_claude_for_planning error handling."""

    @patch("wiggum.runner.check_cli_available", return_value=True)
    @patch("wiggum.runner.subprocess.run")
    def test_returns_error_on_nonzero_exit(self, mock_run, _mock_check_cli) -> None:
        """Returns actionable error details when Claude exits non-zero."""
        mock_run.return_value = MagicMock(returncode=2, stdout="", stderr="boom")

        output, error = run_claude_for_planning("meta prompt")

        assert output is None
        assert error is not None
        assert "exit code 2" in error
        assert "boom" in error

    @patch("wiggum.runner.check_cli_available", return_value=True)
    @patch("wiggum.runner.subprocess.run")
    def test_returns_stdout_on_success(self, mock_run, _mock_check_cli) -> None:
        """Returns stdout with no error when command succeeds."""
        mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")

        output, error = run_claude_for_planning("meta prompt")

        assert output == "ok"
        assert error is None

    @patch("wiggum.runner.check_cli_available", return_value=True)
    @patch("wiggum.runner.subprocess.run")
    def test_returns_error_on_timeout(self, mock_run, _mock_check_cli) -> None:
        """Returns timeout error details when Claude planning hangs."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=60)

        output, error = run_claude_for_planning("meta prompt", timeout_seconds=60)

        assert output is None
        assert error is not None
        assert "timed out" in error
