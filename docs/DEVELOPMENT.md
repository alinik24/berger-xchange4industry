# Development

- Prerequisite: Docker Desktop with Compose.
- Validate: `docker compose -f infrastructure/docker-compose.yaml config`.
- Start: `docker compose -f infrastructure/docker-compose.yaml up --build`.
- Stop: `docker compose -f infrastructure/docker-compose.yaml down`.
- No upstream Git remote or runtime clone is required.
