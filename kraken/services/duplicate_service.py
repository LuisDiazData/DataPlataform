"""
Servicio de Duplicados Kraken
Gestión, consulta, historial, resolución y exportación de duplicados de CDEs.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import csv
from pathlib import Path

from kraken.repositories.duplicates_repo import duplicates_repo
from kraken.core.schemas import DuplicateHistory
from kraken.core.utils import chunk_list

class DuplicateService:
    """
    Orquesta operaciones frecuentes sobre duplicados de CDEs.
    """
    def __init__(self):
        self.repo = duplicates_repo

    def list_duplicates_for_cde(self, cde_id: str, limit: int = 100) -> List[DuplicateHistory]:
        """
        Devuelve historial de duplicados en los que participa un CDE.
        """
        return self.repo.list_duplicates_for_cde(cde_id, limit=limit)

    def find_pair(self, cde_a: str, cde_b: str) -> Optional[DuplicateHistory]:
        """
        Busca un historial de duplicado para un par (en cualquier orden).
        """
        return self.repo.find_pair(cde_a, cde_b)

    def resolve_duplicate(
        self,
        cde_a: str,
        cde_b: str,
        is_duplicate: bool,
        resolved_by: str,
        comment: str = ""
    ) -> DuplicateHistory:
        """
        Registra la resolución (aprobación/rechazo) de un par como duplicados.
        """
        existing = self.repo.find_pair(cde_a, cde_b)
        if existing:
            # Actualiza el registro existente
            updates = {
                "is_duplicate": is_duplicate,
                "resolved_by": resolved_by,
                "resolved_at": datetime.utcnow(),
                "comment": comment
            }
            return self.repo.update(existing.id, updates)
        # Crea uno nuevo
        item = {
            "cde_a": cde_a,
            "cde_b": cde_b,
            "is_duplicate": is_duplicate,
            "resolved_by": resolved_by,
            "resolved_at": datetime.utcnow(),
            "comment": comment
        }
        return self.repo.create(item)

    def list_recent_resolved(self, limit: int = 100) -> List[DuplicateHistory]:
        """
        Lista los duplicados más recientemente resueltos.
        """
        return self.repo.list_recent_resolved(limit=limit)

    def export_duplicate_history(self, path: Path, limit: Optional[int] = None) -> int:
        """
        Exporta historial de duplicados a un archivo CSV.
        """
        records = self.repo.all()
        if limit:
            records = records[:limit]
        fieldnames = [
            "id", "cde_a", "cde_b", "is_duplicate", "resolved_by", "resolved_at", "comment"
        ]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for rec in records:
                writer.writerow({k: getattr(rec, k, "") for k in fieldnames})
        return len(records)

    def paginate_duplicates(self, page: int = 1, page_size: int = 50) -> List[DuplicateHistory]:
        """
        Devuelve una página de duplicados (útil para UIs con paginación).
        """
        all_dupes = self.repo.all()
        chunks = list(chunk_list(all_dupes, page_size))
        if 0 < page <= len(chunks):
            return chunks[page - 1]
        return []

    # Puedes agregar aquí métodos de detección automática usando motores fuzzy/semantic
    # (por ejemplo, integración con search_service o faiss_manager).

# Instancia global para acceso fácil
duplicate_service = DuplicateService()
