"""
Repositorio de CDEs Kraken
CRUD y queries especializadas sobre la tabla 'cdes'
"""

from typing import List, Optional
from kraken.core.schemas import CDE
from .base import GenericRepository

class CDERepository(GenericRepository[CDE]):
    """
    Repositorio de CDEs con métodos personalizados.
    """
    def __init__(self):
        super().__init__(CDE)

    def find_by_cde_id(self, cde_id: str) -> Optional[CDE]:
        """
        Busca un CDE por su Enterprise ID (clave de negocio).
        """
        with self.get_session_fn() as session:
            return session.query(self.model).filter(self.model.cde_id == cde_id).first()

    def list_by_domain(self, domain: str, limit: int = 100) -> List[CDE]:
        """
        Lista CDEs de un dominio productor o consumidor (busca en ambos campos).
        """
        with self.get_session_fn() as session:
            return (
                session.query(self.model)
                .filter(
                    (self.model.prod_domains.ilike(f"%{domain}%")) |
                    (self.model.cons_domains.ilike(f"%{domain}%"))
                )
                .limit(limit)
                .all()
            )

    def list_distinct_domains(self) -> List[str]:
        """
        Lista todos los dominios únicos encontrados en producer y consumer domains.
        """
        with self.get_session_fn() as session:
            prod = [d[0] for d in session.query(self.model.prod_domains).distinct() if d[0]]
            cons = [d[0] for d in session.query(self.model.cons_domains).distinct() if d[0]]
            return list(sorted(set(prod + cons)))

    def search_by_biz_term(self, term: str, exact: bool = False, limit: int = 100) -> List[CDE]:
        """
        Busca CDEs por nombre de negocio.
        """
        with self.get_session_fn() as session:
            query = session.query(self.model)
            if exact:
                query = query.filter(self.model.biz_term == term)
            else:
                query = query.filter(self.model.biz_term.ilike(f"%{term}%"))
            return query.limit(limit).all()

# Shortcut global para acceso fácil
cde_repo = CDERepository()
