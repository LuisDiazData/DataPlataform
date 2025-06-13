"""
Kraken Main Entrypoint
Lanza la UI de Kraken (Streamlit) verificando base, embeddings e índices.
"""

import sys
import subprocess
from pathlib import Path
from kraken.core.config import get_config

def check_db_exists() -> bool:
    db_path = Path(get_config().files.data_dir) / "kraken_data.sqlite"
    return db_path.exists()

def check_embeddings_exist() -> bool:
    emb_cache = Path(get_config().files.data_dir) / "emb_cache.pkl"
    return emb_cache.exists()

def check_faiss_indices_exist() -> bool:
    faiss_dir = Path(get_config().faiss.dir)
    # Ejemplo: atributos, cdes, catálogos
    indices = [
        faiss_dir / "attributes_desc.index",
        faiss_dir / "cdes_desc.index",
        faiss_dir / "catalogs_desc.index"
    ]
    return all(f.exists() for f in indices)

def prepare_kraken_backend():
    """
    Asegura que la base, embeddings y FAISS estén listos.
    """
    from kraken.core.database import init_db
    from kraken.services.ingest.ingestor import ingest_all_from_config
    from kraken.infra.embedding_manager import get_embedding_manager
    from kraken.infra.faiss_manager import get_faiss_manager
    from kraken.repositories.attribute_repo import attribute_repo
    from kraken.repositories.cde_repo import cde_repo
    from kraken.repositories.catalog_repo import catalog_repo

    # 1. Verifica y crea base de datos si falta
    if not check_db_exists():
        print("[Kraken] Creando base de datos...")
        init_db(create_all=True)
        ingest_all_from_config()
        print("[Kraken] Base creada e ingestada.")

    # 2. Verifica y crea embeddings si falta
    if not check_embeddings_exist():
        print("[Kraken] Creando embeddings...")
        embedder = get_embedding_manager()
        # Embeddings de atributos
        attrs = attribute_repo.all()
        texts = [a.desc_raw or a.physical_name for a in attrs]
        embedder.encode(texts)
        # Embeddings de CDEs
        from kraken.repositories.cde_repo import cde_repo
        cdes = cde_repo.all()
        cde_texts = [c.desc_raw or c.biz_term for c in cdes]
        embedder.encode(cde_texts)
        # Embeddings de catálogos
        from kraken.repositories.catalog_repo import catalog_repo
        cats = catalog_repo.all()
        cat_texts = [c.desc_raw or c.table for c in cats]
        embedder.encode(cat_texts)
        print("[Kraken] Embeddings generados.")

    # 3. Verifica y crea índices FAISS si faltan
    if not check_faiss_indices_exist():
        print("[Kraken] Creando índices FAISS...")
        embedder = get_embedding_manager()
        # Índice de atributos
        attrs = attribute_repo.all()
        texts = [a.desc_raw or a.physical_name for a in attrs]
        ids = [str(a.attr_id) for a in attrs]
        get_faiss_manager("attributes_desc").build_index(texts, ids, force=True)
        # Índice de CDEs
        cdes = cde_repo.all()
        cde_texts = [c.desc_raw or c.biz_term for c in cdes]
        cde_ids = [str(c.cde_id) for c in cdes]
        get_faiss_manager("cdes_desc").build_index(cde_texts, cde_ids, force=True)
        # Índice de catálogos
        cats = catalog_repo.all()
        cat_texts = [c.desc_raw or c.table for c in cats]
        cat_ids = [str(c.id) for c in cats]
        get_faiss_manager("catalogs_desc").build_index(cat_texts, cat_ids, force=True)
        print("[Kraken] Índices FAISS listos.")

def run_streamlit_app():
    """
    Lanza la interfaz gráfica de Kraken con Streamlit.
    """
    app_path = Path(__file__).parent / "kraken" / "ui" / "streamlit_app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])

def main():
    """
    Entry point principal para Kraken.
    """
    if len(sys.argv) == 1 or sys.argv[1] in ["ui", "run", ""]:
        print("[Kraken] Verificando entorno inicial...")
        prepare_kraken_backend()
        run_streamlit_app()
    elif sys.argv[1] == "ingest":
        from kraken.services.ingest.ingestor import ingest_all_from_config
        ingest_all_from_config()
        print("Ingesta finalizada.")
    else:
        print(f"Comando no reconocido: {sys.argv[1]}")
        print("Usa: python main.py [ui|ingest]")

if __name__ == "__main__":
    main()
