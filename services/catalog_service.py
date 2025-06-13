"""
Servicio de Catálogos Institucionales Kraken
Lógica avanzada para búsqueda, edición, vínculo a CDEs y agrupación de catálogos.
"""

from typing import List, Optional, Dict, Any, Tuple
from kraken.repositories.catalog_repo import catalog_repo
from kraken.repositories.cde_repo import cde_repo
from kraken.core.schemas import CatalogS080
from kraken.core.utils import clean_text, chunk_list

class CatalogService:
    """
    Orquesta operaciones frecuentes sobre catálogos institucionales.
    """
    def __init__(self):
        self.repo = catalog_repo

    def get_by_id(self, catalog_id: int) -> Optional[CatalogS080]:
        return self.repo.get(catalog_id)

    def find_by_schema_and_table(self, schema: str, table: str) -> Optional[CatalogS080]:
        return self.repo.find_by_schema_and_table(schema, table)

    def search(
        self,
        query: str,
        by: str = "desc_raw",
        limit: int = 20,
        fuzzy: bool = True
    ) -> List[CatalogS080]:
        """
        Búsqueda rápida por descripción corta/larga.
        """
        method = self.repo.search_by_desc if by in ("desc_raw", "desc_clean") else None
        if method and fuzzy:
            return method(query, limit=limit)
        else:
            # Búsqueda lineal alternativa
            return [
                cat for cat in self.repo.all()
                if query.lower() in getattr(cat, by, "").lower()
            ][:limit]

    def list_by_cde(self, cde_id: str, limit: int = 100) -> List[CatalogS080]:
        return self.repo.list_by_cde(cde_id, limit=limit)

    def edit_catalog(
        self,
        catalog_id: int,
        updates: Dict[str, Any]
    ) -> Optional[CatalogS080]:
        """
        Edita un catálogo y retorna el registro actualizado.
        Aplica limpieza de texto a los campos relevantes.
        """
        clean_updates = dict(updates)
        if "desc_raw" in clean_updates:
            clean_updates["desc_clean"] = clean_text(clean_updates["desc_raw"])
        return self.repo.update(catalog_id, clean_updates)

    def group_catalogs_by_schema(self) -> Dict[str, List[CatalogS080]]:
        """
        Agrupa catálogos por schema.
        """
        all_cats = self.repo.all()
        grouped = {}
        for cat in all_cats:
            schema = cat.schema or "(Sin schema)"
            grouped.setdefault(schema, []).append(cat)
        return grouped

    def paginate_catalogs(self, page: int = 1, page_size: int = 50) -> List[CatalogS080]:
        """
        Devuelve una página de catálogos (útil para UIs con paginación).
        """
        all_cats = self.repo.all()
        chunks = list(chunk_list(all_cats, page_size))
        if 0 < page <= len(chunks):
            return chunks[page - 1]
        return []

    def link_catalog_to_cde(self, catalog_id: int, cde_id: str) -> Optional[CatalogS080]:
        """
        Actualiza el catálogo para vincularlo a un CDE específico.
        """
        return self.repo.update(catalog_id, {"cde": cde_id})

# Instancia global para acceso fácil
catalog_service = CatalogService()
