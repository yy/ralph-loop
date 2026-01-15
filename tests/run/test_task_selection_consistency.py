"""Tests for task selection consistency between display and prompt.

This verifies that the task displayed at loop start matches what the
agent is instructed to work on, ensuring consistency between code and
the LOOP-PROMPT.md instructions.
"""

from pathlib import Path

from wiggum.tasks import get_current_task


class TestTaskSelectionConsistency:
    """Tests that task selection is consistent and predictable."""

    def test_selects_first_incomplete_in_in_progress_section(
        self, tmp_path: Path
    ) -> None:
        """If In Progress has incomplete tasks, those are selected first."""
        tasks_file = tmp_path / "TASKS.md"
        tasks_file.write_text(
            "# Tasks\n\n"
            "## Done\n\n"
            "- [x] Completed task\n\n"
            "## In Progress\n\n"
            "- [ ] Task being worked on\n\n"
            "## Todo\n\n"
            "- [ ] Future task\n"
        )
        result = get_current_task(tasks_file)
        assert result == "Task being worked on"

    def test_selects_first_incomplete_in_todo_when_in_progress_empty(
        self, tmp_path: Path
    ) -> None:
        """If In Progress is empty, first Todo task is selected."""
        tasks_file = tmp_path / "TASKS.md"
        tasks_file.write_text(
            "# Tasks\n\n"
            "## Done\n\n"
            "- [x] Completed task\n\n"
            "## In Progress\n\n"
            "## Todo\n\n"
            "- [ ] First todo task\n"
            "- [ ] Second todo task\n"
        )
        result = get_current_task(tasks_file)
        assert result == "First todo task"

    def test_with_multiple_subsections_selects_first_incomplete(
        self, tmp_path: Path
    ) -> None:
        """With multiple subsections, selects first incomplete task in file order."""
        tasks_file = tmp_path / "TASKS.md"
        tasks_file.write_text(
            "# Tasks\n\n"
            "## Done\n\n"
            "- [x] Completed task\n\n"
            "## In Progress\n\n"
            "## Todo\n\n"
            "- [ ] First main todo task\n\n"
            "## Feature A\n\n"
            "- [ ] Feature A task 1\n\n"
            "## Feature B\n\n"
            "- [ ] Feature B task 1\n"
        )
        result = get_current_task(tasks_file)
        # Should select first incomplete task in file order (main Todo section)
        assert result == "First main todo task"

    def test_in_progress_takes_priority_over_any_subsection(
        self, tmp_path: Path
    ) -> None:
        """In Progress tasks take priority over any other section's tasks."""
        tasks_file = tmp_path / "TASKS.md"
        tasks_file.write_text(
            "# Tasks\n\n"
            "## Done\n\n"
            "- [x] Completed\n\n"
            "## In Progress\n\n"
            "- [ ] Currently working on this\n\n"
            "## Todo\n\n"
            "- [ ] High priority task\n\n"
            "## Cleanup\n\n"
            "- [ ] Cleanup task\n"
        )
        result = get_current_task(tasks_file)
        assert result == "Currently working on this"

    def test_selection_matches_loop_prompt_first_incomplete_semantics(
        self, tmp_path: Path
    ) -> None:
        """The selected task matches 'first incomplete task' semantics.

        This test verifies alignment between get_current_task and
        what the LOOP-PROMPT.md should instruct the agent to do.
        """
        tasks_file = tmp_path / "TASKS.md"
        # Realistic TASKS.md structure with multiple sections
        tasks_file.write_text(
            "# Tasks\n\n"
            "## Done\n\n"
            "- [x] Task A\n"
            "- [x] Task B\n\n"
            "## In Progress\n\n"
            "## Todo\n\n"
            "- [ ] First incomplete task - this should be selected\n"
            "- [ ] Second task\n\n"
            "## Test Cleanup\n\n"
            "- [ ] Remove test file X\n"
            "- [ ] Remove test file Y\n"
        )
        result = get_current_task(tasks_file)
        # The agent should work on the first incomplete task in file order
        assert result == "First incomplete task - this should be selected"


class TestLoopPromptTaskSelectionWording:
    """Tests that LOOP-PROMPT.md uses consistent wording for task selection."""

    def test_loop_prompt_uses_first_incomplete_wording(self) -> None:
        """The LOOP-PROMPT.md should instruct agent to work on first incomplete task.

        This ensures alignment between:
        - What the code displays as "Current task" (via get_current_task)
        - What the agent is instructed to work on in LOOP-PROMPT.md
        """
        from wiggum.config import get_templates_dir

        template_path = get_templates_dir() / "LOOP-PROMPT.md"
        assert template_path.exists(), "LOOP-PROMPT.md template not found"
        content = template_path.read_text()

        # Should NOT use ambiguous "highest priority" wording
        assert "highest priority" not in content.lower(), (
            "LOOP-PROMPT.md should not use ambiguous 'highest priority' wording. "
            "Use 'first incomplete task' to match code behavior."
        )

        # Should use clear "first incomplete" wording
        assert "first incomplete task" in content.lower(), (
            "LOOP-PROMPT.md should use 'first incomplete task' wording "
            "to match get_current_task behavior."
        )
