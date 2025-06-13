"""
Repositorio de Atributos Físicos Kraken
CRUD y queries especializadas sobre la tabla 'attributes'
"""

from typing import List, Optional
from kraken.core.schemas import Attribute
from .base import GenericRepository

class AttributeRepository(GenericRepository[Attribute]):
    """
    Repositorio de atributos físicos con métodos personalizados.
    """
    def __init__(self):
        super().__init__(Attribute)

    def find_by_physical_name(self, name: str, exact: bool = False) -> List[Attribute]:
        """
        Busca por nombre físico (exacto o contiene).
        """
        with self.get_session_fn() as session:
            query = session.query(self.model)
            if exact:
                return query.filter(self.model.physical_name == name).all()
            return query.filter(self.model.physical_name.ilike(f"%{name}%")).all()

    def list_by_dominio(self, dominio: str, limit: int = 100) -> List[Attribute]:
        with self.get_session_fn() as session:
            return (
                session.query(self.model)
                .filter(self.model.dominio == dominio)
                .limit(limit)
                .all()
            )

    def list_distinct_dominios(self) -> List[str]:
        with self.get_session_fn() as session:
            return [row[0] for row in session.query(self.model.dominio).distinct()]

    def count_by_iniciativa(self, iniciativa: str) -> int:
        with self.get_session_fn() as session:
            return (
                session.query(self.model)
                .filter(self.model.iniciativa == iniciativa)
                .count()
            )

# Shortcut global para acceso fácil en el resto de la app
attribute_repo = AttributeRepository()
