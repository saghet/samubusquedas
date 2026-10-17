param (
    [Parameter(Mandatory=$false)]
    [string]$GithubUsername,

    [Parameter(Mandatory=$false)]
    [string]$RepoName = "samubusquedas"
)

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Conector Automático GitHub -> Render.com (Producción 24/7 Gratuita)  " -ForegroundColor Yellow
Write-Host "  SamuBusquedas v3.0 (.onion v3) — Arquitectura por saghet              " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

if (-not $GithubUsername) {
    $GithubUsername = Read-Host "Ingresa tu nombre de usuario de GitHub"
}

if (-not $GithubUsername) {
    Write-Host "[!] El usuario no puede estar vacío." -ForegroundColor Red
    exit 1
}

$RemoteUrl = "https://github.com/$GithubUsername/$RepoName.git"
Write-Host "[*] Vinculando repositorio Git hacia: $RemoteUrl" -ForegroundColor Green

git remote remove origin 2>$null
git remote add origin $RemoteUrl

Write-Host "[*] Subiendo código, Dockerfile y claves criptográficas a GitHub..." -ForegroundColor Green
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host "  [EXITO] ¡REPOSITORIO SUBIDO A GITHUB!                               " -ForegroundColor Green
    Write-Host "  Ahora conéctalo en Render en 2 pasos:                               " -ForegroundColor Cyan
    Write-Host "  1. Entra en: https://dashboard.render.com                            " -ForegroundColor White
    Write-Host "  2. Haz clic en 'New +' -> 'Web Service' y selecciona '$RepoName'    " -ForegroundColor White
    Write-Host "  3. Elige el plan 'Free' ($0/mes) y pulsa 'Create Web Service'       " -ForegroundColor White
    Write-Host "======================================================================" -ForegroundColor Green
} else {
    Write-Host "[!] Si falló, asegúrate de haber creado el repositorio '$RepoName' en https://github.com/new primero." -ForegroundColor Yellow
}
