# Windows PowerShell helper for Pakistan E-commerce Analytics Platform
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
$env:PYTHONPATH = (Get-Location).Path

if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "Created .env from .env.example — edit passwords if needed."
}

function Import-DotEnv {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^\s*#' -or $_ -notmatch '=') { return }
        $k, $v = $_.Split('=', 2)
        Set-Item -Path "Env:$($k.Trim())" -Value $v.Trim()
    }
}

Write-Host "==> Starting PostgreSQL"
$dockerOk = $false
try {
    docker compose up -d postgres
    $dockerOk = $true
    Write-Host "==> Waiting for Postgres health"
    Start-Sleep -Seconds 8
} catch {
    Write-Host "Docker unavailable — starting embedded PostgreSQL fallback"
    pip install embedded-postgres -q
    python scripts/start_embedded_postgres.py
}
Import-DotEnv

Write-Host "==> Generating synthetic data"
python -m src.data_generation.generate

Write-Host "==> Validating raw data"
python -m src.validation.validate_raw

Write-Host "==> Loading into PostgreSQL"
python -m src.ingestion.pipeline

Write-Host "==> Running dbt"
Push-Location dbt
dbt debug --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
Pop-Location

Write-Host "==> Excel export + insights"
python -m src.transformation.export_excel
python -m src.transformation.generate_insights

Write-Host "==> pytest"
python -m pytest tests/ -v --tb=short

Write-Host "Pipeline finished."
