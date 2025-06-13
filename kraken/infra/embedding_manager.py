"""
Kraken Embedding Manager
Encapsula carga y uso eficiente del modelo de embeddings (SentenceTransformers), 
gestión de caché local y control de dispositivo.
"""

from pathlib import Path
from typing import List, Union, Optional, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np
import hashlib
import pickle
import threading
import os

from kraken.core.config import get_config
from kraken.core.utils import clean_text

class EmbeddingManager:
    """
    Carga modelo de embeddings (BERT/SBERT), gestiona caché, y provee encode batch.
    """
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.config = get_config().embedding
        self.model_name = self.config.model_name
        self.device = self.config.device
        self.batch_size = self.config.batch_size
        self._model = None
        self._cache_path = Path(get_config().files.data_dir) / "emb_cache.pkl"
        self._cache = self._load_cache()

    def _load_model(self):
        if self._model is None:
            self._model = SentenceTransformer(self.model_name, device=self.device)
        return self._model

    def encode(self, texts: Union[str, List[str]], normalize: bool = True) -> np.ndarray:
        """
        Obtiene los embeddings de uno o varios textos.
        Usa caché local para acelerar y ahorrar recursos.
        """
        if isinstance(texts, str):
            texts = [texts]
        keys = [self._cache_key(t) for t in texts]
        missing_idx = [i for i, k in enumerate(keys) if k not in self._cache]
        # Embed solo los que faltan
        if missing_idx:
            missing_texts = [texts[i] for i in missing_idx]
            model = self._load_model()
            vectors = model.encode(missing_texts, batch_size=self.batch_size, convert_to_numpy=True, normalize_embeddings=normalize)
            for idx, vec in zip(missing_idx, vectors):
                self._cache[keys[idx]] = vec
            self._save_cache()
        # Armar resultado en orden
        result = np.stack([self._cache[k] for k in keys])
        return result[0] if len(result) == 1 else result

    def _cache_key(self, text: str) -> str:
        # Usa hash del texto limpio para evitar problemas de tamaño o unicidad
        clean = clean_text(text)
        return hashlib.sha256(clean.encode("utf-8")).hexdigest()

    def _load_cache(self) -> Dict[str, Any]:
        if self._cache_path.exists():
            try:
                with open(self._cache_path, "rb") as f:
                    return pickle.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        try:
            with open(self._cache_path, "wb") as f:
                pickle.dump(self._cache, f)
        except Exception:
            pass

    @classmethod
    def get_instance(cls):
        # Singleton para uso thread-safe en toda la app
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

# Shortcut global para obtener el manager singleton
def get_embedding_manager() -> EmbeddingManager:
    return EmbeddingManager.get_instance()
