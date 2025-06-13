"""
Kraken UI - Reglas de Calidad de Datos (DQ)
Consulta, filtra, edita y explora reglas DQ asociadas a los CDEs.
"""

import streamlit as st
from kraken.services.quality_rules_service import quality_rules_service
from kraken.ui.constants import ICONS, SECTION_TITLES
from kraken.ui.state import get as get_state, set as set_state, reset as reset_state
from kraken.ui.components.filters import dimension_filter
from kraken.ui.components.pagination import render_pagination_controls, get_pagination_indices, reset_pagination
from kraken.ui.components.forms import rule_edit_form
from kraken.ui.components.modals import open_modal
from kraken.ui.components.toast import show_toast
from kraken.ui.components.loading_spinner import spinner
from kraken.ui.components.utils import truncate

def render_quality_rules():
    st.header(f"{ICONS['rule']} {SECTION_TITLES['quality_rules']}")
    all_dims = quality_rules_service.list_distinct_dimensions()

    # Filtro por dimensión
    with st.sidebar:
        if all_dims:
            dimension_filter(all_dims, label="Dimensión DQ", filter_key="dq_dimension")

    filters = get_state("filters", {})
    dimension = filters.get("dq_dimension")

    # Búsqueda libre
    query = st.text_input("Buscar por texto en regla (natural o estándar)...", key="dq_rules_search")
    with spinner("Buscando reglas..."):
        rules = quality_rules_service.repo.all()
        filtered = [
            r for r in rules
            if (not dimension or r.dimension == dimension)
            and (not query or query.lower() in (r.rule_natural or "").lower() or query.lower() in (r.rule_standard or "").lower())
        ]
        results = filtered

    total = len(results)
    page, start, end = get_pagination_indices(total, key_prefix="dq_", default_page_size=10)
    render_pagination_controls(total, key_prefix="dq_", default_page_size=10)
    show_rules = results[start:end]

    st.caption(f"Mostrando {start+1}-{end} de {total} reglas")
    for rule in show_rules:
        st.markdown(
            f"<b>Regla natural:</b> {truncate(rule.rule_natural, 70)}<br>"
            f"<b>Regla estándar:</b> {truncate(rule.rule_standard, 70)}<br>"
            f"<b>Dimensión:</b> {rule.dimension or '—'} | "
            f"<b>CDE:</b> {rule.cde_id or '—'}",
            unsafe_allow_html=True,
        )
        if st.button(f"Editar", key=f"edit_rule_btn_{rule.id}"):
            def body_func():
                return rule_edit_form(rule.__dict__, key=f"edit_rule_form_{rule.id}")
            def on_submit(data):
                updated = quality_rules_service.edit_rule(rule.id, data)
                show_toast("Regla de calidad actualizada.", type="success")
            open_modal(
                title="Editar regla de calidad",
                body_func=body_func,
                on_submit=on_submit,
                submit_label="Guardar cambios",
                key=f"edit_rule_modal_{rule.id}",
            )

    if not show_rules:
        st.info("No se encontraron reglas que cumplan los criterios de búsqueda.")

    st.divider()
    st.caption("Gestiona y consulta todas las reglas de calidad de datos asociadas a los CDEs.")
