"""Git operations for wiggum."""

import subprocess
from pathlib import Path
from typing import Optional


class GitError(Exception):
    """Raised when a git operation fails."""

    pass


def _run_git(
    args: list[str], cwd: Optional[Path] = None, check: bool = True
) -> subprocess.CompletedProcess[str]:
    """Run a git command.

    Args:
        args: Git command arguments (without 'git' prefix).
        cwd: Working directory. Defaults to current directory.
        check: Whether to raise GitError on non-zero exit code.

    Returns:
        CompletedProcess result.

    Raises:
        GitError: If check=True and command fails.
    """
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise GitError(f"Git command failed: git {' '.join(args)}\n{result.stderr}")
    return result


def is_git_repo(cwd: Optional[Path] = None) -> bool:
    """Check if the current directory is a git repository.

    Args:
        cwd: Working directory to check.

    Returns:
        True if in a git repository, False otherwise.
    """
    result = _run_git(["rev-parse", "--git-dir"], cwd=cwd, check=False)
    return result.returncode == 0


def get_main_branch_name(cwd: Optional[Path] = None) -> str:
    """Detect the main branch name (main or master).

    Args:
        cwd: Working directory.

    Returns:
        The name of the main branch ('main' or 'master').

    Raises:
        GitError: If neither 'main' nor 'master' branch exists.
    """
    # Check if 'main' branch exists
    result = _run_git(["rev-parse", "--verify", "main"], cwd=cwd, check=False)
    if result.returncode == 0:
        return "main"

    # Check if 'master' branch exists
    result = _run_git(["rev-parse", "--verify", "master"], cwd=cwd, check=False)
    if result.returncode == 0:
        return "master"

    raise GitError("Could not detect main branch (neither 'main' nor 'master' exists)")


def get_current_branch(cwd: Optional[Path] = None) -> str:
    """Get the current branch name.

    Args:
        cwd: Working directory.

    Returns:
        The current branch name.

    Raises:
        GitError: If not in a git repository or in detached HEAD state.
    """
    result = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)
    return result.stdout.strip()


def has_remote(cwd: Optional[Path] = None) -> bool:
    """Check if the repository has a remote configured.

    Args:
        cwd: Working directory.

    Returns:
        True if a remote is configured, False otherwise.
    """
    result = _run_git(["remote"], cwd=cwd, check=False)
    return bool(result.stdout.strip())


def create_branch(branch_name: str, cwd: Optional[Path] = None) -> None:
    """Create and switch to a new branch.

    Args:
        branch_name: Name of the branch to create.
        cwd: Working directory.

    Raises:
        GitError: If branch already exists or other git error.
    """
    # Check if branch already exists
    result = _run_git(["rev-parse", "--verify", branch_name], cwd=cwd, check=False)
    if result.returncode == 0:
        raise GitError(f"Branch '{branch_name}' already exists")

    _run_git(["checkout", "-b", branch_name], cwd=cwd)


def fetch_and_merge_main(cwd: Optional[Path] = None) -> bool:
    """Fetch from origin and merge main branch.

    Args:
        cwd: Working directory.

    Returns:
        True if fetch/merge was performed, False if skipped (no remote).

    Raises:
        GitError: If fetch or merge fails.
    """
    if not has_remote(cwd):
        return False

    main_branch = get_main_branch_name(cwd)

    # Fetch from origin
    _run_git(["fetch", "origin", main_branch], cwd=cwd)

    # Merge origin/main into current branch
    _run_git(["merge", f"origin/{main_branch}", "--no-edit"], cwd=cwd)

    return True


def push_branch(cwd: Optional[Path] = None, set_upstream: bool = True) -> None:
    """Push the current branch to origin.

    Args:
        cwd: Working directory.
        set_upstream: Whether to set upstream tracking.

    Raises:
        GitError: If push fails or no remote configured.
    """
    if not has_remote(cwd):
        raise GitError("No remote configured. Cannot push.")

    current_branch = get_current_branch(cwd)
    args = ["push"]
    if set_upstream:
        args.extend(["-u", "origin", current_branch])
    else:
        args.extend(["origin", current_branch])

    _run_git(args, cwd=cwd)


def create_pr(
    title: str,
    body: str,
    cwd: Optional[Path] = None,
    base: Optional[str] = None,
) -> str:
    """Create a pull request using the GitHub CLI.

    Args:
        title: PR title.
        body: PR body.
        cwd: Working directory.
        base: Base branch (default: auto-detect main/master).

    Returns:
        The URL of the created PR.

    Raises:
        GitError: If PR creation fails.
    """
    if base is None:
        base = get_main_branch_name(cwd)

    args = ["gh", "pr", "create", "--title", title, "--body", body, "--base", base]

    result = subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise GitError(f"Failed to create PR: {result.stderr}")

    return result.stdout.strip()


def generate_branch_name(prefix: str = "wiggum") -> str:
    """Generate a unique branch name based on timestamp.

    Args:
        prefix: Prefix for the branch name.

    Returns:
        A branch name like 'wiggum/2024-01-15-143022'.
    """
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    return f"{prefix}/{timestamp}"
