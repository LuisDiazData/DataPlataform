"""
Kraken Search Service
Motor de búsqueda unificado: fuzzy, semántica y combinada, para atributos, CDEs y catálogos.
"""

from typing import List, Dict, Any, Literal, Optional, Tuple
from rapidfuzz import process, fuzz
from kraken.repositories.attribute_repo import attribute_repo
from kraken.repositories.cde_repo import cde_repo
from kraken.repositories.catalog_repo import catalog_repo
from kraken.infra.faiss_manager import get_faiss_manager
from kraken.core.config import get_config
from kraken.core.utils import clean_text

# --- Búsqueda fuzzy ---

def fuzzy_search(
    query: str,
    items: List[Dict[str, Any]],
    field: str,
    top_k: int = 10,
    threshold: int = 70
) -> List[Dict[str, Any]]:
    """
    Busca usando fuzzy matching sobre el campo dado.
    Devuelve una lista de dicts con 'item', 'score', 'method'.
    """
    choices = [(item[field], idx) for idx, item in enumerate(items) if item.get(field)]
    results = process.extract(
        clean_text(query),
        {c[1]: clean_text(c[0]) for c in choices},
        scorer=fuzz.WRatio,
        limit=top_k
    )
    # Filtra por threshold
    filtered = [
        {"item": items[idx], "score": score/100.0, "method": "fuzzy"}
        for idx, score, _ in results if score >= threshold
    ]
    return filtered

# --- Búsqueda semántica FAISS ---

def semantic_search(
    query: str,
    index_name: str,
    id_to_item: Dict[str, Dict[str, Any]],
    top_k: int = 10,
    threshold: float = 0.65
) -> List[Dict[str, Any]]:
    """
    Busca usando embeddings + FAISS sobre el índice dado.
    Devuelve lista de dicts con 'item', 'score', 'method'.
    """
    mgr = get_faiss_manager(index_name)
    faiss_results = mgr.search(query, top_k=top_k)
    filtered = [
        {
            "item": id_to_item.get(hit["id"], {}),
            "score": float(hit["score"]),
            "method": "semantic"
        }
        for hit in faiss_results
        if hit["score"] >= threshold and hit["id"] in id_to_item
    ]
    return filtered

# --- Búsqueda híbrida ---

def hybrid_search(
    query: str,
    items: List[Dict[str, Any]],
    fuzzy_field: str,
    index_name: str,
    id_field: str,
    top_k: int = 10,
    fuzzy_threshold: int = 70,
    semantic_threshold: float = 0.65
) -> List[Dict[str, Any]]:
    """
    Combina fuzzy y semántico, elimina duplicados y pondera scores.
    """
    # Fuzzy
    fuzzy_results = fuzzy_search(query, items, fuzzy_field, top_k=top_k, threshold=fuzzy_threshold)
    # Mapa ID->item
    id_to_item = {str(item[id_field]): item for item in items}
    # Semántico
    semantic_results = semantic_search(query, index_name, id_to_item, top_k=top_k, threshold=semantic_threshold)
    # Fusionar resultados únicos
    seen_ids = set()
    combined = []
    for res in sorted(fuzzy_results + semantic_results, key=lambda r: -r["score"]):
        item_id = str(res["item"].get(id_field))
        if item_id and item_id not in seen_ids:
            combined.append(res)
            seen_ids.add(item_id)
        if len(combined) >= top_k:
            break
    return combined

# --- Interfaces especializadas ---

def search_attributes(query: str, mode: Literal["fuzzy", "semantic", "hybrid"] = "hybrid") -> List[Dict[str, Any]]:
    """
    Busca atributos físicos por nombre/desc usando el modo elegido.
    """
    config = get_config()
    top_k = config.attributes.technical.get("default_limit", 10)
    fuzzy_threshold = config.attributes.technical.get("fuzzy_threshold", 70)
    semantic_threshold = config.attributes.semantic.get("similarity_threshold", 0.65)
    # Armar lista
    rows = [row.__dict__ for row in attribute_repo.all()]
    if mode == "fuzzy":
        return fuzzy_search(query, rows, "physical_name", top_k=top_k, threshold=fuzzy_threshold)
    elif mode == "semantic":
        # id_to_item por attr_id (int)
        id_to_item = {str(r["attr_id"]): r for r in rows}
        return semantic_search(query, "attributes_desc", id_to_item, top_k=top_k, threshold=semantic_threshold)
    else:
        return hybrid_search(
            query, rows, "physical_name", "attributes_desc", "attr_id",
            top_k=top_k, fuzzy_threshold=fuzzy_threshold, semantic_threshold=semantic_threshold
        )

def search_cdes(query: str, mode: Literal["fuzzy", "semantic", "hybrid"] = "hybrid") -> List[Dict[str, Any]]:
    """
    Busca CDEs por nombre de negocio/desc usando el modo elegido.
    """
    config = get_config()
    top_k = config.cde.default_limit
    fuzzy_threshold = config.duplicates.name_similarity_threshold
    semantic_threshold = config.cde.get("similarity_threshold", 0.65)
    rows = [row.__dict__ for row in cde_repo.all()]
    if mode == "fuzzy":
        return fuzzy_search(query, rows, "biz_term", top_k=top_k, threshold=fuzzy_threshold)
    elif mode == "semantic":
        id_to_item = {str(r["cde_id"]): r for r in rows}
        return semantic_search(query, "cdes_desc", id_to_item, top_k=top_k, threshold=semantic_threshold)
    else:
        return hybrid_search(
            query, rows, "biz_term", "cdes_desc", "cde_id",
            top_k=top_k, fuzzy_threshold=fuzzy_threshold, semantic_threshold=semantic_threshold
        )

def search_catalogs(query: str, mode: Literal["fuzzy", "semantic", "hybrid"] = "hybrid") -> List[Dict[str, Any]]:
    """
    Busca catálogos institucionales por descripción usando el modo elegido.
    """
    config = get_config()
    top_k = config.catalogs.default_limit
    fuzzy_threshold = config.duplicates.name_similarity_threshold
    semantic_threshold = config.catalogs.similarity_threshold
    rows = [row.__dict__ for row in catalog_repo.all()]
    if mode == "fuzzy":
        return fuzzy_search(query, rows, "desc_raw", top_k=top_k, threshold=fuzzy_threshold)
    elif mode == "semantic":
        id_to_item = {str(r["id"]): r for r in rows}
        return semantic_search(query, "catalogs_desc", id_to_item, top_k=top_k, threshold=semantic_threshold)
    else:
        return hybrid_search(
            query, rows, "desc_raw", "catalogs_desc", "id",
            top_k=top_k, fuzzy_threshold=fuzzy_threshold, semantic_threshold=semantic_threshold
        )
