"""Tests for the wiggum prune command."""

from pathlib import Path

from typer.testing import CliRunner

from wiggum.cli import app

runner = CliRunner()


class TestPruneCommand:
    """Tests for the `wiggum prune` command."""

    def test_prune_removes_done_tasks(self, tmp_path: Path) -> None:
        """Removes completed tasks from Done section."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("TODO.md").write_text(
                "# Tasks\n\n## Done\n\n- [x] First task\n- [x] Second task\n\n## Todo\n\n- [ ] Pending task\n"
            )

            result = runner.invoke(app, ["prune", "--force"])

            content = Path("TODO.md").read_text()
            assert "First task" not in content
            assert "Second task" not in content
            assert "Pending task" in content
            assert "## Done" in content  # Header preserved

        assert result.exit_code == 0
        assert "Removed 2 completed task(s)" in result.output

    def test_prune_dry_run_preview(self, tmp_path: Path) -> None:
        """--dry-run shows what would be removed without modifying file."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("TODO.md").write_text(
                "# Tasks\n\n## Done\n\n- [x] Done task\n\n## Todo\n\n- [ ] Open task\n"
            )

            result = runner.invoke(app, ["prune", "--dry-run"])

            # File should be unchanged
            content = Path("TODO.md").read_text()
            assert "Done task" in content

        assert result.exit_code == 0
        assert "Would remove 1 completed task(s)" in result.output
        assert "- [x] Done task" in result.output

    def test_prune_force_skips_confirmation(self, tmp_path: Path) -> None:
        """--force skips confirmation prompt."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("TODO.md").write_text(
                "# Tasks\n\n## Done\n\n- [x] Completed item\n\n## Todo\n\n"
            )

            result = runner.invoke(app, ["prune", "--force"])

            content = Path("TODO.md").read_text()
            assert "Completed item" not in content

        assert result.exit_code == 0
        assert "Removed 1 completed task(s)" in result.output

    def test_prune_no_done_tasks(self, tmp_path: Path) -> None:
        """Shows message when no completed tasks exist."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("TODO.md").write_text(
                "# Tasks\n\n## Done\n\n## Todo\n\n- [ ] Open task\n"
            )

            result = runner.invoke(app, ["prune"])

        assert result.exit_code == 0
        assert "No completed tasks to remove" in result.output

    def test_prune_missing_file_error(self, tmp_path: Path) -> None:
        """Shows error when tasks file doesn't exist."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(app, ["prune"])

        assert result.exit_code == 1
        assert "No tasks file found" in result.output

    def test_prune_requires_confirmation(self, tmp_path: Path) -> None:
        """Prompts for confirmation without --force."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("TODO.md").write_text(
                "# Tasks\n\n## Done\n\n- [x] Done task\n\n## Todo\n\n"
            )

            # Answer 'n' to confirmation
            result = runner.invoke(app, ["prune"], input="n\n")

            # File should be unchanged
            content = Path("TODO.md").read_text()
            assert "Done task" in content

        assert result.exit_code == 0
        assert "Aborted" in result.output

    def test_prune_confirmation_yes(self, tmp_path: Path) -> None:
        """Tasks are removed when user confirms."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("TODO.md").write_text(
                "# Tasks\n\n## Done\n\n- [x] Done task\n\n## Todo\n\n"
            )

            result = runner.invoke(app, ["prune"], input="y\n")

            content = Path("TODO.md").read_text()
            assert "Done task" not in content

        assert result.exit_code == 0
        assert "Removed 1 completed task(s)" in result.output

    def test_prune_custom_tasks_file(self, tmp_path: Path) -> None:
        """Works with custom tasks file path."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("custom-tasks.md").write_text(
                "# Tasks\n\n## Done\n\n- [x] Custom task\n\n## Todo\n\n"
            )

            result = runner.invoke(app, ["prune", "-f", "custom-tasks.md", "--force"])

            content = Path("custom-tasks.md").read_text()
            assert "Custom task" not in content

        assert result.exit_code == 0
        assert "Removed 1 completed task(s)" in result.output

    def test_prune_preserves_todo_section(self, tmp_path: Path) -> None:
        """Todo section remains intact after pruning."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("TODO.md").write_text(
                "# Tasks\n\n## Done\n\n- [x] Finished\n\n## Todo\n\n- [ ] Task 1\n- [ ] Task 2\n"
            )

            result = runner.invoke(app, ["prune", "--force"])

            content = Path("TODO.md").read_text()
            assert "- [ ] Task 1" in content
            assert "- [ ] Task 2" in content
            assert "Finished" not in content

        assert result.exit_code == 0

    def test_prune_ignores_checked_tasks_outside_done_section(
        self, tmp_path: Path
    ) -> None:
        """Checked tasks in non-Done sections should not be pruned."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("TASKS.md").write_text(
                "# Tasks\n\n## Done\n\n## Todo\n\n- [x] Checked in todo\n- [ ] Pending\n"
            )

            result = runner.invoke(app, ["prune", "--force"])

            content = Path("TASKS.md").read_text()
            assert "Checked in todo" in content
            assert "Pending" in content

        assert result.exit_code == 0
        assert "No completed tasks to remove" in result.output
