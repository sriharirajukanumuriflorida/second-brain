"""
GitHub repository sync/clone service.
"""
from github import Github
from pathlib import Path
from app.config import settings
from app.utils.logger import log_event
from sqlalchemy.orm import Session
import subprocess
import shutil


class GitHubService:
    """Service for GitHub repository operations."""

    def __init__(self, db: Session):
        self.db = db
        self.github = Github(settings.github_pat) if settings.github_pat else None

    def clone_or_fetch_repo(self, force: bool = False) -> str:
        """Clone or fetch the GitHub repository."""
        vault_path = settings.vault_path_resolved

        if vault_path.exists() and not force:
            # Repository exists, fetch latest
            log_event(self.db, "vault.fetch_started", {"path": str(vault_path)})
            result = subprocess.run(
                ["git", "fetch", "origin"],
                cwd=vault_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                log_event(self.db, "vault.fetch_completed", {"path": str(vault_path)})
                return str(vault_path)
            else:
                log_event(self.db, "vault.fetch_failed", {"error": result.stderr})
                raise Exception(f"Git fetch failed: {result.stderr}")
        else:
            # Clone repository
            if vault_path.exists():
                shutil.rmtree(vault_path)

            log_event(self.db, "vault.clone_started", {
                "repo_url": settings.github_repo_url,
                "path": str(vault_path)
            })

            result = subprocess.run(
                ["git", "clone", settings.github_repo_url, str(vault_path)],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                log_event(self.db, "vault.clone_completed", {"path": str(vault_path)})
                return str(vault_path)
            else:
                log_event(self.db, "vault.clone_failed", {"error": result.stderr})
                raise Exception(f"Git clone failed: {result.stderr}")

    def pull_latest(self) -> str:
        """Pull latest changes from main branch."""
        vault_path = settings.vault_path_resolved
        log_event(self.db, "vault.pull_started", {"path": str(vault_path)})

        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd=vault_path,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            log_event(self.db, "vault.pull_completed", {"path": str(vault_path)})
            return str(vault_path)
        else:
            log_event(self.db, "vault.pull_failed", {"error": result.stderr})
            raise RuntimeError(f"Git pull failed: {result.stderr}")
