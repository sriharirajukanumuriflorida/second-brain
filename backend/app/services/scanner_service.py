"""
Markdown file scanner service.
"""
from pathlib import Path
from typing import Generator


class ScannerService:
    """Service for scanning vault for markdown files."""
    EXCLUDED_TOP_LEVEL_FOLDERS = {"14 Agent Outputs"}

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path

    def scan_markdown_files(self) -> Generator[Path, None, None]:
        """Scan vault for markdown files."""
        for file_path in self.vault_path.rglob("*.md"):
            relative_path = file_path.relative_to(self.vault_path)
            root_folder = relative_path.parts[0] if relative_path.parts else ""
            # Skip hidden files and .obsidian folder
            if (
                ".obsidian" in str(file_path) or
                file_path.name.startswith(".") or
                "99 Archive" in str(file_path) or
                not root_folder[:1].isdigit() or
                root_folder in self.EXCLUDED_TOP_LEVEL_FOLDERS
            ):
                continue
            yield file_path

    def get_relative_path(self, file_path: Path) -> str:
        """Get relative path from vault root."""
        return str(file_path.relative_to(self.vault_path)).replace("\\", "/")

    def extract_title_from_content(self, content: str) -> str:
        """Extract title from markdown content (first heading)."""
        lines = content.split("\n")
        for line in lines:
            if line.startswith("# "):
                return line[2:].strip()
        # Fallback to filename
        return "Untitled"
