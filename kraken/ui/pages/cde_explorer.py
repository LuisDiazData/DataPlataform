"""
Kraken UI - Explorador de CDEs (F5)
Tabla interactiva, filtros por dominio, acceso a reglas DQ y edición de CDEs.
"""

import streamlit as st
from kraken.services.cde_service import cde_service
from kraken.ui.constants import ICONS, SECTION_TITLES
from kraken.ui.state import get as get_state, set as set_state, reset as reset_state
from kraken.ui.components.filters import domain_filter
from kraken.ui.components.result_card import render_cde_result_card
from kraken.ui.components.pagination import render_pagination_controls, get_pagination_indices, reset_pagination
from kraken.ui.components.modals import open_modal
from kraken.ui.components.toast import show_toast
from kraken.ui.components.forms import cde_edit_form
from kraken.ui.components.loading_spinner import spinner

def render_cde_explorer():
    st.header(f"{ICONS['cde']} {SECTION_TITLES['cde_explorer']}")
    all_domains = cde_service.list_distinct_domains()

    # Filtro por dominio productor
    with st.sidebar:
        domain_filter(all_domains, label="Dominio productor", filter_key="cde_domain")

    filters = get_state("filters", {})
    domain = filters.get("cde_domain")

    with spinner("Cargando CDEs..."):
        # Agrupa por dominio y filtra
        grouped = cde_service.group_cdes_by_domain()
        domain_cdes = grouped.get(domain, []) if domain else [cde for group in grouped.values() for cde in group]
        results = [cde.__dict__ for cde in domain_cdes]

    total = len(results)
    page, start, end = get_pagination_indices(total, key_prefix="cde_", default_page_size=10)
    render_pagination_controls(total, key_prefix="cde_", default_page_size=10)
    show_results = results[start:end]

    st.caption(f"Mostrando {start+1}-{end} de {total} CDEs")
    for idx, cde in enumerate(show_results):
        action = render_cde_result_card(cde, key_suffix=f"_explorer_{idx}")
        if action == "edit":
            def body_func():
                return cde_edit_form(cde, key=f"edit_cde_form_{cde['cde_id']}")
            def on_submit(data):
                updated = cde_service.edit_cde(cde['cde_id'], data)
                show_toast("CDE actualizado correctamente.", type="success")
            open_modal(
                title=f"Editar CDE {cde.get('biz_term','')}",
                body_func=body_func,
                on_submit=on_submit,
                submit_label="Guardar cambios",
                key=f"edit_cde_modal_{cde['cde_id']}",
            )
        elif action == "view_rules":
            rules = cde_service.get_quality_rules(cde["cde_id"])
            msg = "\n\n".join(
                f"- **{r.rule_natural}**" for r in rules
            ) or "Este CDE no tiene reglas de calidad registradas."
            open_modal(
                title=f"Reglas de calidad para CDE {cde.get('biz_term','')}",
                body_func=lambda: st.markdown(msg),
                key=f"rules_modal_{cde.get('cde_id')}",
            )

    if not show_results:
        st.warning("No se encontraron CDEs para este dominio.")

    st.divider()
    st.caption("Tip: Usa el filtro de dominio para agrupar los CDEs y accede a sus reglas de calidad y edición rápida desde cada tarjeta.")

