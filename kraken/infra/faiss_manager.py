"""
Kraken FAISS Manager
Gestiona la construcción, consulta, persistencia y recarga de índices FAISS para búsquedas semánticas rápidas.
Soporta incremental, versionado, y múltiples tipos de índice.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import faiss
import numpy as np
import json
import threading
import hashlib

from kraken.core.config import get_config
from kraken.infra.embedding_manager import get_embedding_manager

class FAISSIndexManager:
    _instances: Dict[str, "FAISSIndexManager"] = {}
    _lock = threading.Lock()

    def __init__(self, index_name: str):
        self.config = get_config().faiss
        self.index_name = index_name
        self.index_dir = Path(self.config.dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.index_dir / f"{index_name}.index"
        self.ids_path = self.index_dir / f"{index_name}.ids"
        self.meta_path = self.index_dir / f"{index_name}.meta.json"
        self.index: Optional[faiss.Index] = None
        self.ids: List[str] = []
        self.embedding_dim: int = -1
        self._load_index()

    def _meta(self) -> Dict[str, Any]:
        return {
            "index_name": self.index_name,
            "embedding_dim": self.embedding_dim,
            "faiss_version": faiss.__version__,
            "built_at": "",
        }

    def build_index(self, texts: List[str], ids: List[str], force: bool = False) -> bool:
        """
        Construye y persiste el índice FAISS para los textos e ids dados.
        Si ya existe y no force, no lo reconstruye.
        """
        if self.index_path.exists() and not force:
            print(f"Índice '{self.index_name}' ya existe. Usa force=True para reconstruir.")
            self._load_index()
            return True
        if not texts or not ids or len(texts) != len(ids):
            print(f"Textos o IDs inválidos para construir el índice '{self.index_name}'.")
            return False

        embedder = get_embedding_manager()
        embeddings = embedder.encode(texts)
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)
        self.embedding_dim = embeddings.shape[1]
        # Index FlatIP por defecto, configurable
        if self.config.index_type.upper() == "FLATIP":
            index = faiss.IndexFlatIP(self.embedding_dim)
        elif self.config.index_type.upper() == "HNSW":
            index = faiss.IndexHNSWFlat(self.embedding_dim, 32)
        else:
            raise ValueError(f"Tipo de índice FAISS no soportado: {self.config.index_type}")
        # Normalizar si es IP
        faiss.normalize_L2(embeddings)
        index.add(embeddings)
        self.index = index
        self.ids = list(ids)
        # Guardar
        faiss.write_index(index, str(self.index_path))
        with open(self.ids_path, "w", encoding="utf-8") as f:
            json.dump(self.ids, f)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            meta = self._meta()
            meta["built_at"] = __import__("datetime").datetime.utcnow().isoformat()
            json.dump(meta, f)
        print(f"Índice '{self.index_name}' construido y guardado ({len(ids)} vectores).")
        return True

    def _load_index(self):
        if self.index_path.exists() and self.ids_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            with open(self.ids_path, "r", encoding="utf-8") as f:
                self.ids = json.load(f)
            self.embedding_dim = self.index.d
        else:
            self.index = None
            self.ids = []
            self.embedding_dim = -1

    def add_to_index(self, new_texts: List[str], new_ids: List[str]):
        """
        Añade nuevos embeddings e IDs al índice ya existente (incremental).
        """
        if not self.index:
            raise RuntimeError("Índice no cargado. Construya o cargue primero.")
        embedder = get_embedding_manager()
        vectors = embedder.encode(new_texts)
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        faiss.normalize_L2(vectors)
        self.index.add(vectors)
        self.ids.extend(new_ids)
        faiss.write_index(self.index, str(self.index_path))
        with open(self.ids_path, "w", encoding="utf-8") as f:
            json.dump(self.ids, f)

    def search(self, query: Union[str, List[str]], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Busca los textos/IDs más similares a la query.
        Devuelve lista de dicts: id, score, idx.
        """
        if self.index is None or not self.ids:
            self._load_index()
        if self.index is None or not self.ids:
            return []
        embedder = get_embedding_manager()
        queries = [query] if isinstance(query, str) else query
        q_vecs = embedder.encode(queries)
        if q_vecs.ndim == 1:
            q_vecs = q_vecs.reshape(1, -1)
        faiss.normalize_L2(q_vecs)
        scores, idxs = self.index.search(q_vecs, top_k)
        results = []
        for i, (s_row, id_row) in enumerate(zip(scores, idxs)):
            query_results = []
            for score, idx in zip(s_row, id_row):
                if idx >= 0 and idx < len(self.ids):
                    query_results.append({
                        "id": self.ids[idx],
                        "score": float(score),
                        "idx": idx,
                    })
            results.append(query_results)
        # Si fue un solo query, regresar la lista interna
        return results[0] if len(results) == 1 else results

    @classmethod
    def get_manager(cls, index_name: str) -> "FAISSIndexManager":
        with cls._lock:
            if index_name not in cls._instances:
                cls._instances[index_name] = FAISSIndexManager(index_name)
            return cls._instances[index_name]

# Shortcut global
def get_faiss_manager(index_name: str) -> FAISSIndexManager:
    return FAISSIndexManager.get_manager(index_name)
