# Regenerate PBIP and attempt to open in Power BI Desktop
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
$env:PYTHONPATH = (Get-Location).Path

Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*#' -or $_ -notmatch '=') { return }
    $k, $v = $_.Split('=', 2)
    Set-Item -Path "Env:$($k.Trim())" -Value $v.Trim()
}

python scripts/generate_powerbi_project.py
$pbip = Resolve-Path "dashboards/powerbi/PakistanEcommerce/PakistanEcommerce.pbip"

Write-Host "Power BI project: $pbip"

$pbiPaths = @(
    "${env:ProgramFiles}\Microsoft Power BI Desktop\bin\PBIDesktop.exe",
    "${env:LOCALAPPDATA}\Microsoft\WindowsApps\PBIDesktopStore.exe",
    "${env:ProgramFiles}\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_*__8wekyb3d8bbwe\PBIDesktop.exe"
)

$opened = $false
foreach ($p in $pbiPaths) {
    $resolved = Get-Item $p -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($resolved) {
        Start-Process $resolved.FullName -ArgumentList "`"$pbip`""
        $opened = $true
        break
    }
}

if (-not $opened) {
    Write-Host ""
    Write-Host "Power BI Desktop not found. Install from Microsoft Store:"
    Write-Host "  https://apps.microsoft.com/detail/9ntxr16hnw1t"
    Write-Host ""
    Write-Host "Then open: $pbip"
    explorer (Split-Path $pbip -Parent)
}
