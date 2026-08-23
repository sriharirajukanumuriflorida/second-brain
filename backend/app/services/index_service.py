"""
Metadata index service.
"""
from sqlalchemy.orm import Session
from app.models import Note, SyncEvent
from app.services.parser_service import parse_markdown_with_frontmatter, extract_frontmatter_yaml
from app.services.hash_service import calculate_file_hash, calculate_content_hash
from app.services.extractor_service import extract_tags, extract_backlinks, extract_folder_from_path
from app.services.scanner_service import ScannerService
from pathlib import Path
from typing import List
from datetime import datetime
import json


class IndexService:
    """Service for indexing vault metadata."""

    def __init__(self, db: Session, vault_path: Path):
        self.db = db
        self.vault_path = vault_path
        self.scanner = ScannerService(vault_path)

    def index_vault(self) -> dict:
        """Index all markdown files in vault."""
        stats = {
            "processed": 0,
            "indexed": 0,
            "updated": 0,
            "skipped": 0
        }

        for file_path in self.scanner.scan_markdown_files():
            stats["processed"] += 1
            relative_path = self.scanner.get_relative_path(file_path)

            try:
                # Parse markdown
                parsed = parse_markdown_with_frontmatter(str(file_path))
                content = parsed["content"]
                frontmatter = parsed["frontmatter"]

                # Calculate hashes
                file_hash = calculate_file_hash(file_path)
                content_hash = calculate_content_hash(content)
                frontmatter_hash = calculate_content_hash(
                    extract_frontmatter_yaml(frontmatter)
                )

                # Extract metadata
                title = self.scanner.extract_title_from_content(content)
                tags = extract_tags(content, frontmatter.get("tags", []))
                backlinks = extract_backlinks(content)
                folder = extract_folder_from_path(relative_path)

                # Check if note exists
                existing_note = self.db.query(Note).filter(
                    Note.path == relative_path
                ).first()

                if existing_note:
                    # Check if content changed
                    if existing_note.content_hash == content_hash:
                        stats["skipped"] += 1
                        continue

                    # Update existing note
                    existing_note.title = title
                    existing_note.file_hash = file_hash
                    existing_note.content_hash = content_hash
                    existing_note.frontmatter_hash = frontmatter_hash
                    existing_note.tags = json.dumps(tags)
                    existing_note.backlinks = json.dumps(backlinks)
                    existing_note.frontmatter = extract_frontmatter_yaml(frontmatter)
                    existing_note.last_indexed_at = datetime.utcnow()
                    stats["updated"] += 1
                else:
                    # Create new note
                    note = Note(
                        path=relative_path,
                        title=title,
                        file_hash=file_hash,
                        content_hash=content_hash,
                        frontmatter_hash=frontmatter_hash,
                        tags=json.dumps(tags),
                        backlinks=json.dumps(backlinks),
                        frontmatter=extract_frontmatter_yaml(frontmatter),
                        folder=folder
                    )
                    self.db.add(note)
                    stats["indexed"] += 1

            except Exception as e:
                print(f"Error indexing {relative_path}: {e}")
                continue

        self.db.commit()
        return stats
