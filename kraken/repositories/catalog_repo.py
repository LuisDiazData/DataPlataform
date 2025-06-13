"""
Repositorio de Catálogos S080 Kraken
CRUD y queries especializadas sobre la tabla 'catalogs_s080'
"""

from typing import List, Optional
from kraken.core.schemas import CatalogS080
from .base import GenericRepository

class CatalogRepository(GenericRepository[CatalogS080]):
    """
    Repositorio de catálogos institucionales con métodos personalizados.
    """
    def __init__(self):
        super().__init__(CatalogS080)

    def find_by_schema_and_table(self, schema: str, table: str) -> Optional[CatalogS080]:
        """
        Busca un catálogo por schema y nombre de tabla.
        """
        with self.get_session_fn() as session:
            return (
                session.query(self.model)
                .filter(self.model.schema == schema)
                .filter(self.model.table == table)
                .first()
            )

    def list_by_cde(self, cde_id: str, limit: int = 100) -> List[CatalogS080]:
        """
        Lista catálogos que ya están vinculados a un CDE específico.
        """
        with self.get_session_fn() as session:
            return (
                session.query(self.model)
                .filter(self.model.cde == cde_id)
                .limit(limit)
                .all()
            )

    def search_by_desc(self, query: str, limit: int = 100) -> List[CatalogS080]:
        """
        Busca catálogos por descripción corta o larga.
        """
        with self.get_session_fn() as session:
            return (
                session.query(self.model)
                .filter(
                    (self.model.desc_raw.ilike(f"%{query}%")) |
                    (self.model.desc_clean.ilike(f"%{query}%"))
                )
                .limit(limit)
                .all()
            )

    def list_distinct_tables(self) -> List[str]:
        """
        Lista nombres únicos de tablas de catálogo.
        """
        with self.get_session_fn() as session:
            return [row[0] for row in session.query(self.model.table).distinct() if row[0]]

# Shortcut global para acceso fácil
catalog_repo = CatalogRepository()
