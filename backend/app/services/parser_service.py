"""
YAML front matter parser service.
"""
import frontmatter
from typing import Dict, Any, Optional


def parse_markdown_with_frontmatter(file_path: str) -> Dict[str, Any]:
    """Parse markdown file with YAML front matter."""
    with open(file_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)

    return {
        "frontmatter": post.metadata,
        "content": post.content,
        "raw": post.content
    }


def extract_frontmatter_yaml(frontmatter: Dict[str, Any]) -> str:
    """Convert frontmatter dict to YAML string."""
    import yaml
    return yaml.dump(frontmatter, default_flow_style=False)
