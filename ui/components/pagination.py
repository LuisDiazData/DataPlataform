"""
Kraken UI - Pagination
Controles de paginación y helpers para mantener estado entre páginas de resultados.
"""

import streamlit as st
from typing import Callable, Optional
from kraken.ui.state import get as get_state, set as set_state

def render_pagination_controls(
    total_items: int,
    key_prefix: str = "",
    page_size_options = [10, 25, 50, 100],
    default_page_size: int = 25,
    callback: Optional[Callable] = None,
):
    """
    Renderiza controles de paginación (página actual, tamaño, navegación).
    Guarda el estado en session_state con prefijos para multi-paginadores.
    """
    page_key = f"{key_prefix}page"
    size_key = f"{key_prefix}page_size"
    total_pages = max(1, (total_items + get_state(size_key, default_page_size) - 1) // get_state(size_key, default_page_size))

    col1, col2, col3 = st.columns([2, 2, 6])
    with col1:
        page_size = st.selectbox(
            "Resultados por página",
            options=page_size_options,
            index=page_size_options.index(get_state(size_key, default_page_size)),
            key=size_key,
        )
        set_state(size_key, page_size)

    with col2:
        page = get_state(page_key, 1)
        left, _, right = st.columns([1,2,1])
        prev = left.button("◀", key=f"{key_prefix}prev")
        next_ = right.button("▶", key=f"{key_prefix}next")
        if prev and page > 1:
            set_state(page_key, page - 1)
            if callback: callback()
        if next_ and page < total_pages:
            set_state(page_key, page + 1)
            if callback: callback()
        st.markdown(f"<div style='text-align:center;'>Página <b>{page}</b> de <b>{total_pages}</b></div>", unsafe_allow_html=True)
        if page > total_pages:
            set_state(page_key, total_pages)
        if page < 1:
            set_state(page_key, 1)

    with col3:
        st.markdown(
            f"<div style='text-align:right;color:#888;font-size:0.95em;'>Total: {total_items:,} resultados</div>",
            unsafe_allow_html=True
        )

def get_pagination_indices(
    total_items: int,
    key_prefix: str = "",
    default_page_size: int = 25,
) -> (int, int, int):
    """
    Retorna (página actual, start_idx, end_idx) para usar en slicing de resultados.
    """
    size_key = f"{key_prefix}page_size"
    page_key = f"{key_prefix}page"
    page_size = get_state(size_key, default_page_size)
    page = get_state(page_key, 1)
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    if page < 1:
        page = 1
        set_state(page_key, 1)
    if page > total_pages:
        page = total_pages
        set_state(page_key, total_pages)
    start = (page - 1) * page_size
    end = min(start + page_size, total_items)
    return page, start, end

def reset_pagination(key_prefix: str = ""):
    """
    Resetea el paginador a la primera página.
    """
    set_state(f"{key_prefix}page", 1)
