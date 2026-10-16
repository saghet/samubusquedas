# ==============================================================================
# Script de Publicación Rápida en Windows (Ruta A) - SamuBusquedas (.onion v3)
# ==============================================================================
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectRoot

Write-Host "======================================================================" -ForegroundColor Magenta
Write-Host "  PUBLICANDO SAMUBUSQUEDAS EN LA RED TOR (.ONION v3 + PoW Equi-X)    " -ForegroundColor Magenta
Write-Host "======================================================================" -ForegroundColor Magenta

python "$ProjectRoot\app\run_onion_live.py"
