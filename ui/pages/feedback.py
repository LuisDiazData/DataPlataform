"""
Kraken UI - Feedback y Correcciones (F7)
Panel para consultar, filtrar y exportar feedback, y para registrar nuevos comentarios/correcciones.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
from kraken.services.feedback_service import feedback_service
from kraken.services.attribute_service import attribute_service
from kraken.ui.constants import ICONS, SECTION_TITLES
from kraken.ui.state import get as get_state, set as set_state, reset as reset_state
from kraken.ui.components.forms import feedback_form
from kraken.ui.components.pagination import render_pagination_controls, get_pagination_indices, reset_pagination
from kraken.ui.components.toast import show_toast
from kraken.ui.components.loading_spinner import spinner

def render_feedback():
    st.header(f"{ICONS['feedback']} {SECTION_TITLES['feedback']}")
    st.caption("Consulta el feedback registrado por los usuarios, filtra y exporta. También puedes enviar feedback sobre un atributo físico.")

    # Filtro por usuario
    all_feedback = feedback_service.repo.all()
    users = sorted(set(f.user for f in all_feedback if f.user))
    user = st.selectbox("Filtrar por usuario", ["(Todos)"] + users, key="feedback_user")
    user_filter = None if user == "(Todos)" else user

    # Feedbacks filtrados
    feedbacks = [
        fb for fb in all_feedback
        if (not user_filter or fb.user == user_filter)
    ]
    feedbacks = sorted(feedbacks, key=lambda f: f.created_at or datetime.min, reverse=True)
    total = len(feedbacks)
    page, start, end = get_pagination_indices(total, key_prefix="fb_", default_page_size=10)
    render_pagination_controls(total, key_prefix="fb_", default_page_size=10)
    show_feedbacks = feedbacks[start:end]

    st.caption(f"Mostrando {start+1}-{end} de {total} feedbacks")
    for fb in show_feedbacks:
        dt = fb.created_at.strftime("%Y-%m-%d %H:%M") if fb.created_at else "¿?"
        st.markdown(
            f"• <b>{fb.desc_final or '[Sin corrección]'}</b><br>"
            f"<span style='color:#005fae'>{fb.user}</span> <span style='font-size:0.93em;color:#666;'>({dt})</span> "
            f"{' | <i>' + fb.comment + '</i>' if fb.comment else ''}",
            unsafe_allow_html=True,
        )

    if not show_feedbacks:
        st.info("No se encontró feedback con los filtros seleccionados.")

    st.divider()

    # Exportar feedback a CSV
    st.subheader("Exportar feedback")
    export_path = st.text_input("Ruta para exportar feedback a CSV (servidor local):", value="kraken_feedback.csv")
    if st.button("Exportar a CSV", key="feedback_export_btn"):
        if export_path.strip():
            count = feedback_service.export_feedback_csv(Path(export_path.strip()))
            show_toast(f"Feedback exportado ({count} registros) a {export_path}", type="success")
        else:
            show_toast("Por favor ingresa una ruta válida.", type="warning")

    st.divider()

    # Enviar feedback sobre un atributo físico
    st.subheader("Enviar nuevo feedback")
    attrs = attribute_service.repo.all()
    attr_options = {f"{a.physical_name} ({a.attr_id})": a.attr_id for a in attrs}
    selected = st.selectbox("Selecciona atributo físico", list(attr_options.keys()), key="feedback_attr_sel")
    user = st.text_input("Tu usuario:", value="", key="feedback_user_input")
    if selected and user:
        attr_id = attr_options[selected]
        form_data = feedback_form(attr_id, user, key=f"feedback_form_{attr_id}")
        if form_data:
            fb = feedback_service.register_feedback(**form_data)
            show_toast("¡Feedback registrado correctamente!", type="success")
            st.experimental_rerun()
    else:
        st.info("Selecciona un atributo físico y escribe tu usuario para enviar feedback.")

    st.caption("Tu retroalimentación es fundamental para mejorar la calidad de los activos de datos.")
