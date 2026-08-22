"""
GitHub branch and PR service.
"""
from github import Github
from pathlib import Path
from app.config import settings
from app.utils.logger import log_event
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import subprocess
import json


class GitHubBranchService:
    """Service for GitHub branch and PR operations."""

    def __init__(self, db: Session):
        self.db = db
        self.github = Github(settings.github_pat) if settings.github_pat else None
        self.vault_path = Path(settings.vault_path)

    def generate_branch_name(self, workflow_type: str) -> str:
        """Generate branch name following convention."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        return f"fde/{workflow_type}/{timestamp}"

    def check_branch_exists(self, branch_name: str) -> bool:
        """Check if branch already exists in remote."""
        try:
            repo = self.github.get_repo(settings.github_repo_url.split('/')[-1].replace('.git', ''))
            try:
                repo.get_branch(branch_name)
                return True
            except:
                return False
        except Exception as e:
            log_event(self.db, "github.branch_check_failed", {"error": str(e)})
            return False

    def create_branch(self, branch_name: str) -> str:
        """Create a new branch from main."""
        try:
            log_event(self.db, "github.branch_create_started", {"branch": branch_name})

            # Create branch locally
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.vault_path,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(f"Failed to create branch: {result.stderr}")

            log_event(self.db, "github.branch_create_completed", {"branch": branch_name})
            return branch_name

        except Exception as e:
            log_event(self.db, "github.branch_create_failed", {"branch": branch_name, "error": str(e)})
            raise

    def write_draft_to_vault(self, content: str, filename: str) -> str:
        """Write draft content to vault (14 Agent Outputs folder)."""
        try:
            agent_outputs_path = self.vault_path / "14 Agent Outputs"
            agent_outputs_path.mkdir(parents=True, exist_ok=True)

            file_path = agent_outputs_path / filename

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            log_event(self.db, "vault.draft_written", {"path": str(file_path)})
            return str(file_path)

        except Exception as e:
            log_event(self.db, "vault.draft_write_failed", {"error": str(e)})
            raise

    def commit_changes(self, message: str) -> str:
        """Commit changes to current branch."""
        try:
            log_event(self.db, "git.commit_started", {"message": message})

            # Stage changes
            subprocess.run(
                ["git", "add", "."],
                cwd=self.vault_path,
                capture_output=True,
                text=True
            )

            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.vault_path,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(f"Failed to commit: {result.stderr}")

            log_event(self.db, "git.commit_completed", {"message": message})
            return "committed"

        except Exception as e:
            log_event(self.db, "git.commit_failed", {"error": str(e)})
            raise

    def push_branch(self, branch_name: str) -> str:
        """Push branch to remote."""
        try:
            log_event(self.db, "git.push_started", {"branch": branch_name})

            result = subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                cwd=self.vault_path,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(f"Failed to push: {result.stderr}")

            log_event(self.db, "git.push_completed", {"branch": branch_name})
            return "pushed"

        except Exception as e:
            log_event(self.db, "git.push_failed", {"branch": branch_name, "error": str(e)})
            raise

    def create_pull_request(
        self,
        branch_name: str,
        title: str,
        body: str,
        metadata: dict
    ) -> dict:
        """Create pull request with metadata."""
        try:
            log_event(self.db, "github.pr_create_started", {"branch": branch_name})

            repo = self.github.get_repo(settings.github_repo_url.split('/')[-1].replace('.git', ''))

            # Add metadata to PR body
            metadata_json = json.dumps(metadata, indent=2)
            full_body = f"{body}\n\n---\n\n**FDE Metadata:**\n```json\n{metadata_json}\n```"

            pr = repo.create_pull_request(
                title=title,
                body=full_body,
                head=branch_name,
                base="main"
            )

            log_event(self.db, "github.pr_create_completed", {
                "pr_number": pr.number,
                "branch": branch_name
            })

            return {
                "pr_number": pr.number,
                "pr_url": pr.html_url,
                "branch": branch_name
            }

        except Exception as e:
            log_event(self.db, "github.pr_create_failed", {"branch": branch_name, "error": str(e)})
            raise

    def complete_workflow_branch(
        self,
        workflow_type: str,
        content: str,
        title: str,
        metadata: dict
    ) -> dict:
        """Complete full workflow: branch, write, commit, push, PR."""
        try:
            # Generate branch name
            branch_name = self.generate_branch_name(workflow_type)

            # Check for collision
            if self.check_branch_exists(branch_name):
                # Add suffix to avoid collision
                branch_name = f"{branch_name}-{datetime.now(timezone.utc).strftime('%S')}"

            # Switch to main first
            subprocess.run(
                ["git", "checkout", "main"],
                cwd=self.vault_path,
                capture_output=True,
                text=True
            )

            # Pull latest
            subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=self.vault_path,
                capture_output=True,
                text=True
            )

            # Create branch
            self.create_branch(branch_name)

            # Write draft to vault
            filename = f"{workflow_type}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.md"
            file_path = self.write_draft_to_vault(content, filename)

            # Commit changes
            commit_message = f"FDE Workflow: {workflow_type}\n\nGenerated by FDE Vault Agent Platform"
            self.commit_changes(commit_message)

            # Push branch
            self.push_branch(branch_name)

            # Create PR
            pr_body = f"Generated output from {workflow_type} workflow.\n\nFile: {filename}"
            pr_info = self.create_pull_request(branch_name, title, pr_body, metadata)

            # Switch back to main
            subprocess.run(
                ["git", "checkout", "main"],
                cwd=self.vault_path,
                capture_output=True,
                text=True
            )

            return {
                "branch_name": branch_name,
                "file_path": file_path,
                "pr_number": pr_info["pr_number"],
                "pr_url": pr_info["pr_url"]
            }

        except Exception as e:
            log_event(self.db, "workflow.branch_complete_failed", {"error": str(e)})
            raise
