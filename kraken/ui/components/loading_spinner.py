"""
Kraken UI - Loading Spinner
Context manager para mostrar spinner con mensaje durante operaciones lentas.
"""

import streamlit as st
from contextlib import contextmanager
from typing import Optional

@contextmanager
def spinner(message: str = "Cargando..."):
    """
    Context manager para mostrar spinner y evitar flicker.
    Uso:
        with spinner("Procesando..."):
            # operación lenta
    """
    with st.spinner(message):
        yield

def show_spinner_if(condition: bool, message: str = "Cargando..."):
    """
    Muestra spinner sólo si se cumple la condición (útil para await/callback).
    """
    if condition:
        st.spinner(message)
