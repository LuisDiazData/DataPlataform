"""
Kraken Config Loader (v2)
Carga y valida settings.yaml centralizado para toda la app.
Permite recarga dinámica y selección de perfil (dev/prod).
"""

from pathlib import Path
from typing import Optional, Any, Dict
import yaml
import threading
from pydantic import BaseModel, ValidationError, Field

SETTINGS_PATH = Path(__file__).parent / "settings.yaml"
_CONFIG_LOCK = threading.Lock()
_CONFIG_CACHE: Dict[str, Any] = {}

class EmbeddingSettings(BaseModel):
    model_name: str = Field(..., description="Nombre del modelo de embeddings")
    device: str = "cpu"
    batch_size: int = 64

class FAISSSettings(BaseModel):
    index_type: str = "FlatIP"
    dir: str = "data/faiss_indices"
    cache_size: int = 10000

class FileSettings(BaseModel):
    data_dir: str = "data/"
    catalogs_dir: str = "data/catalogs/"
    faiss_dir: str = "data/faiss_indices/"
    models_dir: str = "data/models/"
    logs_dir: str = "logs/"

class AttributeSettings(BaseModel):
    technical: Dict[str, Any] = Field(default_factory=dict)
    semantic: Dict[str, Any] = Field(default_factory=dict)

class CDESettings(BaseModel):
    default_limit: int = 10
    model_name: str = "mpne"

class CatalogSettings(BaseModel):
    default_limit: int = 10
    similarity_threshold: float = 0.65

class DuplicatesSettings(BaseModel):
    name_similarity_threshold: int = 80
    desc_similarity_threshold: float = 0.7
    max_pairs: int = 100
    export_path: str = "data/duplicates.csv"

class InfraSettings(BaseModel):
    auto_reindex_on_catalog_change: bool = False
    enable_ingestion_logging: bool = True
    ingestion_log_retention_days: int = 180
    watcher_debounce_ms: int = 2000

class UISettings(BaseModel):
    max_results_display: int = 20
    enable_dark_mode: bool = True
    feedback_enabled: bool = True

class KrakenConfig(BaseModel):
    version: str
    profile: str = "prod"
    embedding: EmbeddingSettings
    faiss: FAISSSettings
    files: FileSettings
    attributes: AttributeSettings
    cde: CDESettings
    catalogs: CatalogSettings
    duplicates: DuplicatesSettings
    infra: InfraSettings
    ui: UISettings

def get_config(force_reload: bool = False) -> KrakenConfig:
    """
    Carga y retorna la configuración global validada.
    Usa caché thread-safe para eficiencia.
    """
    with _CONFIG_LOCK:
        global _CONFIG_CACHE
        if not _CONFIG_CACHE or force_reload:
            try:
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    raw = yaml.safe_load(f)
                config = KrakenConfig(**raw)
                _CONFIG_CACHE.clear()
                _CONFIG_CACHE["config"] = config
            except FileNotFoundError:
                raise RuntimeError(f"Archivo de configuración no encontrado: {SETTINGS_PATH}")
            except ValidationError as ve:
                raise RuntimeError(f"Error de validación en settings.yaml: {ve}")
            except Exception as e:
                raise RuntimeError(f"Error cargando settings.yaml: {e}")
        return _CONFIG_CACHE["config"]

# Acceso rápido (opcional, pero no recomendado en código productivo)
CONFIG = get_config()

