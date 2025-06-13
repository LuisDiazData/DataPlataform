import sys
import types
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Stub modules required by cde_service before importing it
clean_mod = types.ModuleType("kraken.core.utils")
clean_mod.clean_text = lambda text: f"clean:{text}" if text is not None else ""
clean_mod.chunk_list = lambda lst, size: []
sys.modules["kraken.core.utils"] = clean_mod

schemas_mod = types.ModuleType("kraken.core.schemas")
schemas_mod.CDE = type("CDE", (), {})
sys.modules["kraken.core.schemas"] = schemas_mod

qual_mod = types.ModuleType("kraken.repositories.quality_rules_repo")
qual_mod.quality_rules_repo = None
sys.modules["kraken.repositories.quality_rules_repo"] = qual_mod

repo_stub = types.SimpleNamespace(find_by_cde_id=lambda cid: None, update=lambda *a, **k: None)
repo_mod = types.ModuleType("kraken.repositories.cde_repo")
repo_mod.cde_repo = repo_stub
sys.modules["kraken.repositories.cde_repo"] = repo_mod

spec = importlib.util.spec_from_file_location("cde_service", ROOT / "services" / "cde_service.py")
cde_service = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cde_service)


def test_edit_cde_updates_row(monkeypatch):
    class Repo:
        def __init__(self):
            self.row = types.SimpleNamespace(id=5, cde_id="X", desc_raw="old")
        def find_by_cde_id(self, cid):
            assert cid == "X"
            return self.row
        def update(self, db_id, updates):
            assert db_id == self.row.id
            for k, v in updates.items():
                setattr(self.row, k, v)
            return self.row

    repo = Repo()
    service = cde_service.CDEService()
    monkeypatch.setattr(service, "repo", repo)

    result = service.edit_cde("X", {"desc_raw": "new"})
    assert result.desc_raw == "new"
    assert repo.row.desc_raw == "new"
