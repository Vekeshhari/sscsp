# SSCSP

Software Supply Chain Security Platform prototype.

## Stack

- FastAPI backend
- PostgreSQL
- React + Vite frontend
- Docker Compose for local orchestration

## Run locally

```bash
cp .env.example .env
docker compose up --build
```

Then open:

- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/docs
- Postgres: localhost:5432

Seed users:

```bash
docker compose exec backend python -m app.seed
```

## Default accounts

- dev / Dev@12345
- analyst / Ana@12345
- admin / Adm@12345
- auditor / Aud@12345
