"""Utilities for updating the project from GitHub."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def get_repo_root() -> Path:
    """Return the repository root directory."""
    return Path(__file__).resolve().parents[2]


def _run_command(command: list[str], cwd: Path) -> tuple[int, str]:
    """Run a command and capture its combined output."""
    result = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        shell=False,
        check=False,
    )
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode, output.strip()


def update_system_from_github(repo_root: Path | str | None = None) -> dict[str, str | bool]:
    """Pull the latest code from GitHub and refresh Python dependencies."""
    root = Path(repo_root) if repo_root is not None else get_repo_root()

    git_dir = root / ".git"
    requirements_file = root / "requirements.txt"

    if not git_dir.exists():
        return {
            "success": False,
            "message": "This folder is not a Git repository.",
            "details": f"Missing: {git_dir}",
        }

    status_code, status_output = _run_command(["git", "status", "--porcelain"], root)
    if status_code != 0:
        return {
            "success": False,
            "message": "Unable to inspect repository status.",
            "details": status_output or "git status failed",
        }

    if status_output:
        return {
            "success": False,
            "message": "Please commit or stash local changes before updating.",
            "details": status_output,
        }

    pull_code, pull_output = _run_command(["git", "pull", "--ff-only", "origin", "main"], root)
    if pull_code != 0:
        return {
            "success": False,
            "message": "Git pull failed.",
            "details": pull_output or "git pull returned a non-zero exit code",
        }

    if requirements_file.exists():
        pip_code, pip_output = _run_command([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], root)
        if pip_code != 0:
            return {
                "success": False,
                "message": "Code updated, but dependency installation failed.",
                "details": pip_output or "pip install returned a non-zero exit code",
            }

    return {
        "success": True,
        "message": "System updated successfully from GitHub.",
        "details": pull_output or "Repository pulled successfully.",
    }