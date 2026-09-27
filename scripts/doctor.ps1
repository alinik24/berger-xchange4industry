$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { Write-Error 'MISSING: Docker Desktop' }
docker compose -f (Join-Path $root 'infrastructure/docker-compose.yaml') config | Out-Null
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host 'docker=CONFIGURED'
Write-Host 'composed_stack=PASS'
Write-Host 'doctor=PASS'
