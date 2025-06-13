# Kraken

Kraken is a small data discovery engine and UI. It loads business dictionaries
and catalog definitions into a local SQLite database, generates embeddings with
`sentence_transformers` and builds FAISS indices so metadata can be searched
using fuzzy or semantic similarity.

## Installation

Kraken requires **Python 3.10** or newer. Once the appropriate Python version is
available, install the project dependencies:

```bash
pip install -r requirements.txt
```

## Required input files

The ingestor expects several Excel/CSV files inside the directory configured as
`files.catalogs_dir` (defaults to `data/catalogs/`). The file names determine the
table each file populates:

- `Mega_Diccionario.xlsx` – physical attributes dictionary.
- `Base_CDEs.xlsx` – business CDE definitions.
- `Base_Catalogos_S080.xlsx` – institutional catalogs.
- `DQ_Rules.xlsx` – quality rules for each CDE.

Columns are matched using the synonyms defined in
`kraken/services/ingestor.py` and can be provided either in Excel or CSV
format.

## Running Kraken

After placing the input files in the configured directory, run:

```bash
python -m kraken.main
```

The command checks that the database, embeddings and FAISS indices exist. If
they do not, it performs the ingestion and indexing steps automatically and then
starts the Streamlit UI. You can trigger ingestion manually with
`python -m kraken.main ingest`.

## Running Tests

Execute the test suite with **pytest** from the repository root:

```bash
pytest
```
