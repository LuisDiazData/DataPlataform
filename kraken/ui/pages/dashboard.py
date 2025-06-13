"""
Kraken UI - Dashboard
Panel general: métricas clave, KPIs de CDEs, atributos, reglas DQ, feedback reciente.
"""

import streamlit as st
from datetime import datetime
from kraken.ui.constants import ICONS, SECTION_TITLES
from kraken.services.cde_service import cde_service
from kraken.services.attribute_service import attribute_service
from kraken.services.catalog_service import catalog_service
from kraken.services.quality_rules_service import quality_rules_service
from kraken.services.feedback_service import feedback_service
from kraken.ui.components.utils import big_number, truncate

def render_dashboard():
    st.header(f"{ICONS['dashboard']} {SECTION_TITLES['dashboard']}")
    st.caption("Bienvenido a Kraken. Aquí tienes un resumen de los activos críticos y la actividad reciente de calidad de datos.")

    # KPIs rápidos
    total_cdes = len(cde_service.repo.all())
    total_attrs = len(attribute_service.repo.all())
    total_catalogs = len(catalog_service.repo.all())
    total_rules = len(quality_rules_service.repo.all())
    total_feedback = len(feedback_service.repo.all())

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: big_number(total_attrs, "Atributos físicos")
    with col2: big_number(total_cdes, "CDEs")
    with col3: big_number(total_catalogs, "Catálogos")
    with col4: big_number(total_rules, "Reglas DQ")
    with col5: big_number(total_feedback, "Feedbacks")

    st.divider()

    # Feedback reciente (últimos 5)
    st.subheader(f"{ICONS['feedback']} Feedback más reciente")
    recent_feedback = feedback_service.repo.all()[-5:] if total_feedback > 0 else []
    if recent_feedback:
        for fb in reversed(recent_feedback):
            dt = fb.created_at.strftime("%Y-%m-%d %H:%M") if fb.created_at else "¿?"
            st.markdown(
                f"• <b>{truncate(fb.desc_final, 60)}</b> &mdash; <span style='color:#005fae;'>{fb.user}</span> <span style='font-size:0.92em;color:#666;'>({dt})</span>",
                unsafe_allow_html=True,
            )
    else:
        st.info("Aún no hay feedback registrado en Kraken.")

    st.divider()

    # Dominios más activos (por CDE)
    st.subheader(f"{ICONS['cde']} Dominios con más CDEs")
    domain_counts = {}
    for cde in cde_service.repo.all():
        doms = (cde.prod_domains or "").split("|")
        for dom in doms:
            dom = dom.strip()
            if dom:
                domain_counts[dom] = domain_counts.get(dom, 0) + 1
    if domain_counts:
        top_domains = sorted(domain_counts.items(), key=lambda x: -x[1])[:6]
        st.bar_chart({dom: count for dom, count in top_domains})
    else:
        st.info("Aún no hay dominios de CDEs registrados.")

    st.caption("Panel Kraken v2 | Para Data Stewards y gestión proactiva de activos críticos.")
