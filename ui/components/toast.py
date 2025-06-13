"""
Kraken UI - Toast
Mensajes instantáneos tipo snackbar (éxito, error, warning, info) para feedback inmediato.
"""

import streamlit as st

def show_toast(
    message: str,
    type: str = "success",
    duration: int = 4,
    key: str = "kraken_toast"
):
    """
    Muestra un toast tipo snackbar (Streamlit ≥1.25) o un aviso visual alternativo.
    type: "success", "error", "warning", "info"
    """
    # Preferencia: usar st.toast si existe
    if hasattr(st, "toast"):
        if type == "success":
            st.toast(message, icon="✅")
        elif type == "error":
            st.toast(message, icon="❌")
        elif type == "warning":
            st.toast(message, icon="⚠️")
        elif type == "info":
            st.toast(message, icon="ℹ️")
        else:
            st.toast(message)
    else:
        # Fallback: una alerta visual arriba de la página
        if type == "success":
            st.success(message)
        elif type == "error":
            st.error(message)
        elif type == "warning":
            st.warning(message)
        elif type == "info":
            st.info(message)
        else:
            st.info(message)
