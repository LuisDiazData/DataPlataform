"""
Kraken UI - Search Bar
Input de búsqueda universal con debounce y atajo Enter.
"""

import streamlit as st
import time
from kraken.ui.state import get as get_state, set as set_state
from typing import Callable, Optional

def search_bar(
    label: str = "Buscar...",
    key: str = "search_query",
    button_label: str = "Buscar",
    on_search: Optional[Callable[[str], None]] = None,
    debounce: float = 0.5,
):
    """
    Renderiza un input de búsqueda con debounce y botón.
    Llama a `on_search(query)` al buscar.
    El estado se guarda en session_state[key].
    """
    query = get_state(key, "")
    last_search = get_state(f"{key}_last_search", "")
    last_input_time = get_state(f"{key}_last_input_time", 0.0)

    input_col, btn_col = st.columns([8,1])
    with input_col:
        new_query = st.text_input(label, value=query, key=f"{key}_input")
        if new_query != query:
            set_state(key, new_query)
            set_state(f"{key}_last_input_time", time.time())

    with btn_col:
        if st.button(button_label, key=f"{key}_btn"):
            set_state(f"{key}_last_search", get_state(key))
            if on_search:
                on_search(get_state(key))

    # Soporte para debounce: busca si han pasado X segs sin escribir
    current_time = time.time()
    if (
        get_state(key) != last_search
        and current_time - get_state(f"{key}_last_input_time", 0.0) > debounce
    ):
        set_state(f"{key}_last_search", get_state(key))
        if on_search:
            on_search(get_state(key))

    # Soporte atajo Enter (Streamlit lo hace automáticamente con text_input + button)
