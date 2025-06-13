"""
Servicio de Atributos Físicos Kraken
Lógica avanzada para búsquedas, edición, validación y reporting de atributos físicos.
"""

from typing import List, Optional, Dict, Any, Tuple
from kraken.repositories.attribute_repo import attribute_repo
from kraken.repositories.cde_repo import cde_repo
from kraken.core.schemas import Attribute
from kraken.core.utils import clean_text, chunk_list

class AttributeService:
    """
    Orquesta operaciones frecuentes de atributos físicos.
    """
    def __init__(self):
        self.repo = attribute_repo

    def get_by_id(self, attr_id: int) -> Optional[Attribute]:
        return self.repo.get(attr_id)

    def search(
        self, 
        query: str, 
        by: str = "physical_name", 
        limit: int = 20, 
        fuzzy: bool = True
    ) -> List[Attribute]:
        """
        Búsqueda rápida por nombre físico, variable o descripción.
        """
        method = self.repo.find_by_physical_name if by == "physical_name" else None
        if method and fuzzy:
            results = method(query, exact=False)
        else:
            # Búsqueda lineal alternativa
            results = [
                attr for attr in self.repo.all()
                if query.lower() in getattr(attr, by, "").lower()
            ]
        return results[:limit]

    def list_by_dominio(self, dominio: str, limit: int = 100) -> List[Attribute]:
        return self.repo.list_by_dominio(dominio, limit=limit)

    def list_distinct_dominios(self) -> List[str]:
        return self.repo.list_distinct_dominios()

    def count_by_iniciativa(self, iniciativa: str) -> int:
        return self.repo.count_by_iniciativa(iniciativa)

    def edit_attribute(
        self, 
        attr_id: int, 
        updates: Dict[str, Any]
    ) -> Optional[Attribute]:
        """
        Edita un atributo físico y retorna el registro actualizado.
        Aplica limpieza a los campos de texto.
        """
        # Limpiar campos relevantes
        clean_updates = dict(updates)
        if "desc_raw" in clean_updates:
            clean_updates["desc_clean"] = clean_text(clean_updates["desc_raw"])
        if "physical_name" in clean_updates:
            clean_updates["physical_name"] = clean_text(clean_updates["physical_name"])
        if "variable_name" in clean_updates:
            clean_updates["variable_name"] = clean_text(clean_updates["variable_name"])
        return self.repo.update(attr_id, clean_updates)

    def get_attributes_with_cde(self) -> List[Tuple[Attribute, Optional[str]]]:
        """
        Devuelve una lista de tuplas: (atributo, cde_id), para reporting o sugerencias.
        """
        attrs = self.repo.all()
        results = []
        for attr in attrs:
            # Aquí podrías tener un campo de mapeo directo, o buscar por lógica de negocio
            cde_id = getattr(attr, "cde_id", None)
            results.append((attr, cde_id))
        return results

    def paginate_attributes(self, page: int = 1, page_size: int = 50) -> List[Attribute]:
        """
        Devuelve una página de atributos físicos (útil para UIs con paginación).
        """
        all_attrs = self.repo.all()
        chunks = list(chunk_list(all_attrs, page_size))
        if 0 < page <= len(chunks):
            return chunks[page - 1]
        return []

# Instancia global para fácil acceso
attribute_service = AttributeService()
