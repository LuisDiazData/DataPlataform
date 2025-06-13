"""
Repositorio de Feedback Kraken
CRUD y queries especializadas sobre la tabla 'feedback'
"""

from typing import List, Optional
from kraken.core.schemas import Feedback
from .base import GenericRepository

class FeedbackRepository(GenericRepository[Feedback]):
    """
    Repositorio para feedback de usuarios y mappings relacionados.
    """
    def __init__(self):
        super().__init__(Feedback)

    def list_by_attr_id(self, attr_id: int, limit: int = 100) -> List[Feedback]:
        """
        Lista feedback asociado a un atributo físico específico.
        """
        with self.get_session_fn() as session:
            return (
                session.query(self.model)
                .filter(self.model.attr_id == attr_id)
                .order_by(self.model.created_at.desc())
                .limit(limit)
                .all()
            )

    def list_by_user(self, user: str, limit: int = 100) -> List[Feedback]:
        """
        Lista feedback creado por un usuario específico.
        """
        with self.get_session_fn() as session:
            return (
                session.query(self.model)
                .filter(self.model.user == user)
                .order_by(self.model.created_at.desc())
                .limit(limit)
                .all()
            )

    def search_by_comment(self, query: str, limit: int = 100) -> List[Feedback]:
        """
        Busca feedback que contenga cierto texto en los comentarios.
        """
        with self.get_session_fn() as session:
            return (
                session.query(self.model)
                .filter(self.model.comment.ilike(f"%{query}%"))
                .order_by(self.model.created_at.desc())
                .limit(limit)
                .all()
            )

# Shortcut global para acceso fácil
feedback_repo = FeedbackRepository()
