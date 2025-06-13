"""
Kraken UI - Gestión de Duplicados
Panel para consultar, filtrar, aprobar/rechazar y ver historial de duplicados de CDEs.
"""

import streamlit as st
from datetime import datetime
from kraken.services.duplicate_service import duplicate_service
from kraken.services.cde_service import cde_service
from kraken.ui.constants import ICONS, SECTION_TITLES
from kraken.ui.state import get as get_state, set as set_state, reset as reset_state
from kraken.ui.components.pagination import render_pagination_controls, get_pagination_indices, reset_pagination
from kraken.ui.components.modals import confirm_modal, open_modal
from kraken.ui.components.toast import show_toast
from kraken.ui.components.loading_spinner import spinner

def render_duplicates():
    st.header(f"{ICONS['duplicate']} {SECTION_TITLES['duplicates']}")
    st.caption("Detecta y resuelve duplicados de CDEs. Aprueba o rechaza sugerencias y consulta el historial.")

    # Muestra historial reciente
    all_dupes = duplicate_service.repo.all()
    total = len(all_dupes)
    page, start, end = get_pagination_indices(total, key_prefix="dup_", default_page_size=10)
    render_pagination_controls(total, key_prefix="dup_", default_page_size=10)
    show_dupes = all_dupes[start:end]

    st.caption(f"Mostrando {start+1}-{end} de {total} posibles duplicados")
    for dupe in show_dupes:
        cde_a = cde_service.get_by_id(dupe.cde_a)
        cde_b = cde_service.get_by_id(dupe.cde_b)
        dt = dupe.resolved_at.strftime("%Y-%m-%d %H:%M") if dupe.resolved_at else "¿?"
        label = (
            f"**{cde_a.biz_term if cde_a else dupe.cde_a}**  ⟷  "
            f"**{cde_b.biz_term if cde_b else dupe.cde_b}**"
        )
        status = (
            "✅ Duplicados" if dupe.is_duplicate else "❌ No duplicados"
        )
        user = dupe.resolved_by or "—"
        st.markdown(
            f"{label} <br>"
            f"<span style='color:#005fae'>{status}</span> | "
            f"<span style='font-size:0.95em;color:#666;'>{dt} | {user}</span> "
            f"{'| <i>'+dupe.comment+'</i>' if dupe.comment else ''}",
            unsafe_allow_html=True,
        )
        # Permitir editar decisión si se desea
        if st.button(f"Modificar decisión", key=f"edit_decision_{dupe.id}"):
            def on_confirm_duplicate():
                duplicate_service.resolve_duplicate(
                    dupe.cde_a,
                    dupe.cde_b,
                    True,
                    user,
                    comment="Modificado",
                )
                show_toast("Marcado como duplicados.", type="success")
                st.rerun()

            def on_confirm_no_duplicate():
                duplicate_service.resolve_duplicate(
                    dupe.cde_a,
                    dupe.cde_b,
                    False,
                    user,
                    comment="Modificado",
                )
                show_toast("Marcado como NO duplicados.", type="warning")
                st.rerun()
            open_modal(
                title="¿Modificar la decisión de duplicidad?",
                body_func=lambda: st.write("Selecciona nueva decisión para este par:"),
                on_submit=on_confirm_duplicate,
                submit_label="Duplicados",
                key=f"modal_dup_yes_{dupe.id}"
            )
            open_modal(
                title="¿Modificar la decisión de duplicidad?",
                body_func=lambda: st.write("Selecciona nueva decisión para este par:"),
                on_submit=on_confirm_no_duplicate,
                submit_label="No duplicados",
                key=f"modal_dup_no_{dupe.id}"
            )

    if not show_dupes:
        st.info("No hay registros de duplicados en el sistema.")

    st.divider()
    st.caption("Revisa, aprueba o rechaza duplicados y mantén la calidad de los CDEs.")
