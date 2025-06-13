"""
Repositorio Genérico Kraken
Abstracción CRUD sobre SQLAlchemy ORM. 
Herédalo para atributos, CDEs, catálogos, feedback, etc.
"""

from typing import Type, TypeVar, Generic, List, Optional, Dict, Any, Callable
from sqlalchemy.orm import Session
from sqlalchemy import select
from kraken.core.database import get_session

T = TypeVar("T")  # Modelo ORM

class GenericRepository(Generic[T]):
    """
    Provee operaciones CRUD y paginadas sobre modelos SQLAlchemy.
    Debe ser instanciado con el modelo y opcionalmente un get_session custom.
    """
    def __init__(self, model: Type[T], get_session_fn: Callable[[], Session] = get_session):
        self.model = model
        self.get_session_fn = get_session_fn

    def get(self, id_: Any) -> Optional[T]:
        with self.get_session_fn() as session:
            return session.get(self.model, id_)

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[Any] = None
    ) -> List[T]:
        with self.get_session_fn() as session:
            query = session.query(self.model)
            if filters:
                for key, value in filters.items():
                    query = query.filter(getattr(self.model, key) == value)
            if order_by is not None:
                query = query.order_by(order_by)
            return query.offset(offset).limit(limit).all()

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        with self.get_session_fn() as session:
            query = session.query(self.model)
            if filters:
                for key, value in filters.items():
                    query = query.filter(getattr(self.model, key) == value)
            return query.count()

    def create(self, obj_in: Dict[str, Any]) -> T:
        with self.get_session_fn() as session:
            obj = self.model(**obj_in)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj

    def update(self, id_: Any, obj_in: Dict[str, Any]) -> Optional[T]:
        with self.get_session_fn() as session:
            obj = session.get(self.model, id_)
            if not obj:
                return None
            for k, v in obj_in.items():
                setattr(obj, k, v)
            session.commit()
            session.refresh(obj)
            return obj

    def delete(self, id_: Any) -> bool:
        with self.get_session_fn() as session:
            obj = session.get(self.model, id_)
            if not obj:
                return False
            session.delete(obj)
            session.commit()
            return True

    def all(self) -> List[T]:
        with self.get_session_fn() as session:
            return session.query(self.model).all()

    def filter_by(self, **kwargs) -> List[T]:
        with self.get_session_fn() as session:
            return session.query(self.model).filter_by(**kwargs).all()
