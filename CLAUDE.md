# CLAUDE.md — beat-books-api

## Project Overview
API gateway for the BeatTheBooks platform. This is the public-facing HTTP interface. It routes requests to beat-books-data (scraping, stats) and beat-books-model (predictions).

## Architecture
Thin API layer — routes delegate to backend services, NO business logic here.
```
User → beat-books-api → beat-books-data (data operations)
                      → beat-books-model (predictions)
```

## Directory Structure
```
src/
├── main.py          # FastAPI app, registers routers
├── routes/          # Route handlers (thin delegation layer)
│   ├── health.py    # GET /
│   ├── scrape.py    # Scraping endpoints → beat-books-data
│   ├── stats.py     # Data retrieval → beat-books-data
│   └── predictions.py # Predictions → beat-books-model
└── core/
    └── config.py    # Service URLs, app config
```

## Rules — ALWAYS Follow
- ALWAYS keep route handlers thin — delegate to backend services
- ALWAYS validate inputs with Pydantic (FastAPI query params / body models)
- ALWAYS return consistent response envelopes (data, pagination, error)
- ALWAYS document endpoints in OpenAPI (FastAPI auto-generates this)

## Rules — NEVER Do
- NEVER put SQL or database queries in route handlers
- NEVER put ML model logic in routes
- NEVER put scraping logic in routes
- NEVER import entities or repositories from beat-books-data directly in routes
- NEVER hardcode service URLs — use config.py

## Common Commands
```bash
uvicorn src.main:app --reload --port 8000
pytest
pytest --cov=src --cov-report=html
```

## Port Assignments
- beat-books-api: localhost:8000 (this service — public-facing)
- beat-books-data: localhost:8001 (internal)
- beat-books-model: localhost:8002 (internal, future)

## Related Repos
- beat-books-data: Data service (this gateway routes to it)
- beat-books-model: Prediction service (this gateway will route to it)
- beat-books-infra: CI/CD, docs, Docker
