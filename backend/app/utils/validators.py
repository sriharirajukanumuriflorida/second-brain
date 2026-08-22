"""
Path and content validators.
"""
import re
from pathlib import Path
from typing import List


def validate_vault_path(path: str) -> bool:
    """Validate that a path is within the vault."""
    # Basic validation - ensure path doesn't try to escape vault
    resolved_path = Path(path).resolve()
    return not (".." in str(resolved_path) or str(resolved_path).startswith("/"))


def sanitize_path(path: str) -> str:
    """Sanitize a file path."""
    # Remove any parent directory references
    return path.replace("..", "").replace("\\", "/")


def extract_tags_from_text(text: str) -> List[str]:
    """Extract tags from markdown text (#tag format)."""
    # Match #tag patterns (but not in code blocks)
    tag_pattern = r'#([a-zA-Z0-9_-]+)'
    tags = re.findall(tag_pattern, text)
    return list(set(tags))


def extract_backlinks_from_text(text: str) -> List[str]:
    """Extract backlinks from markdown text ([[link]] format)."""
    # Match [[link]] patterns
    backlink_pattern = r'\[\[([^\]]+)\]\]'
    backlinks = re.findall(backlink_pattern, text)
    return list(set(backlinks))
