#!/usr/bin/env python3
"""
Vault Folder Setup Script

Creates FDE-specific folders in the Obsidian vault if they don't exist.
This script is idempotent - it can be run multiple times safely.

Usage:
    python scripts/setup_vault_folders.py
"""

import os
from pathlib import Path

# FDE folders to create
FDE_FOLDERS = [
    "10 FDE Playbooks",
    "11 Architecture Decisions",
    "12 Solution Patterns",
    "13 Governance",
    "14 Agent Outputs",
]

# Descriptions for each folder
FOLDER_DESCRIPTIONS = {
    "10 FDE Playbooks": "Operational playbooks for common workflows and procedures.",
    "11 Architecture Decisions": "Architecture Decision Records (ADRs) for the platform.",
    "12 Solution Patterns": "Reusable solution patterns for common problems.",
    "13 Governance": "Policies, procedures, and controls for platform operation.",
    "14 Agent Outputs": "AI-generated outputs (ONLY folder where MVP may write).",
}


def create_folder_with_gitkeep(folder_path: Path, description: str) -> bool:
    """Create a folder with a .gitkeep file containing a description."""
    try:
        folder_path.mkdir(parents=True, exist_ok=True)
        gitkeep_path = folder_path / ".gitkeep"

        if not gitkeep_path.exists():
            gitkeep_path.write_text(f"# {folder_path.name}\n\n{description}\n")
            print(f"  Created: {folder_path}")
            return True
        else:
            print(f"  Skipped (exists): {folder_path}")
            return False
    except Exception as e:
        print(f"  Error creating {folder_path}: {e}")
        return False


def main():
    """Main function to set up vault folders."""
    # Get vault root (assumes script is in vault/scripts/)
    vault_root = Path(__file__).parent.parent

    print(f"Vault root: {vault_root}")
    print("Setting up FDE folders...\n")

    created_count = 0
    skipped_count = 0

    for folder_name in FDE_FOLDERS:
        folder_path = vault_root / folder_name
        description = FOLDER_DESCRIPTIONS.get(folder_name, "")

        if create_folder_with_gitkeep(folder_path, description):
            created_count += 1
        else:
            skipped_count += 1

    print(f"\nSummary:")
    print(f"  Created: {created_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Total: {len(FDE_FOLDERS)}")


if __name__ == "__main__":
    main()
