"""
Kraken Database
Manejo de engine, sesión, y helpers de inicialización/migración para la base de datos Kraken.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.engine import Engine
from contextlib import contextmanager
from pathlib import Path
from .config import get_config
from .schemas import Base

# Obtén la ruta de la base de datos desde settings.yaml
def get_db_path() -> str:
    config = get_config()
    data_dir = Path(config.files.data_dir)
    db_path = data_dir / "kraken_data.sqlite"
    data_dir.mkdir(parents=True, exist_ok=True)
    return str(db_path)

# Inicializa el engine principal (SQLite, puede cambiar a futuro)
def get_engine(echo: bool = False) -> Engine:
    db_path = get_db_path()
    engine = create_engine(
        f"sqlite:///{db_path}",
        echo=echo,
        connect_args={"check_same_thread": False}
    )
    # PRAGMA performance tweaks para SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.close()
    return engine

# Crea un Session factory global, thread-safe
_ENGINE = get_engine()
SessionLocal = scoped_session(sessionmaker(bind=_ENGINE, autoflush=False, autocommit=False))

@contextmanager
def get_session() -> Session:
    """
    Context manager para una sesión SQLAlchemy.
    Cierra y hace rollback ante errores automáticamente.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def init_db(create_all: bool = True):
    """
    Inicializa la base de datos (crea todas las tablas si no existen).
    Se llama en el arranque de Kraken o en ingest.
    """
    if create_all:
        Base.metadata.create_all(bind=_ENGINE)

def drop_all_tables(confirm: bool = False):
    """
    Borra todas las tablas. SOLO usar en desarrollo/testing.
    """
    if confirm:
        Base.metadata.drop_all(bind=_ENGINE)

# Opción: migraciones avanzadas (puedes usar Alembic más adelante)
