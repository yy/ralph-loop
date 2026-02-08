"""Tests for the wiggum list command."""

from pathlib import Path

from typer.testing import CliRunner

from wiggum.cli import app

runner = CliRunner()


class TestListCommand:
    """Tests for the `wiggum list` command."""

    def test_list_shows_todo_tasks(self, tmp_path: Path) -> None:
        """Displays pending tasks."""
        tasks_file = tmp_path / "TODO.md"
        tasks_file.write_text(
            "# Tasks\n\n## Todo\n\n- [ ] First task\n- [ ] Second task\n"
        )

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                app,
                ["list", "--tasks-file", str(tasks_file)],
            )

        assert result.exit_code == 0
        assert "First task" in result.output
        assert "Second task" in result.output

    def test_list_shows_done_tasks(self, tmp_path: Path) -> None:
        """Displays completed tasks."""
        tasks_file = tmp_path / "TODO.md"
        tasks_file.write_text(
            "# Tasks\n\n## Done\n\n- [x] Completed task\n\n## Todo\n\n"
        )

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                app,
                ["list", "--tasks-file", str(tasks_file)],
            )

        assert result.exit_code == 0
        assert "Completed task" in result.output
        assert "Done:" in result.output

    def test_list_shows_both_todo_and_done(self, tmp_path: Path) -> None:
        """Displays both pending and completed tasks."""
        tasks_file = tmp_path / "TODO.md"
        tasks_file.write_text(
            "# Tasks\n\n"
            "## Done\n\n"
            "- [x] Completed task\n\n"
            "## Todo\n\n"
            "- [ ] Pending task\n"
        )

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                app,
                ["list", "--tasks-file", str(tasks_file)],
            )

        assert result.exit_code == 0
        assert "Completed task" in result.output
        assert "Pending task" in result.output
        assert "Todo:" in result.output
        assert "Done:" in result.output

    def test_list_shows_none_when_no_todo_tasks(self, tmp_path: Path) -> None:
        """Shows '(none)' when there are no pending tasks."""
        tasks_file = tmp_path / "TODO.md"
        tasks_file.write_text(
            "# Tasks\n\n## Done\n\n- [x] Completed task\n\n## Todo\n\n"
        )

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                app,
                ["list", "--tasks-file", str(tasks_file)],
            )

        assert result.exit_code == 0
        assert "(none)" in result.output

    def test_list_default_file(self, tmp_path: Path) -> None:
        """Uses TODO.md in current directory by default."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("TODO.md").write_text("# Tasks\n\n## Todo\n\n- [ ] A task\n")
            result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "A task" in result.output

    def test_list_missing_file_shows_error(self, tmp_path: Path) -> None:
        """Shows error when tasks file doesn't exist."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                app,
                ["list", "--tasks-file", "nonexistent.md"],
            )

        assert result.exit_code == 1
        assert "No tasks file found" in result.output

    def test_list_short_flag(self, tmp_path: Path) -> None:
        """Supports -f as shorthand for --tasks-file."""
        tasks_file = tmp_path / "custom.md"
        tasks_file.write_text("# Tasks\n\n## Todo\n\n- [ ] Custom task\n")

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                app,
                ["list", "-f", str(tasks_file)],
            )

        assert result.exit_code == 0
        assert "Custom task" in result.output

    def test_list_preserves_task_order(self, tmp_path: Path) -> None:
        """Tasks are displayed in the order they appear in the file."""
        tasks_file = tmp_path / "TODO.md"
        tasks_file.write_text(
            "# Tasks\n\n## Todo\n\n- [ ] First\n- [ ] Second\n- [ ] Third\n"
        )

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                app,
                ["list", "--tasks-file", str(tasks_file)],
            )

        assert result.exit_code == 0
        first_pos = result.output.find("First")
        second_pos = result.output.find("Second")
        third_pos = result.output.find("Third")
        assert first_pos < second_pos < third_pos

    def test_list_handles_uppercase_x_checkbox(self, tmp_path: Path) -> None:
        """Recognizes [X] as a completed task."""
        tasks_file = tmp_path / "TODO.md"
        tasks_file.write_text("# Tasks\n\n## Done\n\n- [X] Uppercase completed\n")

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                app,
                ["list", "--tasks-file", str(tasks_file)],
            )

        assert result.exit_code == 0
        assert "Uppercase completed" in result.output
