# Narrative Vectors for Financial Filings

Ingest PDFs from `data/{TICKER}/`, extract text, vectorize (TF-IDF by default), and store vectors in **Postgres + pgvector**. The pipeline is **modular** so you can swap the vectorizer without touching the rest.

---

## ✅ Features

- Walks `data/{TICKER}/` directories and reads all PDFs
- Extracts plain text from each PDF
- Vectorizes via a swappable interface (TF-IDF included)
- Stores text + embeddings in Postgres (`pgvector`)
- Includes a sample script to read back one vector

---

## 📁 Project Structure

```text
project_root/
  data/
    KO/
      2018_10K.pdf
      2019_10K.pdf
    MSFT/
      2020_10K.pdf
  config.py
  pdf_reader.py
  vectorizer.py
  db.py
  pipeline.py
  main.py
  read_one_vector.py
  docker-compose.yml
  README.md
```

**Roles**
- `pdf_reader.py` → iterate `data/{TICKER}/` and extract PDF text  
- `vectorizer.py` → `BaseVectorizer` interface + TF-IDF impl  
- `db.py` → Postgres + `pgvector` wrapper (init table, insert)  
- `pipeline.py` → orchestrates read → vectorize → store  
- `main.py` → runs the full pipeline  
- `read_one_vector.py` → prints a sample stored vector

---

## 🧰 Requirements

- **Python** 3.9+
- **Docker** + **Docker Compose**

Verify:
```bash
python --version
docker --version
```

Create & activate venv:
```bash
# macOS/Linux
python -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install Python deps:
```bash
pip install pypdf numpy scikit-learn psycopg2-binary pgvector
```

(Optional) freeze:
```bash
pip freeze > requirements.txt
```

---

## 🐘 Postgres + pgvector (Docker)

Create `docker-compose.yml` in project root:

```yaml
version: "3.8"

services:
  db:
    image: pgvector/pgvector:pg16
    container_name: pgvector-db
    environment:
      POSTGRES_DB: narrative_vectors
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d narrative_vectors"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

Start DB:
```bash
docker compose up -d
docker ps
```

(If issues) Logs:
```bash
docker compose logs db
```

Sanity check:
```bash
docker exec -it pgvector-db psql -U postgres -d narrative_vectors -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker exec -it pgvector-db psql -U postgres -d narrative_vectors -c "\dx"
```

---

## ⚙️ Configure `config.py`

```python
from pathlib import Path

DATA_DIR = Path("data")
DB_DSN   = "postgresql://postgres:postgres@localhost:5432/narrative_vectors"
EMBED_DIM = 512    # must match TF-IDF max_features and DB vector(dim)
```

> If you later run your Python app **inside Docker** alongside the DB, change host to `db`:
> `postgresql://postgres:postgres@db:5432/narrative_vectors`

---

## ▶️ Run the Pipeline

1) Put PDFs under `data/{TICKER}/` (e.g., `data/KO/2019_10K.pdf`).

2) Start DB:
```bash
docker compose up -d
```

3) Activate venv and run:
```bash
python main.py
```

Expected logs: number of documents, vectorizer dimension, embedding shape (e.g., `(N, 512)`), schema init, inserts.

---

## 🔎 Inspect Stored Data

Open `psql` inside the container:
```bash
docker exec -it pgvector-db psql -U postgres -d narrative_vectors
```

Sample query:
```sql
SELECT id, ticker, doc_id, LENGTH(content) AS content_len
FROM document_embeddings
LIMIT 5;
```

Exit with `\q`.

---

## 📖 Read Back One Vector

From project root (with venv active, DB running):
```bash
python read_one_vector.py
```

You’ll see:
- Row ID, ticker, doc ID
- Vector dimension
- First few values of the vector

---

## 🔁 Swapping the Vectorizer (Extensibility)

- `vectorizer.py` exposes a `BaseVectorizer` interface (`fit`, `transform`, `dim`).
- Add your own vectorizer (e.g., sentence transformers) as a new class.
- Update only `fit_vectorizer()` in `pipeline.py` to instantiate your new class.
- Ensure `EMBED_DIM` (and DB column type `vector(dim)`) matches the new dimension.

No changes required in `pdf_reader.py`, `db.py` (other than dimension), or `main.py`.

---

## 🧹 DB Lifecycle

- Stop (keep data):
```bash
docker compose down
```

- Start:
```bash
docker compose up -d
```

- Full reset (wipe data):
```bash
docker compose down -v
docker compose up -d
```

Then re-run:
```bash
python main.py
```

---

## ❗ Troubleshooting

- **`vector` extension missing**  
  Ensure you used the `pgvector/pgvector:pg16` image and ran  
  `CREATE EXTENSION IF NOT EXISTS vector;`

- **Connection refused**  
  Confirm container is running (`docker ps`), port `5432` not blocked, DSN host is `localhost`.

- **Empty results**  
  Check that `data/{TICKER}/` contains PDFs with extractable text and re-run `main.py`.

---
