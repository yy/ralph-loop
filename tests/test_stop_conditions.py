"""Tests for stop conditions in ralph-loop."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from ralph_loop.cli import app, file_exists_check, tasks_remaining

runner = CliRunner()


class TestFileExistsCheck:
    """Tests for the file_exists stop condition."""

    def test_file_exists_check_returns_true_when_file_exists(
        self, tmp_path: Path
    ) -> None:
        """When the target file exists, file_exists_check returns True."""
        stop_file = tmp_path / "DONE.md"
        stop_file.write_text("done")
        assert file_exists_check(stop_file) is True

    def test_file_exists_check_returns_false_when_file_missing(
        self, tmp_path: Path
    ) -> None:
        """When the target file doesn't exist, file_exists_check returns False."""
        stop_file = tmp_path / "DONE.md"
        assert file_exists_check(stop_file) is False

    def test_file_exists_check_returns_false_for_none(self) -> None:
        """When no stop file is specified (None), file_exists_check returns False."""
        assert file_exists_check(None) is False


class TestRunWithFileExistsStopCondition:
    """Integration tests for the run command with file_exists stop condition."""

    def test_run_exits_immediately_when_stop_file_exists(self, tmp_path: Path) -> None:
        """The loop exits without running if the stop file already exists."""
        # Setup
        prompt_file = tmp_path / "LOOP-PROMPT.md"
        prompt_file.write_text("test prompt")
        stop_file = tmp_path / "DONE.md"
        stop_file.write_text("done")
        tasks_file = tmp_path / "TASKS.md"
        tasks_file.write_text("# Tasks\n\n## Todo\n\n- [ ] task1\n")

        with patch("ralph_loop.cli.subprocess.run") as mock_run:
            result = runner.invoke(
                app,
                [
                    "run",
                    "-f",
                    str(prompt_file),
                    "--tasks",
                    str(tasks_file),
                    "--stop-file",
                    str(stop_file),
                    "-n",
                    "5",
                ],
            )

        # Claude should never be called because stop file exists
        mock_run.assert_not_called()
        assert "Stop file" in result.output
        assert result.exit_code == 0

    def test_run_stops_when_stop_file_created_during_loop(self, tmp_path: Path) -> None:
        """The loop stops after an iteration if the stop file is created."""
        # Setup
        prompt_file = tmp_path / "LOOP-PROMPT.md"
        prompt_file.write_text("test prompt")
        stop_file = tmp_path / "DONE.md"
        tasks_file = tmp_path / "TASKS.md"
        tasks_file.write_text("# Tasks\n\n## Todo\n\n- [ ] task1\n")

        call_count = 0

        def mock_subprocess_run(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            # Create the stop file on first call
            if call_count == 1:
                stop_file.write_text("done")
            return MagicMock(returncode=0)

        with patch("ralph_loop.cli.subprocess.run", side_effect=mock_subprocess_run):
            result = runner.invoke(
                app,
                [
                    "run",
                    "-f",
                    str(prompt_file),
                    "--tasks",
                    str(tasks_file),
                    "--stop-file",
                    str(stop_file),
                    "-n",
                    "5",
                ],
            )

        # Claude should be called exactly once
        assert call_count == 1
        assert "Stop file" in result.output
        assert result.exit_code == 0

    def test_run_without_stop_file_continues_normally(self, tmp_path: Path) -> None:
        """Without --stop-file, the loop doesn't check for file existence."""
        prompt_file = tmp_path / "LOOP-PROMPT.md"
        prompt_file.write_text("test prompt")
        tasks_file = tmp_path / "TASKS.md"
        # Start with tasks, then mark them done after first iteration
        tasks_file.write_text("# Tasks\n\n## Todo\n\n- [ ] task1\n")

        call_count = 0

        def mock_subprocess_run(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            # Mark tasks complete after first iteration
            if call_count == 1:
                tasks_file.write_text("# Tasks\n\n## Todo\n\n## Done\n\n- [x] task1\n")
            return MagicMock(returncode=0)

        with patch("ralph_loop.cli.subprocess.run", side_effect=mock_subprocess_run):
            result = runner.invoke(
                app,
                [
                    "run",
                    "-f",
                    str(prompt_file),
                    "--tasks",
                    str(tasks_file),
                    "-n",
                    "5",
                ],
            )

        # Should run once and then exit due to tasks being complete
        assert call_count == 1
        assert result.exit_code == 0


class TestTasksRemaining:
    """Tests for the tasks_remaining function."""

    def test_tasks_remaining_true_when_unchecked_tasks(self, tmp_path: Path) -> None:
        """Returns True when there are unchecked task boxes."""
        tasks_file = tmp_path / "TASKS.md"
        tasks_file.write_text("# Tasks\n\n## Todo\n\n- [ ] task1\n- [ ] task2\n")
        assert tasks_remaining(tasks_file) is True

    def test_tasks_remaining_false_when_all_complete(self, tmp_path: Path) -> None:
        """Returns False when all tasks are checked."""
        tasks_file = tmp_path / "TASKS.md"
        tasks_file.write_text("# Tasks\n\n## Done\n\n- [x] task1\n- [x] task2\n")
        assert tasks_remaining(tasks_file) is False

    def test_tasks_remaining_true_when_file_missing(self, tmp_path: Path) -> None:
        """Returns True when tasks file doesn't exist (keep running)."""
        tasks_file = tmp_path / "TASKS.md"
        assert tasks_remaining(tasks_file) is True


class TestDryRunWithStopFile:
    """Tests for dry-run mode with stop file option."""

    def test_dry_run_shows_stop_file_option(self, tmp_path: Path) -> None:
        """Dry run output shows the stop file when specified."""
        prompt_file = tmp_path / "LOOP-PROMPT.md"
        prompt_file.write_text("test prompt")
        stop_file = tmp_path / "DONE.md"

        result = runner.invoke(
            app,
            [
                "run",
                "-f",
                str(prompt_file),
                "--stop-file",
                str(stop_file),
                "--dry-run",
            ],
        )

        assert (
            "stop-file" in result.output.lower() or "stop file" in result.output.lower()
        )
        assert result.exit_code == 0
