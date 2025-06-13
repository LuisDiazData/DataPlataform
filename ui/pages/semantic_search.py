"""
Kraken UI - Búsqueda Semántica de CDEs y Atributos (F3, F2, F4)
Permite buscar CDEs por descripción/nombre y sugerir vínculos Atributo–CDE y CDE–Atributo.
"""

import streamlit as st
from kraken.services.cde_service import cde_service
from kraken.services.attribute_service import attribute_service
from kraken.ui.state import get as get_state, set as set_state, reset as reset_state
from kraken.ui.constants import ICONS, SECTION_TITLES
from kraken.ui.components.search_bar import search_bar
from kraken.ui.components.result_card import render_cde_result_card, render_attribute_result_card
from kraken.ui.components.pagination import render_pagination_controls, get_pagination_indices, reset_pagination
from kraken.ui.components.modals import open_modal
from kraken.ui.components.toast import show_toast
from kraken.ui.components.loading_spinner import spinner

def render_semantic_search():
    st.header(f"{ICONS['semantic_search']} {SECTION_TITLES['semantic_search']}")
    st.caption("Búsqueda semántica sobre CDEs (por nombre de negocio o descripción).")

    # --- F3: Buscar CDE por nombre/desc ---
    def do_cde_search(query: str):
        with spinner("Buscando CDEs..."):
            results = [
                c.__dict__ for c in cde_service.search(query, by="biz_term", fuzzy=False, limit=50)
            ]
            set_state("results", results)
            reset_pagination()
    search_bar(
        label="Buscar CDE por nombre de negocio o descripción...",
        key="semantic_search_query",
        button_label="Buscar",
        on_search=do_cde_search
    )

    results = get_state("results", [])
    total = len(results)
    page, start, end = get_pagination_indices(total, key_prefix="sem_", default_page_size=10)
    render_pagination_controls(total, key_prefix="sem_", default_page_size=10)
    show_results = results[start:end]

    st.caption(f"Mostrando {start+1}-{end} de {total} resultados")
    for idx, cde in enumerate(show_results):
        action = render_cde_result_card(cde, key_suffix=f"_{idx}")
        if action == "edit":
            def body_func():
                return None  # Aquí iría tu cde_edit_form si quieres edición inline
            def on_submit(data):
                # Aquí llamarías a cde_service.edit_cde
                show_toast("CDE actualizado correctamente.", type="success")
                do_cde_search(get_state("semantic_search_query", ""))
            open_modal(
                title=f"Editar CDE {cde.get('biz_term','')}",
                body_func=body_func,
                on_submit=on_submit,
                submit_label="Guardar cambios",
                key=f"edit_cde_modal_{cde.get('cde_id')}",
            )
        elif action == "view_rules":
            # Aquí podrías abrir un modal con reglas DQ asociadas
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
        st.warning("No se encontraron CDEs que cumplan los criterios de búsqueda.")

    # --- F2: Sugerir CDE para un atributo (side feature) ---
    st.divider()
    st.subheader("¿Tienes un atributo físico y quieres sugerir el mejor CDE?")
    attr_query = st.text_input("Nombre/descripción del atributo físico...", key="attr_semantic_query")
    if attr_query:
        with spinner("Buscando sugerencia de CDE..."):
            # Busca semánticamente el CDE más relevante para el atributo ingresado
            cde_suggestions = cde_service.search(attr_query, by="desc_raw", fuzzy=False, limit=5)
            if cde_suggestions:
                st.info("CDE(s) sugeridos:")
                for cde in cde_suggestions:
                    st.markdown(
                        f"- **{cde.biz_term}** (`{cde.cde_id}`): {cde.desc_raw[:80]}"
                    )
            else:
                st.warning("No se encontraron CDEs relevantes para ese atributo.")

    # --- F4: Descubrir atributos físicos desde un CDE seleccionado ---
    st.divider()
    st.subheader("¿Quieres ver atributos físicos relacionados a un CDE?")
    cde_query = st.text_input("Nombre/ID del CDE...", key="cde_attr_query")
    if cde_query:
        with spinner("Buscando atributos físicos..."):
            # Busca semánticamente atributos por la descripción/nombre del CDE ingresado
            attrs = attribute_service.search(cde_query, by="desc_raw", fuzzy=False, limit=10)
            if attrs:
                st.info("Atributos físicos sugeridos:")
                for a in attrs:
                    render_attribute_result_card(a.__dict__, key_suffix=f"_f4_{a.attr_id}")
            else:
                st.warning("No se encontraron atributos relevantes para ese CDE.")
