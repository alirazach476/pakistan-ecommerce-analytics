# Launch interactive BI dashboard (Streamlit) connected to PostgreSQL
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
$env:PYTHONPATH = (Get-Location).Path

Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*#' -or $_ -notmatch '=') { return }
    $k, $v = $_.Split('=', 2)
    Set-Item -Path "Env:$($k.Trim())" -Value $v.Trim()
}

Write-Host "Starting BI dashboard at http://localhost:8501"
streamlit run dashboards/streamlit/app.py --server.headless true
