"""
Kraken UI - Filtros reutilizables
Sidebar y barra superior de filtros para atributos, CDEs, catálogos, reglas, feedback, etc.
"""

import streamlit as st
from typing import List, Dict, Any, Optional, Callable
from kraken.ui.state import get as get_state, set as set_state, set_filter
from kraken.ui.constants import ICONS

def domain_filter(
    domains: List[str],
    label: str = "Dominio",
    filter_key: str = "dominio",
    show_all: bool = True,
    default: Optional[str] = None,
):
    """
    Renderiza un selectbox para dominio, y actualiza el filtro global.
    """
    options = ["(Todos)"] + sorted(domains) if show_all else sorted(domains)
    current = get_state("filters", {}).get(filter_key, default or options[0])
    value = st.sidebar.selectbox(f"{ICONS['attribute']} {label}", options, index=options.index(current) if current in options else 0)
    if value != current:
        set_filter(filter_key, None if value == "(Todos)" else value)

def initiative_filter(
    iniciativas: List[str],
    label: str = "Iniciativa",
    filter_key: str = "iniciativa",
    show_all: bool = True,
    default: Optional[str] = None,
):
    options = ["(Todas)"] + sorted(iniciativas) if show_all else sorted(iniciativas)
    current = get_state("filters", {}).get(filter_key, default or options[0])
    value = st.sidebar.selectbox(f"🎯 {label}", options, index=options.index(current) if current in options else 0)
    if value != current:
        set_filter(filter_key, None if value == "(Todas)" else value)

def dimension_filter(
    dimensiones: List[str],
    label: str = "Dimensión DQ",
    filter_key: str = "dimension",
    show_all: bool = True,
    default: Optional[str] = None,
):
    options = ["(Todas)"] + sorted(dimensiones) if show_all else sorted(dimensiones)
    current = get_state("filters", {}).get(filter_key, default or options[0])
    value = st.sidebar.selectbox(f"{ICONS['rule']} {label}", options, index=options.index(current) if current in options else 0)
    if value != current:
        set_filter(filter_key, None if value == "(Todas)" else value)

def user_filter(
    users: List[str],
    label: str = "Usuario",
    filter_key: str = "user",
    show_all: bool = True,
    default: Optional[str] = None,
):
    options = ["(Todos)"] + sorted(users) if show_all else sorted(users)
    current = get_state("filters", {}).get(filter_key, default or options[0])
    value = st.sidebar.selectbox(f"👤 {label}", options, index=options.index(current) if current in options else 0)
    if value != current:
        set_filter(filter_key, None if value == "(Todos)" else value)

def sidebar_filters(
    domains: List[str] = [],
    iniciativas: List[str] = [],
    dimensiones: List[str] = [],
    users: List[str] = [],
):
    """
    Llama los filtros disponibles en el sidebar.
    """
    if domains:
        domain_filter(domains)
    if iniciativas:
        initiative_filter(iniciativas)
    if dimensiones:
        dimension_filter(dimensiones)
    if users:
        user_filter(users)

# Para filtros en barra superior, puedes hacer variantes que usen st.columns en vez de sidebar.
