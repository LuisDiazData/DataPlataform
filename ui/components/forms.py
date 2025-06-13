"""
Kraken UI - Forms
Formularios reutilizables para edición y alta rápida de atributos, CDEs, catálogos, reglas DQ y feedback.
Devuelven un dict con los datos o None si se cancela.
"""

import streamlit as st
from typing import Optional, Dict, Any

def attribute_edit_form(
    initial: Dict[str, Any],
    key: str = "attr_edit_form",
    submit_label: str = "Guardar cambios"
) -> Optional[Dict[str, Any]]:
    """
    Formulario para editar un atributo físico.
    """
    with st.form(key=key):
        physical_name = st.text_input("Nombre físico", value=initial.get("physical_name", ""))
        desc_raw = st.text_area("Descripción", value=initial.get("desc_raw", ""))
        dominio = st.text_input("Dominio", value=initial.get("dominio", ""))
        iniciativa = st.text_input("Iniciativa", value=initial.get("iniciativa", ""))
        submitted = st.form_submit_button(submit_label)
        if submitted:
            return {
                "physical_name": physical_name.strip(),
                "desc_raw": desc_raw.strip(),
                "dominio": dominio.strip(),
                "iniciativa": iniciativa.strip(),
            }
    return None

def cde_edit_form(
    initial: Dict[str, Any],
    key: str = "cde_edit_form",
    submit_label: str = "Guardar cambios"
) -> Optional[Dict[str, Any]]:
    """
    Formulario para editar un CDE.
    """
    with st.form(key=key):
        biz_term = st.text_input("Nombre de negocio", value=initial.get("biz_term", ""))
        desc_raw = st.text_area("Descripción", value=initial.get("desc_raw", ""))
        prod_domains = st.text_input("Dominios productores (separados por |)", value=initial.get("prod_domains", ""))
        cons_domains = st.text_input("Dominios consumidores (separados por |)", value=initial.get("cons_domains", ""))
        submitted = st.form_submit_button(submit_label)
        if submitted:
            return {
                "biz_term": biz_term.strip(),
                "desc_raw": desc_raw.strip(),
                "prod_domains": prod_domains.strip(),
                "cons_domains": cons_domains.strip(),
            }
    return None

def catalog_edit_form(
    initial: Dict[str, Any],
    key: str = "catalog_edit_form",
    submit_label: str = "Guardar cambios"
) -> Optional[Dict[str, Any]]:
    """
    Formulario para editar un catálogo institucional.
    """
    with st.form(key=key):
        schema = st.text_input("Schema", value=initial.get("schema", ""))
        table = st.text_input("Tabla", value=initial.get("table", ""))
        desc_raw = st.text_area("Descripción", value=initial.get("desc_raw", ""))
        atributos = st.text_area("Atributos", value=initial.get("atributos", ""))
        ejemplo_datos = st.text_area("Ejemplo de datos", value=initial.get("ejemplo_datos", ""))
        submitted = st.form_submit_button(submit_label)
        if submitted:
            return {
                "schema": schema.strip(),
                "table": table.strip(),
                "desc_raw": desc_raw.strip(),
                "atributos": atributos.strip(),
                "ejemplo_datos": ejemplo_datos.strip(),
            }
    return None

def rule_edit_form(
    initial: Dict[str, Any],
    key: str = "rule_edit_form",
    submit_label: str = "Guardar cambios"
) -> Optional[Dict[str, Any]]:
    """
    Formulario para editar una regla de calidad.
    """
    with st.form(key=key):
        rule_natural = st.text_area("Regla natural (lenguaje humano)", value=initial.get("rule_natural", ""))
        rule_standard = st.text_area("Regla estándar", value=initial.get("rule_standard", ""))
        dimension = st.text_input("Dimensión DQ", value=initial.get("dimension", ""))
        field_type = st.text_input("Tipo de campo", value=initial.get("field_type", ""))
        max_length = st.number_input("Longitud máxima", min_value=1, max_value=2000, value=initial.get("max_length", 100))
        scale = st.number_input("Escala", min_value=0, max_value=100, value=initial.get("scale", 0))
        pattern = st.text_input("Patrón", value=initial.get("pattern", ""))
        example = st.text_input("Ejemplo", value=initial.get("example", ""))
        submitted = st.form_submit_button(submit_label)
        if submitted:
            return {
                "rule_natural": rule_natural.strip(),
                "rule_standard": rule_standard.strip(),
                "dimension": dimension.strip(),
                "field_type": field_type.strip(),
                "max_length": int(max_length),
                "scale": int(scale),
                "pattern": pattern.strip(),
                "example": example.strip(),
            }
    return None

def feedback_form(
    attr_id: int,
    user: str,
    key: str = "feedback_form",
    submit_label: str = "Enviar feedback"
) -> Optional[Dict[str, Any]]:
    """
    Formulario para registrar feedback de usuario sobre un atributo físico.
    """
    with st.form(key=key):
        desc_original = st.text_area("Descripción original", value="")
        desc_final = st.text_area("Descripción sugerida/corregida", value="")
        score = st.slider("Score de relevancia", min_value=0.0, max_value=1.0, value=1.0, step=0.01)
        comment = st.text_area("Comentario (opcional)", value="")
        submitted = st.form_submit_button(submit_label)
        if submitted:
            return {
                "attr_id": attr_id,
                "user": user,
                "desc_original": desc_original.strip(),
                "desc_final": desc_final.strip(),
                "score": float(score),
                "comment": comment.strip(),
            }
    return None
