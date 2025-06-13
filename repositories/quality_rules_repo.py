"""
Repositorio de Reglas de Calidad Kraken
CRUD y queries especializadas sobre la tabla 'cde_quality_rules'
"""

from typing import List, Optional
from kraken.core.schemas import QualityRule
from .base import GenericRepository

class QualityRulesRepository(GenericRepository[QualityRule]):
    """
    Repositorio para reglas de calidad asociadas a CDEs.
    """
    def __init__(self):
        super().__init__(QualityRule)

    def find_by_cde_id(self, cde_id: str, limit: int = 100) -> List[QualityRule]:
        """
        Lista reglas de calidad asociadas a un CDE específico.
        """
        with self.get_session_fn() as session:
            return (
                session.query(self.model)
                .filter(self.model.cde_id == cde_id)
                .limit(limit)
                .all()
            )

    def search_by_rule_text(self, query: str, limit: int = 100) -> List[QualityRule]:
        """
        Busca reglas de calidad por texto en rule_natural o rule_standard.
        """
        with self.get_session_fn() as session:
            return (
                session.query(self.model)
                .filter(
                    (self.model.rule_natural.ilike(f"%{query}%")) |
                    (self.model.rule_standard.ilike(f"%{query}%"))
                )
                .limit(limit)
                .all()
            )

    def list_distinct_dimensions(self) -> List[str]:
        """
        Devuelve una lista de dimensiones únicas (ej. "validez", "completitud").
        """
        with self.get_session_fn() as session:
            return [row[0] for row in session.query(self.model.dimension).distinct() if row[0]]

# Shortcut global para acceso fácil
quality_rules_repo = QualityRulesRepository()
