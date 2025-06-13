"""
Helpers de UI Kraken
Truncar texto, formatear badges, markdown seguro, tooltips y más.
"""

import streamlit as st
from datetime import datetime
from typing import Optional

def truncate(text: str, length: int = 48) -> str:
    """
    Acorta un texto largo y agrega '...'.
    """
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[:length-3] + "..."

def badge(label: str, color: str = "#005fae") -> str:
    """
    Devuelve HTML para un badge coloreado.
    """
    return f"<span style='background:{color}; color:#fff; padding:2px 8px; border-radius:8px; font-size:0.92em; margin-right:6px'>{label}</span>"

def safe_markdown(md: str, **kwargs):
    """
    Renderiza markdown seguro (desactiva HTML por defecto).
    """
    st.markdown(md, unsafe_allow_html=False, **kwargs)

def tooltip(label: str, tooltip: str) -> str:
    """
    Devuelve HTML de texto con tooltip al pasar el mouse.
    """
    return f"<span title='{tooltip}' style='text-decoration:underline dotted #54b4d3; cursor:help'>{label}</span>"

def render_na(val: Optional[str], placeholder: str = "N/A") -> str:
    """
    Muestra un valor o 'N/A' estilizado.
    """
    if val is None or str(val).strip() == "":
        return f"<span style='color:#aaa;font-style:italic'>{placeholder}</span>"
    return str(val)

def format_datetime(dt: Optional[datetime], fmt: str = "%Y-%m-%d %H:%M") -> str:
    """
    Formatea un datetime o regresa 'N/A'.
    """
    if not dt:
        return "<span style='color:#aaa;font-style:italic'>N/A</span>"
    return dt.strftime(fmt)

def icon_label(icon: str, text: str) -> str:
    """
    Combina un emoji/ícono con texto.
    """
    return f"{icon} {text}"

def big_number(value: int, label: str, color: str = "#005fae"):
    """
    Muestra un 'big number' en Dashboard.
    """
    st.markdown(
        f"""
        <div style="display:flex;align-items:flex-end;gap:10px;">
            <span style="font-size:2.3em; color:{color}; font-weight:bold">{value:,}</span>
            <span style="color:#444; font-size:1em">{label}</span>
        </div>
        """, unsafe_allow_html=True
    )
