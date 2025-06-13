"""
Kraken Result Card
Componente visual para mostrar atributos, CDEs o catálogos con acciones inline.
"""

import streamlit as st
from typing import Dict, Any, Optional
from kraken.ui.constants import ICONS, COLORS
from kraken.ui.utils import truncate, badge, render_na, icon_label, format_datetime

def render_attribute_result_card(attr: Dict[str, Any], key_suffix: Optional[str] = "") -> Optional[str]:
    """
    Renderiza una tarjeta de resultado para un atributo físico.
    Devuelve la acción tomada ("edit", "link_cde", etc.) o None.
    """
    key_prefix = f"attr_{attr.get('attr_id', 'X')}_{key_suffix}"

    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.markdown(
            f"""
            <div style="border-radius:14px; box-shadow:{COLORS['card_shadow']}; background:{COLORS['card_bg']}; padding:16px 22px 10px 22px; margin-bottom:12px">
                <div style="font-size:1.12em; font-weight:600">{ICONS['attribute']} {truncate(attr.get('physical_name', ''), 38)}</div>
                <div style="font-size:0.98em; color:#555; margin-top:2px">{truncate(attr.get('desc_raw', ''), 68)}</div>
                <div style="margin:8px 0 0 0;">
                    {badge(attr.get('dominio', 'Sin dominio'))}
                    {badge(attr.get('iniciativa', 'Sin iniciativa'), COLORS['accent'])}
                    {badge(f"ID {attr.get('attr_id','')}", COLORS['secondary'])}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        action = None
        if st.button(icon_label(ICONS["edit"], "Editar"), key=f"{key_prefix}_edit"):
            action = "edit"
        if st.button(icon_label(ICONS["cde"], "Vincular CDE"), key=f"{key_prefix}_linkcde"):
            action = "link_cde"
        return action

def render_cde_result_card(cde: Dict[str, Any], key_suffix: Optional[str] = "") -> Optional[str]:
    """
    Renderiza una tarjeta de resultado para un CDE.
    Devuelve la acción tomada ("edit", "view_rules", etc.) o None.
    """
    key_prefix = f"cde_{cde.get('cde_id', 'X')}_{key_suffix}"

    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.markdown(
            f"""
            <div style="border-radius:14px; box-shadow:{COLORS['card_shadow']}; background:{COLORS['card_bg']}; padding:16px 22px 10px 22px; margin-bottom:12px">
                <div style="font-size:1.14em; font-weight:600">{ICONS['cde']} {truncate(cde.get('biz_term', ''), 38)}</div>
                <div style="font-size:0.99em; color:#555; margin-top:2px">{truncate(cde.get('desc_raw', ''), 68)}</div>
                <div style="margin:8px 0 0 0;">
                    {badge(cde.get('prod_domains', 'Sin dominio'))}
                    {badge(f"ID {cde.get('cde_id','')}", COLORS['secondary'])}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        action = None
        if st.button(icon_label(ICONS["edit"], "Editar"), key=f"{key_prefix}_edit"):
            action = "edit"
        if st.button(icon_label(ICONS["rule"], "Reglas DQ"), key=f"{key_prefix}_rules"):
            action = "view_rules"
        return action

def render_catalog_result_card(cat: Dict[str, Any], key_suffix: Optional[str] = "") -> Optional[str]:
    """
    Renderiza una tarjeta de resultado para un catálogo.
    Devuelve la acción tomada ("edit", "link_cde", etc.) o None.
    """
    key_prefix = f"cat_{cat.get('id', 'X')}_{key_suffix}"

    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.markdown(
            f"""
            <div style="border-radius:14px; box-shadow:{COLORS['card_shadow']}; background:{COLORS['card_bg']}; padding:16px 22px 10px 22px; margin-bottom:12px">
                <div style="font-size:1.1em; font-weight:600">{ICONS['catalog']} {truncate(cat.get('table', ''), 38)}</div>
                <div style="font-size:0.98em; color:#555; margin-top:2px">{truncate(cat.get('desc_raw', ''), 68)}</div>
                <div style="margin:8px 0 0 0;">
                    {badge(cat.get('schema', 'Sin schema'), COLORS['secondary'])}
                    {badge(f"ID {cat.get('id','')}", COLORS['primary'])}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        action = None
        if st.button(icon_label(ICONS["edit"], "Editar"), key=f"{key_prefix}_edit"):
            action = "edit"
        if st.button(icon_label(ICONS["cde"], "Vincular CDE"), key=f"{key_prefix}_linkcde"):
            action = "link_cde"
        return action

# Puedes seguir agregando más tipos de tarjeta según lo necesites (ej. feedback, duplicados, reglas DQ, etc.)
