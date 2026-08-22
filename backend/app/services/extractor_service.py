"""
Tag and backlink extractor service.
"""
from app.utils.validators import extract_tags_from_text, extract_backlinks_from_text
from typing import List


def extract_tags(content: str, frontmatter_tags: List[str] = None) -> List[str]:
    """Extract tags from content and frontmatter."""
    content_tags = extract_tags_from_text(content)
    all_tags = set(content_tags)
    if frontmatter_tags:
        all_tags.update(frontmatter_tags)
    return list(all_tags)


def extract_backlinks(content: str) -> List[str]:
    """Extract backlinks from content."""
    return extract_backlinks_from_text(content)


def extract_folder_from_path(path: str) -> str:
    """Extract folder name from file path."""
    parts = path.split("/")
    if len(parts) > 1:
        return parts[0]
    return ""
