"""
Kraken Utils
Funciones utilitarias de uso general para limpieza de texto, particionamiento de listas, manejo de paths, y más.
"""

import re
import unicodedata
from typing import List, Any, Iterator, Optional
from pathlib import Path
import os

def clean_text(text: Optional[str]) -> str:
    """
    Normaliza y limpia una cadena de texto para comparaciones semánticas o fuzzy.
    - Convierte a minúsculas, quita saltos de línea, espacios extra, signos raros, normaliza Unicode.
    - Si recibe None, regresa cadena vacía.
    """
    if not text or not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text)
    # Remueve puntuación innecesaria, deja sólo letras/números, espacios, guiones y puntos.
    text = re.sub(r"[^\w\s\-\.,]", "", text)
    text = unicodedata.normalize("NFKC", text)
    return text.strip()

def chunk_list(lst: List[Any], chunk_size: int) -> Iterator[List[Any]]:
    """
    Divide una lista en bloques de tamaño `chunk_size`.
    Ejemplo: list(chunk_list([1,2,3,4,5], 2)) → [[1,2],[3,4],[5]]
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def ensure_dir(path: str | Path) -> None:
    """
    Crea el directorio (y padres) si no existe. No falla si ya existe.
    """
    if isinstance(path, str):
        path = Path(path)
    path.mkdir(parents=True, exist_ok=True)

def get_file_stem(filename: str) -> str:
    """
    Obtiene el nombre base de un archivo sin extensión.
    """
    return Path(filename).stem

def is_excel_file(path: str | Path) -> bool:
    """
    Retorna True si la ruta corresponde a un archivo Excel.
    """
    return str(path).lower().endswith((".xlsx", ".xls"))

def is_csv_file(path: str | Path) -> bool:
    """
    Retorna True si la ruta corresponde a un archivo CSV.
    """
    return str(path).lower().endswith(".csv")

def parse_list_field(val: Optional[str], sep: str = "|") -> List[str]:
    """
    Convierte un campo de texto delimitado a lista. Ejemplo: "A|B|C" → ["A", "B", "C"]
    Si el campo es vacío/None, retorna [].
    """
    if not val or not isinstance(val, str):
        return []
    return [v.strip() for v in val.split(sep) if v.strip()]

def safe_int(val: Any, default: int = 0) -> int:
    """
    Convierte un valor a int de forma segura, con valor por default.
    """
    try:
        return int(val)
    except Exception:
        return default

def safe_float(val: Any, default: float = 0.0) -> float:
    """
    Convierte un valor a float de forma segura, con valor por default.
    """
    try:
        return float(val)
    except Exception:
        return default

def get_env_variable(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Obtiene una variable de entorno o regresa el default si no existe.
    """
    return os.environ.get(name, default)
