"""
Kraken Ingestor
Carga archivos Excel/CSV en las tablas principales usando los repositorios.
Detecta columnas por sinónimos, limpia textos y registra logs de ingestión.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import pandas as pd

from kraken.repositories.attribute_repo import attribute_repo
from kraken.repositories.cde_repo import cde_repo
from kraken.repositories.catalog_repo import catalog_repo
from kraken.repositories.quality_rules_repo import quality_rules_repo
from kraken.repositories.feedback_repo import feedback_repo
from kraken.repositories.duplicates_repo import duplicates_repo
from kraken.core.utils import clean_text
from kraken.core.database import get_session
from kraken.core.schemas import IngestionLog

# Sinónimos de columnas para cada tabla
COLUMN_SYNONYMS: Dict[str, Dict[str, List[str]]] = {
    "attributes": {
        "product": ["PRODUCT"],
        "dominio": ["DOMINIO"],
        "aplication_csi": ["APPLICATION_CSI"],
        "origination_source": ["ORIGINATION_SOURCE"],
        "table_source": ["TABLE_SOURCE", "TABLESOURCE"],
        "dataset_description": ["DATASET_DESCRIPTION"],
        "physical_name": ["N_FISICO"],
        "variable_name": ["VARIABLE_NAME", "N_VARIABLE", "VARIABLE"],
        "desc_raw": ["DESC_ESP", "DATASET_DESCRIPTION", "DESCRIPTIO"],
        "iniciativa": ["INICIATIVA"],
    },
    "cdes": {
        "cde_id": ["Enterprise_ID", "CDE", "ID_CDE"],
        "biz_term": ["BIZ_TERM", "Biz_Term", "BUSINESS_TERM"],
        "desc_raw": ["DESCRIPCION_CDE", "Descripcion_CDE", "Desc_Cde", "DESC_CDE"],
        "prod_domains": ["producer_domains", "PRODUCER_DOMAINS"],
        "cons_domains": ["consumer_domains", "CONSUMER_DOMAINS"],
        "falta_desc": ["falta_desc", "FALTA_DESC"]
    },
    "catalogs_s080": {
        "schema": ["SCHEMA", "ESQUEMA", "schema"],
        "table": ["TABLE", "TABLA", "table"],
        "desc_raw": ["DESC_CORTA", "DESCRIPCION_CORTA", "DESCRIPTION", "desc_cort"],
        "atributos": ["ATRIBUTOS", "ATTRIBUTES", "atributos"],
        "ejemplo_datos": ["EJEMPLO_DATOS", "SAMPLE_DATA", "EXAMPLES", "eje_txt_largo"],
        "cde": ["CDE", "cde_id"]
    },
    "cde_quality_rules": {
        "cde_id": ["Enterprise_ID", "CDE", "ID_CDE", "ENTERPRISE_ID"],
        "rule_natural": ["rule_natural", "RULE_NATURAL"],
        "rule_standard": ["rule_standard", "RULE_STANDARD"],
        "dimension": ["dimension", "DIMENSION"],
        "field_type": ["field_type", "FIELD_TYPE"],
        "max_length": ["max_length", "MAX_LENGTH"],
        "scale": ["scale", "SCALE"],
        "pattern": ["pattern", "PATTERN"],
        "example": ["example", "EXAMPLE"]
    },
}

# Relaciona nombre de archivo (sin extensión) a tabla/función de repo
FILENAME_TABLE_MAP = {
    "Mega_Diccionario": ("attributes", attribute_repo),
    "Base_CDEs": ("cdes", cde_repo),
    "Base_Catalogos_S080": ("catalogs_s080", catalog_repo),
    "DQ_Rules": ("cde_quality_rules", quality_rules_repo),
}

def map_columns(df: pd.DataFrame, table: str) -> pd.DataFrame:
    """
    Renombra columnas según sinónimos y limpia nombres.
    """
    synonyms = COLUMN_SYNONYMS.get(table, {})
    mapping = {}
    raw_cols = list(df.columns)
    for std_col, syn_list in synonyms.items():
        for raw_col in raw_cols:
            for syn in syn_list:
                if str(raw_col).strip().lower() == syn.strip().lower():
                    mapping[raw_col] = std_col
    df = df.rename(columns=mapping)
    # Añadir columnas faltantes como vacías
    for std_col in synonyms:
        if std_col not in df.columns:
            df[std_col] = ""
    return df

def process_row(row: Dict[str, Any], table: str) -> Dict[str, Any]:
    """
    Aplica limpieza y estandarización a cada fila antes de insertar.
    """
    clean = dict(row)
    if "desc_raw" in clean:
        clean["desc_clean"] = clean_text(clean.get("desc_raw", ""))
    if "physical_name" in clean:
        clean["physical_name"] = clean_text(clean.get("physical_name", ""))
    if "variable_name" in clean:
        clean["variable_name"] = clean_text(clean.get("variable_name", ""))
    # Otros campos de limpieza pueden agregarse aquí
    return clean

def ingest_file(file_path: Path) -> int:
    """
    Ingesta un solo archivo Excel o CSV en la tabla correcta.
    Retorna el número de filas insertadas.
    """
    stem = file_path.stem
    if stem not in FILENAME_TABLE_MAP:
        logging.warning(f"Archivo {file_path} no mapeado, omitiendo.")
        return 0
    table, repo = FILENAME_TABLE_MAP[stem]
    # Lee archivo (soporte Excel y CSV)
    if file_path.suffix.lower() in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
    elif file_path.suffix.lower() == ".csv":
        df = pd.read_csv(file_path)
    else:
        logging.warning(f"Formato de archivo no soportado: {file_path}")
        return 0
    df = map_columns(df, table)
    n = 0
    for _, row in df.iterrows():
        item = process_row(row.to_dict(), table)
        try:
            repo.create(item)
            n += 1
        except Exception as ex:
            logging.error(f"Error insertando fila en {table}: {ex}")
    # Registra log de ingestión
    with get_session() as session:
        session.add(IngestionLog(details=f"{file_path.name}: {n} filas"))
    logging.info(f"Ingesta completada de {file_path.name}: {n} filas insertadas.")
    return n

def ingest_directory(directory: Path) -> Dict[str, int]:
    """
    Ingesta todos los archivos soportados en un directorio.
    Retorna diccionario {archivo: filas insertadas}
    """
    results = {}
    for file in directory.glob("*.xlsx"):
        results[file.name] = ingest_file(file)
    for file in directory.glob("*.csv"):
        results[file.name] = ingest_file(file)
    return results

def ingest_all_from_config():
    """
    Ingesta todos los archivos de catálogos definidos en settings.yaml.
    """
    from kraken.core.config import get_config
    catalogs_dir = Path(get_config().files.catalogs_dir)
    logging.info(f"Iniciando ingestión desde {catalogs_dir}")
    return ingest_directory(catalogs_dir)
