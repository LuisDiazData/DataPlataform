"""
Servicio de Feedback Kraken
Gestión, búsqueda, edición y exportación de feedback de usuarios sobre atributos físicos.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import csv
from pathlib import Path

from kraken.repositories.feedback_repo import feedback_repo
from kraken.core.schemas import Feedback
from kraken.core.utils import clean_text, chunk_list

class FeedbackService:
    """
    Orquesta operaciones frecuentes sobre feedback de usuarios.
    """
    def __init__(self):
        self.repo = feedback_repo

    def register_feedback(
        self,
        attr_id: int,
        user: str,
        desc_original: str,
        desc_final: str,
        score: float = 1.0,
        comment: Optional[str] = None,
    ) -> Feedback:
        """
        Registra un nuevo feedback. Aplica limpieza a los textos.
        """
        item = {
            "attr_id": attr_id,
            "user": user,
            "desc_original": clean_text(desc_original),
            "desc_final": clean_text(desc_final),
            "score": score,
            "comment": comment or "",
            "created_at": datetime.utcnow()
        }
        return self.repo.create(item)

    def list_by_attr_id(self, attr_id: int, limit: int = 100) -> List[Feedback]:
        return self.repo.list_by_attr_id(attr_id, limit=limit)

    def list_by_user(self, user: str, limit: int = 100) -> List[Feedback]:
        return self.repo.list_by_user(user, limit=limit)

    def search_by_comment(self, query: str, limit: int = 100) -> List[Feedback]:
        return self.repo.search_by_comment(query, limit=limit)

    def paginate_feedback(self, page: int = 1, page_size: int = 50) -> List[Feedback]:
        """
        Devuelve una página de feedbacks.
        """
        all_feedback = self.repo.all()
        chunks = list(chunk_list(all_feedback, page_size))
        if 0 < page <= len(chunks):
            return chunks[page - 1]
        return []

    def export_feedback_csv(self, path: Path, limit: Optional[int] = None) -> int:
        """
        Exporta el feedback histórico a un archivo CSV.
        Retorna la cantidad de filas exportadas.
        """
        feedbacks = self.repo.all()
        if limit:
            feedbacks = feedbacks[:limit]
        fieldnames = [
            "id", "attr_id", "user", "desc_original", "desc_final",
            "score", "comment", "created_at"
        ]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for fb in feedbacks:
                writer.writerow({k: getattr(fb, k, "") for k in fieldnames})
        return len(feedbacks)

    def edit_feedback(self, feedback_id: int, updates: Dict[str, Any]) -> Optional[Feedback]:
        """
        Edita un feedback existente.
        """
        clean_updates = dict(updates)
        if "desc_final" in clean_updates:
            clean_updates["desc_final"] = clean_text(clean_updates["desc_final"])
        if "desc_original" in clean_updates:
            clean_updates["desc_original"] = clean_text(clean_updates["desc_original"])
        if "comment" in clean_updates:
            clean_updates["comment"] = clean_updates["comment"].strip()
        return self.repo.update(feedback_id, clean_updates)

# Instancia global para acceso fácil
feedback_service = FeedbackService()
