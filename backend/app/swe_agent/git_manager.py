"""
Safe Git Integration Manager (Sprint 8 Step 11).
Handles status, diff, branch, commit, checkout, stash, tag, and merge preparation.
Never executes force push (git push -f).
"""

import subprocess
from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger(__name__)


class GitManager:
    """Safe Git integration manager."""

    @classmethod
    def get_status(cls, repo_path: str = ".") -> Dict[str, Any]:
        """Returns git status output."""
        res = subprocess.run("git status --porcelain", shell=True, cwd=repo_path, capture_output=True, text=True)
        return {
            "status": "CLEAN" if not res.stdout.strip() else "DIRTY",
            "modified_files": res.stdout.splitlines()
        }

    @classmethod
    def get_diff(cls, file_path: Optional[str] = None, repo_path: str = ".") -> str:
        """Returns git diff output."""
        cmd = f"git diff {file_path}" if file_path else "git diff"
        res = subprocess.run(cmd, shell=True, cwd=repo_path, capture_output=True, text=True)
        return res.stdout or "No changes in working directory."

    @classmethod
    def list_branches(cls, repo_path: str = ".") -> Dict[str, Any]:
        """Lists local git branches."""
        res = subprocess.run("git branch", shell=True, cwd=repo_path, capture_output=True, text=True)
        branches = [b.strip() for b in res.stdout.splitlines()]
        current = next((b.lstrip("* ").strip() for b in branches if b.startswith("*")), "main")
        return {"current_branch": current, "branches": branches}

    @classmethod
    def commit_changes(cls, commit_message: str, repo_path: str = ".") -> Dict[str, Any]:
        """Stages changes and commits with message."""
        add_res = subprocess.run("git add .", shell=True, cwd=repo_path, capture_output=True, text=True)
        commit_cmd = f'git commit -m "{commit_message}"'
        commit_res = subprocess.run(commit_cmd, shell=True, cwd=repo_path, capture_output=True, text=True)

        return {
            "commit_message": commit_message,
            "success": commit_res.returncode == 0,
            "stdout": commit_res.stdout,
            "stderr": commit_res.stderr
        }

    @classmethod
    def create_branch(cls, branch_name: str, repo_path: str = ".") -> Dict[str, Any]:
        """Creates and checks out new feature branch."""
        res = subprocess.run(f"git checkout -b {branch_name}", shell=True, cwd=repo_path, capture_output=True, text=True)
        return {"branch_name": branch_name, "success": res.returncode == 0, "output": res.stdout or res.stderr}

    @classmethod
    def stash(cls, repo_path: str = ".") -> Dict[str, Any]:
        """Stashes working directory changes."""
        res = subprocess.run("git stash", shell=True, cwd=repo_path, capture_output=True, text=True)
        return {"output": res.stdout, "success": res.returncode == 0}


git_manager = GitManager()
