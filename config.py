from pathlib import Path

# Folder containing data/{TICKER}/
DATA_DIR = Path("data")

# Postgres connection string (matches docker-compose.yml)
DB_DSN = "postgresql://postgres:postgres@localhost:5432/narrative_vectors"

# Only used if TF–IDF fallback is triggered
TFIDF_FALLBACK_DIM = 768
