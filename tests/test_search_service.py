import sys
import types
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Stub modules required by search_service before importing it
clean_utils = types.ModuleType("kraken.core.utils")
clean_utils.clean_text = lambda text: text
sys.modules["kraken.core.utils"] = clean_utils

config_mod = types.ModuleType("kraken.core.config")
# placeholder, monkeypatched in tests
config_mod.get_config = lambda: None
sys.modules["kraken.core.config"] = config_mod

# Stub rapidfuzz to avoid dependency during tests
rf_mod = types.ModuleType("rapidfuzz")
rf_mod.process = types.SimpleNamespace(extract=lambda *a, **k: [])
rf_mod.fuzz = types.SimpleNamespace(WRatio=lambda *a, **k: 0)
sys.modules["rapidfuzz"] = rf_mod

faiss_mod = types.ModuleType("kraken.infra.faiss_manager")
faiss_mod.get_faiss_manager = lambda name: types.SimpleNamespace(search=lambda q, top_k: [])
sys.modules["kraken.infra.faiss_manager"] = faiss_mod

for repo in ["attribute_repo", "cde_repo", "catalog_repo"]:
    mod = types.ModuleType(f"kraken.repositories.{repo}")
    mod.__dict__[repo] = types.SimpleNamespace(all=lambda: [])
    sys.modules[f"kraken.repositories.{repo}"] = mod

spec = importlib.util.spec_from_file_location(
    "search_service", ROOT / "kraken" / "services" / "search_service.py"
)
search_service = importlib.util.module_from_spec(spec)
spec.loader.exec_module(search_service)


def test_search_cdes_default_similarity(monkeypatch):
    class Dummy:
        pass

    cfg = Dummy()
    cfg.cde = Dummy()
    cfg.cde.default_limit = 5
    # similarity_threshold intentionally absent
    cfg.duplicates = Dummy()
    cfg.duplicates.name_similarity_threshold = 80

    monkeypatch.setattr(search_service, "get_config", lambda: cfg)

    class Repo:
        def all(self):
            return [types.SimpleNamespace(cde_id=1, biz_term="b", desc_raw="d")]
    monkeypatch.setattr(search_service, "cde_repo", Repo())

    captured = {}

    def fake_semantic_search(q, idx, id_map, top_k=10, threshold=0.0):
        captured["threshold"] = threshold
        return []

    monkeypatch.setattr(search_service, "semantic_search", fake_semantic_search)

    search_service.search_cdes("term", mode="semantic")
    assert captured["threshold"] == 0.65
