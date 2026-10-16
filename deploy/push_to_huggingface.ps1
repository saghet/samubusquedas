param (
    [Parameter(Mandatory=$false)]
    [string]$HfUsername,

    [Parameter(Mandatory=$false)]
    [string]$SpaceName = "samubusquedas-onion"
)

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Publicador Automático a Hugging Face Spaces (2 vCPU / 16 GB RAM Gratis)  " -ForegroundColor Yellow
Write-Host "  SamuBusquedas v3.0 (.onion v3) — Arquitectura por saghet              " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

if (-not $HfUsername) {
    $HfUsername = Read-Host "Ingresa tu usuario de Hugging Face (ej. saghet)"
}

if (-not $HfUsername) {
    Write-Host "[!] El nombre de usuario no puede estar vacío." -ForegroundColor Red
    exit 1
}

$RemoteUrl = "https://huggingface.co/spaces/$HfUsername/$SpaceName"
Write-Host "[*] Configurando remoto Git hacia: $RemoteUrl" -ForegroundColor Green

git remote remove space 2>$null
git remote add space $RemoteUrl

Write-Host "[*] Enviando código y claves criptográficas del servicio .onion..." -ForegroundColor Green
Write-Host "    (Si Git solicita contraseña, ingresa tu Access Token de Hugging Face de https://huggingface.co/settings/tokens)" -ForegroundColor DarkYellow

git push -u space master:main --force

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host "  [EXITO] ¡SAMUBUSQUEDAS PUBLICADO EN LA NUBE GRATUITA (HUGGING FACE)! " -ForegroundColor Green
    Write-Host "  Dirección Oficial Permanente en la Red Tor (.onion v3):              " -ForegroundColor Cyan
    Write-Host "  http://x4wgcuog7p6i3gh5t2mcshhfe5cjlkiygl24vf4ac6xmqm5g62jkehyd.onion " -ForegroundColor Yellow
    Write-Host "  Panel de Monitoreo: $RemoteUrl                                      " -ForegroundColor White
    Write-Host "======================================================================" -ForegroundColor Green
} else {
    Write-Host "[!] Hubo un error al subir a Hugging Face. Verifica que el Space exista en https://huggingface.co/new-space con SDK Docker." -ForegroundColor Red
}
