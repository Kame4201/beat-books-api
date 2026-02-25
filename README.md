# beat-books-api

API gateway for the BeatTheBooks NFL prediction platform.

## What This Does

Routes HTTP requests to the appropriate backend service:
- **Scraping & Stats** → `beat-books-data` (port 8001)
- **Predictions** → `beat-books-model` (port 8002, future)

This is a thin routing layer with no business logic.

## Quick Start

### Local Development

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload --port 8000
# Swagger docs at http://localhost:8000/docs
```

### Docker

```bash
# Build the image
docker build -t beat-books-api .

# Run the container
docker run -p 8000:8000 beat-books-api

# Health check
curl http://localhost:8000/
```

## Endpoints

| Method | Endpoint | Routes To |
|--------|----------|-----------|
| GET | `/` | Health check |
| GET | `/scrape/{team}/{year}` | beat-books-data |
| GET | `/scrape/{year}` | beat-books-data |
| POST | `/scrape/excel` | beat-books-data |
| GET | `/teams/{team}/stats` | beat-books-data |
| GET | `/players` | beat-books-data |
| GET | `/games` | beat-books-data |
| GET | `/standings` | beat-books-data |
| GET | `/predictions/predict` | beat-books-model |

## Troubleshooting

### Windows: `Dev` vs `dev` ref collision

On case-insensitive filesystems (Windows, some macOS configs), `git fetch` may fail with:

```
error: cannot lock ref 'refs/remotes/origin/dev': 'refs/remotes/origin/Dev' exists
```

This happens because the remote has both `Dev` and `dev` branches, which collide locally.

**Fix (safe, local-clone only):**

```bash
git refs migrate --ref-format=reftable
```

This converts your local ref storage to a case-sensitive format. It does not affect the remote.

## Related Repos

- [beat-books-data](https://github.com/Kame4201/beat-books-data) — Data ingestion & storage
- [beat-books-model](https://github.com/Kame4201/beat-books-model) — ML predictions
- [beat-books-infra](https://github.com/Kame4201/beat-books-infra) — CI/CD, docs, Docker
