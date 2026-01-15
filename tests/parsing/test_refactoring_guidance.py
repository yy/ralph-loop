"""Tests for refactoring guidance in LOOP-PROMPT.md template.

After completing a task, the agent should examine the codebase and
add refactoring tasks (simplification, cleanup, better organization).
"""

from pathlib import Path


class TestRefactoringGuidanceInTemplate:
    """Tests for refactoring guidance in LOOP-PROMPT.md template."""

    def test_loop_prompt_template_has_refactoring_step(self) -> None:
        """The LOOP-PROMPT.md template should include a step to add refactoring tasks."""
        template_path = (
            Path(__file__).parent.parent.parent / "templates" / "LOOP-PROMPT.md"
        )
        assert template_path.exists(), "LOOP-PROMPT.md template not found"
        content = template_path.read_text()

        # The template should mention examining the codebase for refactoring opportunities
        assert "refactor" in content.lower(), (
            f"LOOP-PROMPT.md template should mention refactoring. Content:\n{content}"
        )

    def test_loop_prompt_template_mentions_simplification(self) -> None:
        """The template should mention simplification as a refactoring goal."""
        template_path = (
            Path(__file__).parent.parent.parent / "templates" / "LOOP-PROMPT.md"
        )
        content = template_path.read_text()

        assert "simplif" in content.lower(), (
            "LOOP-PROMPT.md template should mention simplification. "
            f"Content:\n{content}"
        )

    def test_loop_prompt_template_mentions_cleanup(self) -> None:
        """The template should mention cleanup as a refactoring goal."""
        template_path = (
            Path(__file__).parent.parent.parent / "templates" / "LOOP-PROMPT.md"
        )
        content = template_path.read_text()

        assert "cleanup" in content.lower() or "clean up" in content.lower(), (
            f"LOOP-PROMPT.md template should mention cleanup. Content:\n{content}"
        )

    def test_loop_prompt_template_has_refactoring_in_workflow(self) -> None:
        """The refactoring step should be part of the workflow section."""
        template_path = (
            Path(__file__).parent.parent.parent / "templates" / "LOOP-PROMPT.md"
        )
        content = template_path.read_text()

        # Find the workflow section and check it contains refactoring
        workflow_start = content.find("## Workflow")
        assert workflow_start != -1, (
            "LOOP-PROMPT.md template should have Workflow section"
        )

        # Get content after workflow section
        workflow_section = content[workflow_start:]

        # The workflow should mention examining/reviewing code for refactoring
        assert "refactor" in workflow_section.lower(), (
            "Workflow section should include refactoring step. "
            f"Workflow section:\n{workflow_section}"
        )
