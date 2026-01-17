"""Tests for the git workflow integration in the run command."""

from pathlib import Path

from typer.testing import CliRunner

from wiggum.cli import app

runner = CliRunner()


class TestGitWorkflowDryRun:
    """Tests for git workflow dry run output."""

    def test_dry_run_shows_git_workflow_when_enabled(self, tmp_path: Path) -> None:
        """Shows git workflow info when --git flag is used."""
        prompt_file = tmp_path / "LOOP-PROMPT.md"
        prompt_file.write_text("Test prompt")
        tasks_file = tmp_path / "TASKS.md"
        tasks_file.write_text("# Tasks\n\n## Todo\n\n- [ ] Test task\n")

        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("LOOP-PROMPT.md").write_text(prompt_file.read_text())
            Path("TASKS.md").write_text(tasks_file.read_text())
            result = runner.invoke(app, ["run", "--dry-run", "--git"])

        assert result.exit_code == 0
        assert "Git workflow: enabled" in result.output

    def test_dry_run_shows_branch_prefix(self, tmp_path: Path) -> None:
        """Shows branch prefix when --git flag is used."""
        prompt_file = tmp_path / "LOOP-PROMPT.md"
        prompt_file.write_text("Test prompt")
        tasks_file = tmp_path / "TASKS.md"
        tasks_file.write_text("# Tasks\n\n## Todo\n\n- [ ] Test task\n")

        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("LOOP-PROMPT.md").write_text(prompt_file.read_text())
            Path("TASKS.md").write_text(tasks_file.read_text())
            result = runner.invoke(
                app, ["run", "--dry-run", "--git", "--branch-prefix", "myprefix"]
            )

        assert result.exit_code == 0
        assert "Branch prefix: myprefix" in result.output

    def test_dry_run_default_branch_prefix(self, tmp_path: Path) -> None:
        """Uses 'wiggum' as default branch prefix."""
        prompt_file = tmp_path / "LOOP-PROMPT.md"
        prompt_file.write_text("Test prompt")
        tasks_file = tmp_path / "TASKS.md"
        tasks_file.write_text("# Tasks\n\n## Todo\n\n- [ ] Test task\n")

        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("LOOP-PROMPT.md").write_text(prompt_file.read_text())
            Path("TASKS.md").write_text(tasks_file.read_text())
            result = runner.invoke(app, ["run", "--dry-run", "--git"])

        assert result.exit_code == 0
        assert "Branch prefix: wiggum" in result.output

    def test_dry_run_no_git_workflow_by_default(self, tmp_path: Path) -> None:
        """Git workflow is not shown when --git flag is not used."""
        prompt_file = tmp_path / "LOOP-PROMPT.md"
        prompt_file.write_text("Test prompt")
        tasks_file = tmp_path / "TASKS.md"
        tasks_file.write_text("# Tasks\n\n## Todo\n\n- [ ] Test task\n")

        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("LOOP-PROMPT.md").write_text(prompt_file.read_text())
            Path("TASKS.md").write_text(tasks_file.read_text())
            result = runner.invoke(app, ["run", "--dry-run"])

        assert result.exit_code == 0
        assert "Git workflow" not in result.output


class TestGitWorkflowConfig:
    """Tests for git workflow configuration resolution."""

    def test_git_workflow_from_config(self, tmp_path: Path) -> None:
        """Reads git workflow setting from config file."""
        config_file = tmp_path / ".wiggum.toml"
        config_file.write_text('[git]\nenabled = true\nbranch_prefix = "feature"')
        prompt_file = tmp_path / "LOOP-PROMPT.md"
        prompt_file.write_text("Test prompt")
        tasks_file = tmp_path / "TASKS.md"
        tasks_file.write_text("# Tasks\n\n## Todo\n\n- [ ] Test task\n")

        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path(".wiggum.toml").write_text(config_file.read_text())
            Path("LOOP-PROMPT.md").write_text(prompt_file.read_text())
            Path("TASKS.md").write_text(tasks_file.read_text())
            result = runner.invoke(app, ["run", "--dry-run"])

        assert result.exit_code == 0
        assert "Git workflow: enabled" in result.output
        assert "Branch prefix: feature" in result.output

    def test_no_git_flag_overrides_config(self, tmp_path: Path) -> None:
        """--no-git flag overrides config file setting."""
        config_file = tmp_path / ".wiggum.toml"
        config_file.write_text("[git]\nenabled = true")
        prompt_file = tmp_path / "LOOP-PROMPT.md"
        prompt_file.write_text("Test prompt")
        tasks_file = tmp_path / "TASKS.md"
        tasks_file.write_text("# Tasks\n\n## Todo\n\n- [ ] Test task\n")

        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path(".wiggum.toml").write_text(config_file.read_text())
            Path("LOOP-PROMPT.md").write_text(prompt_file.read_text())
            Path("TASKS.md").write_text(tasks_file.read_text())
            result = runner.invoke(app, ["run", "--dry-run", "--no-git"])

        assert result.exit_code == 0
        assert "Git workflow" not in result.output


class TestGitWorkflowValidation:
    """Tests for git workflow validation."""

    def test_git_and_no_git_mutually_exclusive(self, tmp_path: Path) -> None:
        """Cannot use both --git and --no-git flags."""
        prompt_file = tmp_path / "LOOP-PROMPT.md"
        prompt_file.write_text("Test prompt")
        tasks_file = tmp_path / "TASKS.md"
        tasks_file.write_text("# Tasks\n\n## Todo\n\n- [ ] Test task\n")

        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("LOOP-PROMPT.md").write_text(prompt_file.read_text())
            Path("TASKS.md").write_text(tasks_file.read_text())
            result = runner.invoke(app, ["run", "--git", "--no-git"])

        assert result.exit_code == 1
        assert "mutually exclusive" in result.output

    def test_git_requires_git_repo(self, tmp_path: Path) -> None:
        """--git flag requires a git repository."""
        prompt_file = tmp_path / "LOOP-PROMPT.md"
        prompt_file.write_text("Test prompt")
        tasks_file = tmp_path / "TASKS.md"
        tasks_file.write_text("# Tasks\n\n## Todo\n\n- [ ] Test task\n")

        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("LOOP-PROMPT.md").write_text(prompt_file.read_text())
            Path("TASKS.md").write_text(tasks_file.read_text())
            result = runner.invoke(app, ["run", "--git", "-n", "1"])

        assert result.exit_code == 1
        assert "requires a git repository" in result.output
