"""
Kraken UI - Métricas y Analítica de Uso
Panel para admins: uso de la herramienta, actividad, tiempos de respuesta.
"""

import streamlit as st
from datetime import datetime
from pathlib import Path
import pandas as pd
from kraken.core.config import get_config
from kraken.ui.constants import ICONS, SECTION_TITLES

def render_metrics():
    st.header(f"{ICONS['metrics']} {SECTION_TITLES['metrics']}")
    st.caption("Analítica de uso, actividad y performance de Kraken. (Solo visible para administradores)")

    # Intenta leer un archivo de métricas si existe
    metrics_path = Path(get_config().files.data_dir) / "metrics.csv"
    if metrics_path.exists():
        df = pd.read_csv(metrics_path)
        # Esperado: columnas como "timestamp", "user", "action", "entity", "elapsed_ms"
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        st.subheader("Acciones recientes")
        st.dataframe(df.sort_values("timestamp", ascending=False).head(30), use_container_width=True)

        st.divider()
        st.subheader("Usuarios más activos")
        if "user" in df.columns:
            top_users = df["user"].value_counts().head(10)
            st.bar_chart(top_users)

        st.divider()
        st.subheader("Tiempos de respuesta")
        if "elapsed_ms" in df.columns:
            st.line_chart(df.sort_values("timestamp")["elapsed_ms"].rolling(10).mean(), use_container_width=True)
            st.caption("Promedio móvil de los últimos 10 eventos (ms)")

        st.divider()
        st.subheader("Resumen por acción")
        if "action" in df.columns:
            action_counts = df["action"].value_counts()
            st.bar_chart(action_counts)
    else:
        st.info(
            f"No se encontró archivo de métricas en {metrics_path}. Ejecuta operaciones para generar analítica."
        )

    st.caption("Panel de métricas Kraken v2 | Analítica para monitoreo y mejora continua.")
