param([switch]$SkipDocker)
$ErrorActionPreference = "Stop"
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { Write-Error "MISSING: Docker Desktop (required for the composed stack)" }
if (-not $SkipDocker) { docker compose -f infrastructure/docker-compose.yaml config | Out-Null; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }
Write-Host "Bootstrap validated. Start with: docker compose -f infrastructure/docker-compose.yaml up --build"
