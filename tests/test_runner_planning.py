"""Tests for planning command execution in runner utilities."""

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
