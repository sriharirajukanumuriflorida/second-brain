"""
Unit tests for pure utility functions: tag/backlink extraction, path safety,
content hashing, and git branch naming.
"""
from app.utils.validators import (
    extract_tags_from_text,
    extract_backlinks_from_text,
    sanitize_path,
)
from app.services.hash_service import calculate_content_hash
from app.services.scanner_service import ScannerService


class TestTagExtraction:
    def test_extracts_hashtags(self):
        tags = extract_tags_from_text("Some #rag and #llm-engineering notes")
        assert set(tags) == {"rag", "llm-engineering"}

    def test_deduplicates(self):
        assert extract_tags_from_text("#rag #rag #rag") == ["rag"]

    def test_no_tags_returns_empty(self):
        assert extract_tags_from_text("plain text, no tags") == []


class TestBacklinkExtraction:
    def test_extracts_wikilinks(self):
        links = extract_backlinks_from_text("See [[Note A]] and [[Note B]]")
        assert set(links) == {"Note A", "Note B"}

    def test_no_backlinks_returns_empty(self):
        assert extract_backlinks_from_text("no links here") == []


class TestPathSafety:
    def test_sanitize_strips_parent_refs(self):
        assert ".." not in sanitize_path("../../etc/passwd")

    def test_sanitize_normalizes_backslashes(self):
        assert "\\" not in sanitize_path("a\\b\\c")


class TestContentHash:
    def test_deterministic(self):
        assert calculate_content_hash("hello") == calculate_content_hash("hello")

    def test_differs_on_change(self):
        assert calculate_content_hash("hello") != calculate_content_hash("world")


class TestBranchNaming:
    def test_branch_name_format(self, db_session):
        """Current format is fde/{workflow}/{yyyyMMdd-HHmmss}.

        NOTE: the implementation plan specifies
        agent-output/{workflow}/{ts}-{short_run_id} with a run id for collision
        safety; the code currently omits the run id. This test pins the ACTUAL
        behavior so a future fix to match the plan is a deliberate change.
        """
        from app.services.github_branch_service import GitHubBranchService
        svc = GitHubBranchService(db_session)
        name = svc.generate_branch_name("grill-me")
        assert name.startswith("fde/grill-me/")
        # timestamp segment is 8+1+6 chars: yyyyMMdd-HHmmss
        ts = name.rsplit("/", 1)[1]
        assert len(ts) == 15 and ts[8] == "-"


class TestScannerService:
    def test_scans_only_note_folders(self, tmp_path):
        vault = tmp_path
        (vault / "02 Literature Notes").mkdir()
        (vault / "backend").mkdir()
        (vault / "frontend").mkdir()
        (vault / "14 Agent Outputs").mkdir()
        (vault / "02 Literature Notes" / "note.md").write_text("# Note", encoding="utf-8")
        (vault / "backend" / "README.md").write_text("# Backend", encoding="utf-8")
        (vault / "frontend" / "README.md").write_text("# Frontend", encoding="utf-8")
        (vault / "14 Agent Outputs" / "note.md").write_text("# Agent Output", encoding="utf-8")
        (vault / "README.md").write_text("# Root", encoding="utf-8")

        files = list(ScannerService(vault).scan_markdown_files())
        assert [p.relative_to(vault).as_posix() for p in files] == [
            "02 Literature Notes/note.md"
        ]
