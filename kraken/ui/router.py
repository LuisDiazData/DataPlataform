"""
Kraken UI Router
Gestiona la navegación multipágina de la app, con soporte para deep links (?page=).
"""

import streamlit as st
from typing import Callable, Dict

# Importa aquí cada página real (solo los nombres, los .py deben existir aunque sean st.empty())
from .pages.dashboard import render_dashboard
from .pages.technical_search import render_technical_search
from .pages.semantic_search import render_semantic_search
from .pages.cde_explorer import render_cde_explorer
from .pages.catalogs import render_catalogs
from .pages.duplicates import render_duplicates
from .pages.feedback import render_feedback
from .pages.quality_rules import render_quality_rules
from .pages.metrics import render_metrics

PAGES: Dict[str, Callable[[], None]] = {
    "🏠 Dashboard": render_dashboard,
    "🔧 Búsqueda Técnica": render_technical_search,
    "🤖 Búsqueda Semántica": render_semantic_search,
    "📋 CDE Explorer": render_cde_explorer,
    "📑 Catálogos": render_catalogs,
    "🔁 Duplicados": render_duplicates,
    "💬 Feedback": render_feedback,
    "📏 Reglas DQ": render_quality_rules,
    "📈 Métricas": render_metrics,
}

def get_query_params():
    """Devuelve los query params actuales como dict."""
    return st.experimental_get_query_params()

def set_query_params(page: str):
    """Actualiza los query params para deep link."""
    st.experimental_set_query_params(page=page)

def render_page():
    """Renderiza la página seleccionada y sincroniza los query params."""
    st.sidebar.title("Menú Kraken")
    page_names = list(PAGES.keys())

    # Deep link: si hay ?page=... en la URL, selecciónalo
    query_params = get_query_params()
    default_idx = 0
    if "page" in query_params:
        page_param = query_params["page"][0]
        if page_param in page_names:
            default_idx = page_names.index(page_param)

    # Sidebar radio para navegación
    page = st.sidebar.radio("Ir a:", page_names, index=default_idx)
    set_query_params(page)

    # Llama a la función de la página
    render_func = PAGES[page]
    render_func()
