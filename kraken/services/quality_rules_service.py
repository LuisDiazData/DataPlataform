"""
Servicio de Reglas de Calidad Kraken
Lógica avanzada para búsqueda, agrupación, edición y reporting de reglas DQ de CDEs.
"""

from typing import List, Optional, Dict, Any
from kraken.repositories.quality_rules_repo import quality_rules_repo
from kraken.core.schemas import QualityRule
from kraken.core.utils import clean_text, chunk_list

class QualityRulesService:
    """
    Orquesta operaciones frecuentes sobre reglas de calidad de datos.
    """
    def __init__(self):
        self.repo = quality_rules_repo

    def get_by_id(self, rule_id: int) -> Optional[QualityRule]:
        return self.repo.get(rule_id)

    def find_by_cde_id(self, cde_id: str, limit: int = 100) -> List[QualityRule]:
        """
        Lista reglas asociadas a un CDE específico.
        """
        return self.repo.find_by_cde_id(cde_id, limit=limit)

    def search(
        self,
        query: str,
        by: str = "rule_natural",
        limit: int = 50,
        fuzzy: bool = True
    ) -> List[QualityRule]:
        """
        Busca reglas de calidad por texto en regla natural o estándar.
        """
        method = self.repo.search_by_rule_text if by in ("rule_natural", "rule_standard") else None
        if method and fuzzy:
            return method(query, limit=limit)
        else:
            return [
                rule for rule in self.repo.all()
                if query.lower() in getattr(rule, by, "").lower()
            ][:limit]

    def list_distinct_dimensions(self) -> List[str]:
        """
        Devuelve lista de dimensiones únicas (ej. "validez", "completitud").
        """
        return self.repo.list_distinct_dimensions()

    def group_rules_by_dimension(self) -> Dict[str, List[QualityRule]]:
        """
        Agrupa las reglas por dimensión (útil para dashboards).
        """
        all_rules = self.repo.all()
        grouped = {}
        for rule in all_rules:
            dim = rule.dimension or "(Sin dimensión)"
            grouped.setdefault(dim, []).append(rule)
        return grouped

    def paginate_rules(self, page: int = 1, page_size: int = 50) -> List[QualityRule]:
        """
        Devuelve una página de reglas (útil para UIs con paginación).
        """
        all_rules = self.repo.all()
        chunks = list(chunk_list(all_rules, page_size))
        if 0 < page <= len(chunks):
            return chunks[page - 1]
        return []

    def edit_rule(self, rule_id: int, updates: Dict[str, Any]) -> Optional[QualityRule]:
        """
        Edita una regla de calidad y retorna el registro actualizado.
        Aplica limpieza a los campos de texto relevantes.
        """
        clean_updates = dict(updates)
        if "rule_natural" in clean_updates:
            clean_updates["rule_natural"] = clean_text(clean_updates["rule_natural"])
        if "rule_standard" in clean_updates:
            clean_updates["rule_standard"] = clean_text(clean_updates["rule_standard"])
        return self.repo.update(rule_id, clean_updates)

# Instancia global para fácil acceso
quality_rules_service = QualityRulesService()
