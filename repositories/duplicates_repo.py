"""
Repositorio de Duplicados Kraken
CRUD y queries especializadas sobre la tabla 'duplicate_history'
"""

from typing import List, Optional
from kraken.core.schemas import DuplicateHistory
from .base import GenericRepository

class DuplicatesRepository(GenericRepository[DuplicateHistory]):
    """
    Repositorio para historial y resolución de duplicados entre CDEs.
    """
    def __init__(self):
        super().__init__(DuplicateHistory)

    def list_duplicates_for_cde(self, cde_id: str, limit: int = 100) -> List[DuplicateHistory]:
        """
        Devuelve el historial de duplicados donde un CDE participa.
        """
        with self.get_session_fn() as session:
            return (
                session.query(self.model)
                .filter(
                    (self.model.cde_a == cde_id) | (self.model.cde_b == cde_id)
                )
                .order_by(self.model.resolved_at.desc())
                .limit(limit)
                .all()
            )

    def find_pair(self, cde_a: str, cde_b: str) -> Optional[DuplicateHistory]:
        """
        Devuelve el registro de historial para un par CDE A y B (en cualquier orden).
        """
        with self.get_session_fn() as session:
            return (
                session.query(self.model)
                .filter(
                    ((self.model.cde_a == cde_a) & (self.model.cde_b == cde_b)) |
                    ((self.model.cde_a == cde_b) & (self.model.cde_b == cde_a))
                )
                .first()
            )

    def list_recent_resolved(self, limit: int = 100) -> List[DuplicateHistory]:
        """
        Lista los duplicados más recientemente resueltos.
        """
        with self.get_session_fn() as session:
            return (
                session.query(self.model)
                .order_by(self.model.resolved_at.desc())
                .limit(limit)
                .all()
            )

# Shortcut global para acceso fácil
duplicates_repo = DuplicatesRepository()
