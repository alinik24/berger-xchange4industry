#!/usr/bin/env bash
set -euo pipefail
command -v docker >/dev/null || { echo "MISSING: Docker Desktop"; exit 1; }
if [[ "${1:-}" != "--skip-docker" ]]; then docker compose -f infrastructure/docker-compose.yaml config >/dev/null; fi
echo "Bootstrap validated. Start with: docker compose -f infrastructure/docker-compose.yaml up --build"
