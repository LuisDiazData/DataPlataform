"""
Kraken ORM Schemas - SQLAlchemy models
Define todas las tablas requeridas para ingestión y operación de Kraken.
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

# ---- Tabla de atributos físicos ----
class Attribute(Base):
    __tablename__ = "attributes"
    attr_id         = Column(Integer, primary_key=True, autoincrement=True)
    product         = Column(String(100))
    dominio         = Column(String(100))
    aplication_csi  = Column(String(100))
    origination_source = Column(String(100))
    table_source    = Column(String(100))
    dataset_description = Column(Text)
    physical_name   = Column(String(120), index=True)
    variable_name   = Column(String(120))
    desc_raw        = Column(Text)
    desc_clean      = Column(Text)
    iniciativa      = Column(String(100))
    created_at      = Column(DateTime, server_default=func.now())

# ---- Tabla de CDEs ----
class CDE(Base):
    __tablename__ = "cdes"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    cde_id        = Column(String(100), unique=True, index=True)
    biz_term      = Column(String(200), index=True)
    desc_raw      = Column(Text)
    desc_clean    = Column(Text)
    prod_domains  = Column(String(200))
    cons_domains  = Column(String(200))
    falta_desc    = Column(Boolean, default=False)
    created_at    = Column(DateTime, server_default=func.now())

# ---- Tabla de Catálogos S080 ----
class CatalogS080(Base):
    __tablename__ = "catalogs_s080"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    schema        = Column(String(50))
    table         = Column(String(50))
    desc_raw      = Column(Text)
    desc_clean    = Column(Text)
    atributos     = Column(String(250))
    ejemplo_datos = Column(Text)
    cde           = Column(String(100))  # vínculo sugerido CDE
    created_at    = Column(DateTime, server_default=func.now())

# ---- Tabla de reglas de calidad (DQ) ----
class QualityRule(Base):
    __tablename__ = "cde_quality_rules"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    cde_id        = Column(String(100), index=True)
    rule_natural  = Column(Text)
    rule_standard = Column(Text)
    dimension     = Column(String(50))
    field_type    = Column(String(50))
    max_length    = Column(Integer)
    scale         = Column(Integer)
    pattern       = Column(String(100))
    example       = Column(String(100))
    created_at    = Column(DateTime, server_default=func.now())

# ---- Tabla de feedback de usuario ----
class Feedback(Base):
    __tablename__ = "feedback"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    attr_id       = Column(Integer, index=True)   # Relación con Attribute
    user          = Column(String(64))
    desc_original = Column(Text)
    desc_final    = Column(Text)
    score         = Column(Float)
    comment       = Column(Text)
    created_at    = Column(DateTime, server_default=func.now())

# ---- Historial de duplicados y resolución ----
class DuplicateHistory(Base):
    __tablename__ = "duplicate_history"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    cde_a         = Column(String(100), index=True)
    cde_b         = Column(String(100), index=True)
    is_duplicate  = Column(Boolean)
    resolved_by   = Column(String(64))
    resolved_at   = Column(DateTime, server_default=func.now())
    comment       = Column(Text)

# ---- Log de ingestión ----
class IngestionLog(Base):
    __tablename__ = "ingestion_log"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    ingestion_time = Column(DateTime, server_default=func.now())
    details       = Column(Text)

