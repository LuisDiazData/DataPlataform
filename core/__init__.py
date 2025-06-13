# kraken/core/__init__.py

"""
Kraken Core - Initialization
Exposes version, configuration loader and key base modules.
"""

from .config import get_config, KrakenConfig
from .schemas import (
    Attribute,
    CDE,
    CatalogS080,
    QualityRule,
    Feedback,
    DuplicateHistory,
)
from .utils import clean_text, chunk_list

# Opcional: Exponer versión del paquete
try:
    from importlib.metadata import version, PackageNotFoundError
    __version__ = version("kraken")
except Exception:
    __version__ = "2.0.0-dev"

__all__ = [
    "get_config",
    "KrakenConfig",
    "Attribute",
    "CDE",
    "CatalogS080",
    "QualityRule",
    "Feedback",
    "DuplicateHistory",
    "clean_text",
    "chunk_list",
    "__version__",
]

