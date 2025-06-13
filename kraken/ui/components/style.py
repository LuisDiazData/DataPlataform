"""
Kraken UI Styles
Inyecta CSS global (claro/oscuro), define helpers de tema y permite alternar tema dinámicamente.

Los archivos ``kraken.css``, ``kraken_dark.css`` y ``logo.svg`` deben ubicarse en
``kraken/ui/assets/``. Si no están presentes, la aplicación mostrará advertencias
y usará estilos por defecto.
"""

import streamlit as st
from pathlib import Path
from kraken.core.config import get_config

_ASSET_PATH = Path(__file__).parent.parent / "assets"

def load_css(filename: str):
    css_file = _ASSET_PATH / filename
    if not css_file.exists():
        st.warning(f"Archivo CSS no encontrado: {css_file}")
        return
    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def apply_theme():
    """
    Aplica el tema Kraken (claro u oscuro según settings).
    """
    config = get_config()
    st.markdown("<meta name='viewport' content='width=device-width, initial-scale=1'>", unsafe_allow_html=True)
    # Aplica CSS principal
    load_css("kraken.css")
    # Si dark mode está habilitado, aplica CSS adicional
    if getattr(config.ui, "enable_dark_mode", False):
        dark_on = st.session_state.get("dark_mode", False)
        if dark_on:
            load_css("kraken_dark.css")

def theme_toggle_button():
    """
    Renderiza un botón para alternar el tema claro/oscuro en session_state.
    """
    config = get_config()
    if not getattr(config.ui, "enable_dark_mode", False):
        return  # No mostrar si no está permitido

    dark_on = st.session_state.get("dark_mode", False)
    label = "🌙 Modo oscuro" if not dark_on else "☀️ Modo claro"
    if st.sidebar.button(label, key="theme_toggle"):
        st.session_state["dark_mode"] = not dark_on
        st.experimental_rerun()

def kraken_logo(height: int = 48):
    """
    Muestra el logo Kraken corporativo en el sidebar o header.
    """
    logo_path = _ASSET_PATH / "logo.svg"
    if logo_path.exists():
        st.sidebar.image(str(logo_path), use_column_width=False, width=height)
    else:
        st.sidebar.markdown("**KRAKEN**")

def inject_variables():
    """
    Inyecta variables CSS útiles para todos los componentes.
    """
    st.markdown("""
    <style>
        :root {
            --kraken-primary: #005fae;
            --kraken-secondary: #54b4d3;
            --kraken-accent: #ff9800;
            --kraken-bg: #f8fafc;
            --kraken-card-radius: 18px;
            --kraken-shadow: 0 4px 16px rgba(0,0,0,0.07);
        }
    </style>
    """, unsafe_allow_html=True)
