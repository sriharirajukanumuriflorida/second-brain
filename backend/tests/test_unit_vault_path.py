"""
Unit tests for vault_path_resolved (absolute anchoring) — the fix for the
relative 'vault_clone/...' reads that failed with No such file or directory.
"""
from pathlib import Path

from app.config import Settings


def test_relative_vault_path_anchored_to_backend_dir():
    """A relative VAULT_PATH resolves to an absolute path under backend/."""
    s = Settings(vault_path=Path("./vault_clone"))
    resolved = s.vault_path_resolved
    assert resolved.is_absolute()
    assert resolved.name == "vault_clone"
    # Anchored to the backend dir (parent of the app package), not the CWD.
    backend_dir = Path(__file__).resolve().parent.parent
    assert resolved == (backend_dir / "vault_clone").resolve()


def test_absolute_vault_path_respected(tmp_path):
    """An absolute VAULT_PATH is returned unchanged."""
    s = Settings(vault_path=tmp_path)
    assert s.vault_path_resolved == tmp_path
    assert s.vault_path_resolved.is_absolute()


def test_resolved_is_stable_regardless_of_cwd(monkeypatch, tmp_path):
    """Resolution must not depend on the process working directory."""
    s = Settings(vault_path=Path("./vault_clone"))
    before = s.vault_path_resolved
    monkeypatch.chdir(tmp_path)
    after = s.vault_path_resolved
    assert before == after
