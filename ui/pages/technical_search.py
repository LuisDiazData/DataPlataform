"""
Kraken UI - Búsqueda Técnica de Atributos Físicos (F1, F2)
Permite buscar, filtrar, editar y vincular atributos físicos.
"""

import streamlit as st
from kraken.services.attribute_service import attribute_service
from kraken.services.cde_service import cde_service
from kraken.ui.state import get as get_state, set as set_state, reset as reset_state
from kraken.ui.constants import ICONS, SECTION_TITLES
from kraken.ui.components.search_bar import search_bar
from kraken.ui.components.result_card import render_attribute_result_card
from kraken.ui.components.filters import domain_filter, initiative_filter
from kraken.ui.components.pagination import render_pagination_controls, get_pagination_indices, reset_pagination
from kraken.ui.components.forms import attribute_edit_form
from kraken.ui.components.modals import open_modal
from kraken.ui.components.toast import show_toast
from kraken.ui.components.loading_spinner import spinner

def render_technical_search():
    st.header(f"{ICONS['technical_search']} {SECTION_TITLES['technical_search']}")
    all_domains = attribute_service.list_distinct_dominios()
    all_iniciativas = list({a.iniciativa for a in attribute_service.repo.all() if a.iniciativa})

    # Filtros (sidebar)
    with st.sidebar:
        domain_filter(all_domains)
        initiative_filter(all_iniciativas)

    # Búsqueda
    def do_search(query: str):
        filters = get_state("filters", {})
        domain = filters.get("dominio")
        iniciativa = filters.get("iniciativa")
        with spinner("Buscando atributos..."):
            # Búsqueda filtrada por dominio/iniciativa si aplica
            results = [
                a for a in attribute_service.repo.all()
                if (not domain or a.dominio == domain)
                and (not iniciativa or a.iniciativa == iniciativa)
                and (query.lower() in (a.physical_name or "").lower() or query.lower() in (a.desc_raw or "").lower())
            ]
            set_state("results", [a.__dict__ for a in results])
            reset_pagination()

    search_bar(
        label="Buscar por nombre físico o descripción...",
        key="search_query",
        button_label="Buscar",
        on_search=do_search
    )

    # Render resultados y paginación
    results = get_state("results", [])
    total = len(results)
    page, start, end = get_pagination_indices(total, default_page_size=10)
    render_pagination_controls(total, default_page_size=10)
    show_results = results[start:end]

    st.caption(f"Mostrando {start+1}-{end} de {total} resultados")
    for idx, attr in enumerate(show_results):
        action = render_attribute_result_card(attr, key_suffix=f"_{idx}")
        if action == "edit":
            def body_func():
                return attribute_edit_form(attr, key=f"edit_attr_form_{attr['attr_id']}")
            def on_submit(data):
                updated = attribute_service.edit_attribute(attr['attr_id'], data)
                show_toast("Atributo actualizado correctamente.", type="success")
                # Refrescar resultados
                do_search(get_state("search_query", ""))
            open_modal(
                title=f"Editar atributo {attr.get('physical_name','')}",
                body_func=body_func,
                on_submit=on_submit,
                submit_label="Guardar cambios",
                key=f"edit_attr_modal_{attr['attr_id']}",
            )
        elif action == "link_cde":
            # Ejemplo simple: muestra sugerencias semánticas y permite vincular
            cde_suggestions = cde_service.search(attr["desc_raw"] or attr["physical_name"], limit=5)
            st.info("Sugerencias de CDE para vincular:")
            for cde in cde_suggestions:
                st.markdown(f"- **{cde.biz_term}** (`{cde.cde_id}`): {cde.desc_raw[:80]}")
            # Aquí puedes agregar botón/modal para realizar el vínculo real

    if not show_results:
        st.warning("No se encontraron atributos físicos que cumplan los criterios de búsqueda.")
