"""
Kraken UI - Punto de entrada principal de Streamlit
Configura tema, navegación, prepara entorno y llama a las páginas.
"""

import streamlit as st
from kraken.ui.components.style import apply_theme, theme_toggle_button, kraken_logo
from kraken.ui.router import render_page
from kraken.services.ingest.ingestor import ingest_all_from_config
from kraken.core.database import init_db
from kraken.infra.faiss_manager import get_faiss_manager

def prepare_kraken_backend():
    """
    Asegura que la base, embeddings y FAISS estén listos.
    Ejecuta ingestores si es la primera vez.
    """
    init_db(create_all=True)  # Crea tablas si no existen
    ingest_all_from_config()  # Ingesta los excels/base
    # Puedes agregar aquí lógica para construir índices FAISS si están vacíos
    # get_faiss_manager("attributes_desc").build_index([...], [...], force=False)
    # get_faiss_manager("cdes_desc").build_index([...], [...], force=False)

def main():
    st.set_page_config(page_title="Kraken Data Steward", layout="wide")
    apply_theme()
    theme_toggle_button()
    kraken_logo(height=48)
    # Preparar base y entorno si es la primera vez (o al recargar)
    with st.spinner("Inicializando Kraken..."):
        prepare_kraken_backend()
    render_page()

if __name__ == "__main__":
    main()
