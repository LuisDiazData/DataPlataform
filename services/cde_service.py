"""
Servicio de CDEs Kraken
Lógica de negocio avanzada para búsqueda, edición, agrupación y reporte de CDEs.
"""

from typing import List, Optional, Dict, Any, Tuple
from kraken.repositories.cde_repo import cde_repo
from kraken.repositories.quality_rules_repo import quality_rules_repo
from kraken.core.schemas import CDE
from kraken.core.utils import clean_text, chunk_list

class CDEService:
    """
    Orquesta operaciones frecuentes sobre CDEs.
    """
    def __init__(self):
        self.repo = cde_repo

    def get_by_id(self, cde_id: str) -> Optional[CDE]:
        return self.repo.find_by_cde_id(cde_id)

    def search(
        self, 
        query: str, 
        by: str = "biz_term", 
        limit: int = 20, 
        fuzzy: bool = True
    ) -> List[CDE]:
        """
        Búsqueda rápida por business term o descripción.
        """
        method = self.repo.search_by_biz_term if by == "biz_term" else None
        if method and fuzzy:
            return method(query, exact=False, limit=limit)
        else:
            # Búsqueda lineal alternativa
            return [
                cde for cde in self.repo.all()
                if query.lower() in getattr(cde, by, "").lower()
            ][:limit]

    def list_by_domain(self, domain: str, limit: int = 100) -> List[CDE]:
        return self.repo.list_by_domain(domain, limit=limit)

    def list_distinct_domains(self) -> List[str]:
        return self.repo.list_distinct_domains()

    def edit_cde(
        self, 
        cde_id: str, 
        updates: Dict[str, Any]
    ) -> Optional[CDE]:
        """
        Edita un CDE y retorna el registro actualizado.
        Aplica limpieza de texto a los campos principales.
        """
        clean_updates = dict(updates)
        if "desc_raw" in clean_updates:
            clean_updates["desc_clean"] = clean_text(clean_updates["desc_raw"])
        if "biz_term" in clean_updates:
            clean_updates["biz_term"] = clean_text(clean_updates["biz_term"])
        return self.repo.update(cde_id, clean_updates)

    def get_quality_rules(self, cde_id: str) -> List[Any]:
        """
        Devuelve las reglas de calidad asociadas a un CDE.
        """
        return quality_rules_repo.find_by_cde_id(cde_id)

    def group_cdes_by_domain(self) -> Dict[str, List[CDE]]:
        """
        Agrupa los CDEs por dominio productor (útil para explorer o dashboards).
        """
        all_cdes = self.repo.all()
        grouped = {}
        for cde in all_cdes:
            domains = []
            # Soporta "|" como separador de múltiples dominios
            if cde.prod_domains:
                domains = [d.strip() for d in cde.prod_domains.split("|") if d.strip()]
            for dom in domains or ["(Sin dominio)"]:
                grouped.setdefault(dom, []).append(cde)
        return grouped

    def paginate_cdes(self, page: int = 1, page_size: int = 50) -> List[CDE]:
        """
        Devuelve una página de CDEs (útil para UIs con paginación).
        """
        all_cdes = self.repo.all()
        chunks = list(chunk_list(all_cdes, page_size))
        if 0 < page <= len(chunks):
            return chunks[page - 1]
        return []

# Instancia global para fácil acceso
cde_service = CDEService()
