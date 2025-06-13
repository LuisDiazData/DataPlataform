"""
Kraken UI - Modals
API sencilla para abrir modales con formularios, confirmaciones o mensajes.
"""

import streamlit as st
from typing import Callable, Optional, Any

def open_modal(
    title: str,
    body_func: Callable[[], Optional[Any]],
    on_submit: Optional[Callable[[Any], None]] = None,
    on_cancel: Optional[Callable[[], None]] = None,
    submit_label: str = "Guardar",
    cancel_label: str = "Cancelar",
    key: str = "modal",
):
    """
    Abre un modal con un título y un cuerpo dado por una función (por ejemplo, un formulario).
    Llama on_submit(data) si se envía, on_cancel() si se cancela.
    """
    with st.modal(title, key=key):
        data = body_func()
        cols = st.columns([1, 1])
        submitted = cols[0].button(submit_label, key=f"{key}_submit")
        cancelled = cols[1].button(cancel_label, key=f"{key}_cancel")
        if submitted:
            if on_submit and data is not None:
                on_submit(data)
            st.experimental_rerun()
        elif cancelled:
            if on_cancel:
                on_cancel()
            st.experimental_rerun()

def confirm_modal(
    title: str,
    message: str,
    on_confirm: Callable[[], None],
    on_cancel: Optional[Callable[[], None]] = None,
    confirm_label: str = "Sí",
    cancel_label: str = "No",
    key: str = "confirm_modal",
):
    """
    Abre un modal de confirmación (Sí/No).
    """
    with st.modal(title, key=key):
        st.write(message)
        cols = st.columns([1, 1])
        confirmed = cols[0].button(confirm_label, key=f"{key}_yes")
        cancelled = cols[1].button(cancel_label, key=f"{key}_no")
        if confirmed:
            on_confirm()
            st.experimental_rerun()
        elif cancelled:
            if on_cancel:
                on_cancel()
            st.experimental_rerun()

def info_modal(
    title: str,
    message: str,
    key: str = "info_modal"
):
    """
    Modal sólo informativo.
    """
    with st.modal(title, key=key):
        st.write(message)
        st.button("Cerrar", key=f"{key}_close", on_click=st.experimental_rerun)

