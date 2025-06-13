"""
Kraken UI - Catálogos Institucionales (F6)
Buscar, filtrar, editar y vincular catálogos a CDEs.
"""

import streamlit as st
from kraken.services.catalog_service import catalog_service
from kraken.services.cde_service import cde_service
from kraken.ui.constants import ICONS, SECTION_TITLES
from kraken.ui.state import get as get_state, set as set_state, reset as reset_state
from kraken.ui.components.filters import domain_filter
from kraken.ui.components.result_card import render_catalog_result_card
from kraken.ui.components.pagination import render_pagination_controls, get_pagination_indices, reset_pagination
from kraken.ui.components.forms import catalog_edit_form
from kraken.ui.components.modals import open_modal
from kraken.ui.components.toast import show_toast
from kraken.ui.components.loading_spinner import spinner

def render_catalogs():
    st.header(f"{ICONS['catalog']} {SECTION_TITLES['catalogs']}")
    all_schemas = list({c.schema for c in catalog_service.repo.all() if c.schema})

    # Filtro por schema
    with st.sidebar:
        if all_schemas:
            domain_filter(all_schemas, label="Schema", filter_key="catalog_schema")

    filters = get_state("filters", {})
    schema = filters.get("catalog_schema")

    # Búsqueda libre
    query = st.text_input("Buscar por nombre de tabla o descripción...", key="catalogs_search")
    with spinner("Buscando catálogos..."):
        cats = catalog_service.repo.all()
        filtered = [
            c for c in cats
            if (not schema or c.schema == schema)
            and (not query or query.lower() in (c.table or "").lower() or query.lower() in (c.desc_raw or "").lower())
        ]
        results = [c.__dict__ for c in filtered]

    total = len(results)
    page, start, end = get_pagination_indices(total, key_prefix="cat_", default_page_size=10)
    render_pagination_controls(total, key_prefix="cat_", default_page_size=10)
    show_results = results[start:end]

    st.caption(f"Mostrando {start+1}-{end} de {total} catálogos")
    for idx, cat in enumerate(show_results):
        action = render_catalog_result_card(cat, key_suffix=f"_{idx}")
        if action == "edit":
            def body_func():
                return catalog_edit_form(cat, key=f"edit_catalog_form_{cat['id']}")
            def on_submit(data):
                updated = catalog_service.edit_catalog(cat['id'], data)
                show_toast("Catálogo actualizado correctamente.", type="success")
            open_modal(
                title=f"Editar catálogo {cat.get('table','')}",
                body_func=body_func,
                on_submit=on_submit,
                submit_label="Guardar cambios",
                key=f"edit_catalog_modal_{cat['id']}",
            )
        elif action == "link_cde":
            # Modal para vincular catálogo a un CDE
            cdes = cde_service.repo.all()
            options = {f"{c.biz_term} ({c.cde_id})": c.cde_id for c in cdes}
            def body_func():
                return st.selectbox("Selecciona CDE a vincular", list(options.keys()), key=f"link_cde_sel_{cat['id']}")
            def on_submit(selected_label):
                cde_id = options.get(selected_label)
                if cde_id:
                    updated = catalog_service.link_catalog_to_cde(cat['id'], cde_id)
                    show_toast(f"Catálogo vinculado a CDE {cde_id}", type="success")
            open_modal(
                title=f"Vincular catálogo {cat.get('table','')} a CDE",
                body_func=body_func,
                on_submit=on_submit,
                submit_label="Vincular",
                key=f"link_catalog_cde_modal_{cat['id']}",
            )

    if not show_results:
        st.warning("No se encontraron catálogos que cumplan los criterios de búsqueda.")

    st.divider()
    st.caption("Vincula catálogos institucionales a CDEs y edítalos de forma sencilla desde aquí.")
