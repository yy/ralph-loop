"""Tests for lean init (default, no Claude call)."""

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from wiggum.cli import app

runner = CliRunner()


class TestLeanInit:
    """Tests for lean init behavior (no --suggest flag)."""

    def test_lean_init_creates_all_files(self, tmp_path: Path) -> None:
        """Lean init creates LOOP-PROMPT.md, TODO.md, and .wiggum.toml."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("templates").mkdir()
            (Path("templates") / "LOOP-PROMPT.md").write_text(
                "## Goal\n\n{{goal}}\n\n## Workflow\n"
            )
            (Path("templates") / "TODO.md").write_text(
                "# Tasks\n\n## Todo\n\n{{tasks}}\n"
            )
            (Path("templates") / "META-PROMPT.md").write_text("Analyze {{goal}}")

            # doc files, task, empty, security (3=yolo), git (n)
            result = runner.invoke(
                app,
                ["init"],
                input="README.md\nMy task\n\n3\nn\n",
            )

            assert result.exit_code == 0, f"Init failed: {result.output}"
            assert Path("LOOP-PROMPT.md").exists()
            assert Path("TODO.md").exists()
            assert Path(".wiggum.toml").exists()

    def test_lean_init_shows_suggest_tip(self, tmp_path: Path) -> None:
        """Lean init shows tip about wiggum suggest."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("templates").mkdir()
            (Path("templates") / "LOOP-PROMPT.md").write_text(
                "## Goal\n\n{{goal}}\n\n## Workflow\n"
            )
            (Path("templates") / "TODO.md").write_text(
                "# Tasks\n\n## Todo\n\n{{tasks}}\n"
            )
            (Path("templates") / "META-PROMPT.md").write_text("Analyze {{goal}}")

            result = runner.invoke(
                app,
                ["init"],
                input="README.md\nTask 1\n\n1\nn\n",
            )

            assert result.exit_code == 0
            assert "wiggum suggest" in result.output

    def test_lean_init_does_not_call_claude(self, tmp_path: Path) -> None:
        """Lean init does not call run_claude_with_retry."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("templates").mkdir()
            (Path("templates") / "LOOP-PROMPT.md").write_text(
                "## Goal\n\n{{goal}}\n\n## Workflow\n"
            )
            (Path("templates") / "TODO.md").write_text(
                "# Tasks\n\n## Todo\n\n{{tasks}}\n"
            )
            (Path("templates") / "META-PROMPT.md").write_text("Analyze {{goal}}")

            with patch("wiggum.cli.run_claude_with_retry") as mock_claude:
                result = runner.invoke(
                    app,
                    ["init"],
                    input="README.md\nTask 1\n\n1\nn\n",
                )

            assert result.exit_code == 0
            mock_claude.assert_not_called()

    def test_suggest_flag_triggers_claude_call(self, tmp_path: Path) -> None:
        """--suggest flag triggers Claude call (returns error, falls back to manual)."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("templates").mkdir()
            (Path("templates") / "LOOP-PROMPT.md").write_text(
                "## Goal\n\n{{goal}}\n\n## Workflow\n"
            )
            (Path("templates") / "TODO.md").write_text(
                "# Tasks\n\n## Todo\n\n{{tasks}}\n"
            )
            (Path("templates") / "META-PROMPT.md").write_text(
                "{{goal}}{{existing_tasks}}"
            )

            # Mock returns (None, error_msg) so init falls back to manual entry.
            # Input matches the manual-entry prompts: doc files, task, empty, security, git.
            with patch(
                "wiggum.cli.run_claude_with_retry",
                return_value=(None, "Claude returned no output"),
            ) as mock_claude:
                result = runner.invoke(
                    app,
                    ["init", "--suggest"],
                    input="README.md\nTask 1\n\n1\nn\n",
                )

            assert result.exit_code == 0
            mock_claude.assert_called_once()

    def test_short_flag_triggers_claude_call(self, tmp_path: Path) -> None:
        """-s short flag triggers Claude call."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("templates").mkdir()
            (Path("templates") / "LOOP-PROMPT.md").write_text(
                "## Goal\n\n{{goal}}\n\n## Workflow\n"
            )
            (Path("templates") / "TODO.md").write_text(
                "# Tasks\n\n## Todo\n\n{{tasks}}\n"
            )
            (Path("templates") / "META-PROMPT.md").write_text(
                "{{goal}}{{existing_tasks}}"
            )

            # Mock returns (None, error_msg) so init falls back to manual entry.
            with patch(
                "wiggum.cli.run_claude_with_retry",
                return_value=(None, "Claude returned no output"),
            ) as mock_claude:
                result = runner.invoke(
                    app,
                    ["init", "-s"],
                    input="README.md\nTask 1\n\n1\nn\n",
                )

            assert result.exit_code == 0
            mock_claude.assert_called_once()

    def test_suggest_flag_does_not_show_tip(self, tmp_path: Path) -> None:
        """--suggest flag does not show suggest tip."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("templates").mkdir()
            (Path("templates") / "LOOP-PROMPT.md").write_text(
                "## Goal\n\n{{goal}}\n\n## Workflow\n"
            )
            (Path("templates") / "TODO.md").write_text(
                "# Tasks\n\n## Todo\n\n{{tasks}}\n"
            )
            (Path("templates") / "META-PROMPT.md").write_text(
                "{{goal}}{{existing_tasks}}"
            )

            with patch(
                "wiggum.cli.run_claude_with_retry",
                return_value=(None, "Claude returned no output"),
            ):
                result = runner.invoke(
                    app,
                    ["init", "--suggest"],
                    input="README.md\nTask 1\n\n1\nn\n",
                )

            assert result.exit_code == 0
            assert "Tip: run 'wiggum suggest'" not in result.output

    def test_suggest_without_meta_prompt_errors(self, tmp_path: Path) -> None:
        """--suggest errors if META-PROMPT.md template is missing."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("templates").mkdir()
            (Path("templates") / "LOOP-PROMPT.md").write_text(
                "## Goal\n\n{{goal}}\n\n## Workflow\n"
            )
            (Path("templates") / "TODO.md").write_text(
                "# Tasks\n\n## Todo\n\n{{tasks}}\n"
            )
            # No META-PROMPT.md

            result = runner.invoke(app, ["init", "--suggest"])

            assert result.exit_code == 1
            assert "Meta prompt not found" in result.output

    def test_lean_init_force_overwrites_existing(self, tmp_path: Path) -> None:
        """--force with lean init overwrites LOOP-PROMPT.md without Claude."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("templates").mkdir()
            (Path("templates") / "LOOP-PROMPT.md").write_text(
                "## Goal\n\n{{goal}}\n\n## Workflow\n"
            )
            (Path("templates") / "TODO.md").write_text(
                "# Tasks\n\n## Todo\n\n{{tasks}}\n"
            )
            (Path("templates") / "META-PROMPT.md").write_text("Analyze {{goal}}")

            # Create existing files
            Path("LOOP-PROMPT.md").write_text("Old prompt")
            Path("TODO.md").write_text("# Tasks\n\n## Todo\n\n- [ ] Old task\n")

            with patch("wiggum.cli.run_claude_with_retry") as mock_claude:
                result = runner.invoke(
                    app,
                    ["init", "--force"],
                    input="README.md\nNew task\n\n3\nn\n",
                )

            assert result.exit_code == 0, f"Init failed: {result.output}"
            mock_claude.assert_not_called()
            # LOOP-PROMPT.md should be overwritten with template content
            assert "Old prompt" not in Path("LOOP-PROMPT.md").read_text()
            # TODO.md should be overwritten (--force)
            content = Path("TODO.md").read_text()
            assert "- [ ] New task" in content
            assert "Old task" not in content
