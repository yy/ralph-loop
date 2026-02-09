"""Tests for the wiggum git module."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from wiggum.git import (
    GitError,
    create_branch,
    create_pr,
    fetch_and_merge_main,
    get_current_branch,
    get_main_branch_name,
    is_git_repo,
    push_branch,
)


class TestIsGitRepo:
    """Tests for is_git_repo function."""

    def test_returns_true_in_git_repo(self, tmp_path: Path) -> None:
        """Returns True when in a git repository."""
        # Initialize a git repo
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        assert is_git_repo(tmp_path) is True

    def test_returns_false_outside_git_repo(self, tmp_path: Path) -> None:
        """Returns False when not in a git repository."""
        assert is_git_repo(tmp_path) is False


class TestGetMainBranchName:
    """Tests for get_main_branch_name function."""

    def test_detects_main_branch(self, tmp_path: Path) -> None:
        """Detects 'main' as the main branch."""
        subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=tmp_path,
            capture_output=True,
        )
        (tmp_path / "file.txt").write_text("content")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True
        )

        assert get_main_branch_name(tmp_path) == "main"

    def test_detects_master_branch(self, tmp_path: Path) -> None:
        """Detects 'master' as the main branch when 'main' doesn't exist."""
        subprocess.run(
            ["git", "init", "-b", "master"], cwd=tmp_path, capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=tmp_path,
            capture_output=True,
        )
        (tmp_path / "file.txt").write_text("content")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True
        )

        assert get_main_branch_name(tmp_path) == "master"

    def test_raises_when_no_main_or_master(self, tmp_path: Path) -> None:
        """Raises GitError when neither 'main' nor 'master' exists."""
        subprocess.run(
            ["git", "init", "-b", "develop"], cwd=tmp_path, capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=tmp_path,
            capture_output=True,
        )
        (tmp_path / "file.txt").write_text("content")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True
        )

        with pytest.raises(GitError, match="Could not detect main branch"):
            get_main_branch_name(tmp_path)


class TestGetCurrentBranch:
    """Tests for get_current_branch function."""

    def test_returns_current_branch_name(self, tmp_path: Path) -> None:
        """Returns the name of the current branch."""
        subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=tmp_path,
            capture_output=True,
        )
        (tmp_path / "file.txt").write_text("content")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True
        )

        assert get_current_branch(tmp_path) == "main"

    @patch("wiggum.git.subprocess.run")
    def test_raises_on_timeout(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Raises GitError when git command times out."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="git", timeout=120)

        with pytest.raises(GitError, match="timed out"):
            get_current_branch(tmp_path)


class TestCreateBranch:
    """Tests for create_branch function."""

    def test_creates_and_switches_to_new_branch(self, tmp_path: Path) -> None:
        """Creates a new branch and switches to it."""
        subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=tmp_path,
            capture_output=True,
        )
        (tmp_path / "file.txt").write_text("content")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True
        )

        create_branch("feature-branch", tmp_path)

        assert get_current_branch(tmp_path) == "feature-branch"

    def test_raises_when_branch_already_exists(self, tmp_path: Path) -> None:
        """Raises GitError when trying to create existing branch."""
        subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=tmp_path,
            capture_output=True,
        )
        (tmp_path / "file.txt").write_text("content")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True
        )

        with pytest.raises(GitError, match="already exists"):
            create_branch("main", tmp_path)


class TestFetchAndMergeMain:
    """Tests for fetch_and_merge_main function."""

    def test_skips_when_no_remote(self, tmp_path: Path) -> None:
        """Returns early when there is no remote configured."""
        subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=tmp_path,
            capture_output=True,
        )
        (tmp_path / "file.txt").write_text("content")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True
        )

        # Should not raise - just skips silently
        result = fetch_and_merge_main(tmp_path)
        assert result is False  # Indicates no fetch/merge happened


class TestPushBranch:
    """Tests for push_branch function."""

    def test_raises_when_no_remote(self, tmp_path: Path) -> None:
        """Raises GitError when there is no remote configured."""
        subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=tmp_path,
            capture_output=True,
        )
        (tmp_path / "file.txt").write_text("content")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True
        )

        with pytest.raises(GitError, match="No remote"):
            push_branch(tmp_path)


class TestCreatePr:
    """Tests for create_pr function."""

    @patch("subprocess.run")
    def test_calls_gh_pr_create(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Calls gh pr create with correct arguments."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="https://github.com/owner/repo/pull/1\n", stderr=""
        )

        result = create_pr(
            title="Test PR",
            body="Test body",
            base="main",  # Provide base to skip get_main_branch_name call
            cwd=tmp_path,
        )

        assert result == "https://github.com/owner/repo/pull/1"
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0][0] == "gh"
        assert call_args[0][0][1] == "pr"
        assert call_args[0][0][2] == "create"

    @patch("subprocess.run")
    def test_raises_on_gh_failure(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Raises GitError when gh command fails."""
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="gh: not logged in"
        )

        with pytest.raises(GitError, match="Failed to create PR"):
            create_pr(title="Test PR", body="Test body", base="main", cwd=tmp_path)

    @patch("subprocess.run")
    def test_raises_on_timeout(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Raises GitError when gh command times out."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="gh", timeout=120)

        with pytest.raises(GitError, match="timed out"):
            create_pr(title="Test PR", body="Test body", base="main", cwd=tmp_path)
