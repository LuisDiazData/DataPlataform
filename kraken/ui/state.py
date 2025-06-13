"""
State Manager para Kraken UI
Helpers para uso seguro y consistente de st.session_state en toda la interfaz.
"""

import streamlit as st
from typing import Any, Optional

def get(key: str, default: Optional[Any] = None) -> Any:
    """
    Obtiene un valor de session_state, lo inicializa si no existe.
    """
    return st.session_state.setdefault(key, default)

def set(key: str, value: Any) -> None:
    """
    Asigna un valor en session_state.
    """
    st.session_state[key] = value

def toggle(key: str, default: bool = False) -> None:
    """
    Invierte un valor booleano (útil para switches).
    """
    st.session_state[key] = not st.session_state.get(key, default)

def reset(keys: list[str]) -> None:
    """
    Elimina uno o varios keys de session_state (para resetear filtros, paginación, etc.).
    """
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]

def clear_all() -> None:
    """
    Borra toda la session_state (útil para pruebas/debug o logout).
    """
    st.session_state.clear()

def ensure_init(keys_defaults: dict[str, Any]) -> None:
    """
    Inicializa varios keys a sus valores por default si no existen.
    """
    for k, v in keys_defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def get_filter(key: str, default: Any = None) -> Any:
    """
    Helper especial para filtros (todos bajo state['filters']).
    """
    filters = st.session_state.setdefault("filters", {})
    return filters.get(key, default)

def set_filter(key: str, value: Any) -> None:
    filters = st.session_state.setdefault("filters", {})
    filters[key] = value
    st.session_state["filters"] = filters  # actualiza el objeto completo

