"""Tests for refactoring guidance in LOOP-PROMPT.md template.

After completing a task, the agent should perform meaningful cleanup:
- Remove dead code
- Simplify overly complex logic
- Consolidate duplicates
- Delete trivial tests
- Ensure code is production-ready
"""

from wiggum.config import get_templates_dir


class TestRefactoringGuidanceInTemplate:
    """Tests for refactoring guidance in LOOP-PROMPT.md template."""

    def test_workflow_has_refactoring_section(self) -> None:
        """The workflow should have a dedicated refactoring/cleanup section."""
        template_path = get_templates_dir() / "LOOP-PROMPT.md"
        content = template_path.read_text()

        # The workflow should have a numbered step that covers cleanup/refactoring
        workflow_start = content.find("## Workflow")
        assert workflow_start != -1, "Template should have Workflow section"

        workflow_section = content[workflow_start:]
        # Should contain refactoring guidance in the workflow
        assert (
            "refactor" in workflow_section.lower()
            or "cleanup" in workflow_section.lower()
        ), "Workflow should include refactoring/cleanup guidance"

    def test_refactoring_includes_dead_code_removal(self) -> None:
        """Refactoring guidance should mention removing dead/unused code."""
        template_path = get_templates_dir() / "LOOP-PROMPT.md"
        content = template_path.read_text().lower()

        assert "dead code" in content or "unused" in content or "remove" in content, (
            "Template should guide agent to remove dead/unused code"
        )

    def test_refactoring_includes_simplification(self) -> None:
        """Refactoring guidance should mention simplifying complex code."""
        template_path = get_templates_dir() / "LOOP-PROMPT.md"
        content = template_path.read_text().lower()

        assert "simplif" in content, (
            "Template should guide agent to simplify complex code"
        )

    def test_refactoring_includes_duplication_handling(self) -> None:
        """Refactoring guidance should mention consolidating duplicates."""
        template_path = get_templates_dir() / "LOOP-PROMPT.md"
        content = template_path.read_text().lower()

        assert "duplicat" in content or "consolidat" in content, (
            "Template should guide agent to handle code duplication"
        )

    def test_refactoring_includes_test_cleanup(self) -> None:
        """Refactoring guidance should mention cleaning up trivial tests."""
        template_path = get_templates_dir() / "LOOP-PROMPT.md"
        content = template_path.read_text().lower()

        # Should mention cleaning up tests that don't add value
        assert (
            ("trivial" in content and "test" in content)
            or "test cleanup" in content
            or "delete test" in content
        ), "Template should guide agent to clean up trivial tests"

    def test_refactoring_is_required_before_marking_complete(self) -> None:
        """Refactoring should happen before marking a task complete."""
        template_path = get_templates_dir() / "LOOP-PROMPT.md"
        content = template_path.read_text()

        # Find positions of key phrases
        workflow_start = content.find("## Workflow")
        workflow_section = content[workflow_start:]

        # The refactoring step should come before marking task complete
        refactor_pos = workflow_section.lower().find("refactor")
        cleanup_pos = workflow_section.lower().find("cleanup")
        mark_complete_pos = workflow_section.lower().find("mark the task complete")

        # At least one of refactor/cleanup should appear
        earliest_cleanup = (
            min(pos for pos in [refactor_pos, cleanup_pos] if pos != -1)
            if refactor_pos != -1 or cleanup_pos != -1
            else -1
        )

        assert earliest_cleanup != -1, "Should have refactoring/cleanup guidance"
        assert mark_complete_pos != -1, "Should have 'mark task complete' step"
        assert earliest_cleanup < mark_complete_pos, (
            "Refactoring should happen before marking task complete"
        )
