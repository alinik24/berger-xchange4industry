# Berger Xchange4Industry

## What this project is

A self-contained Berger Xchange4Industry prototype with backend, Streamlit frontend, PostgreSQL, trust-service, EDC, and mock connectivity services.

## Quick start

```powershell
git clone https://github.com/alinik24/berger-xchange4industry.git
cd berger-xchange4industry
.\bootstrap.ps1
docker compose -f infrastructure/docker-compose.yaml up --build
```

Linux/macOS: `./bootstrap.sh`.

## Configuration

The compose file supplies development-only container defaults and local service names. Do not use its sample passwords outside local development. No external repository is required to build or run this copy.

## Verification

- `docker compose -f infrastructure/docker-compose.yaml config` validates the topology.
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:8501`
- PostgreSQL: `localhost:5432`

See `docs/ARCHITECTURE.md` and `docs/DEVELOPMENT.md`.
