@echo off
chcp 65001 >nul
echo ==============================================================================
echo   SamuBusquedas (.onion v3) — Diagnóstico de Estado y Salud del Servicio
echo   Arquitecto: saghet ^| Version: 1.99.11
echo ==============================================================================
echo.

echo [1/4] Verificando Proceso Tor (tor.exe)...
tasklist /FI "IMAGENAME eq tor.exe" 2>NUL | find /I /N "tor.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo   [OK] tor.exe esta activo y ejecutandose.
) else (
    echo   [ALERTA] tor.exe no esta en ejecucion.
)

echo.
echo [2/4] Verificando Puertos Locales (8080 HTTP, 8443 HTTPS, 19050 SOCKS)...
netstat -ano | findstr ":8080" | findstr "LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Puerto 8080 (HTTP / LAN Wi-Fi): ACTIVO
) else (
    echo   [FALLO] Puerto 8080 INACTIVO
)

netstat -ano | findstr ":8443" | findstr "LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Puerto 8443 (HTTPS / Tor Movil): ACTIVO
) else (
    echo   [FALLO] Puerto 8443 INACTIVO
)

netstat -ano | findstr ":19050" | findstr "LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Puerto 19050 (Tor SOCKS5h): ACTIVO
) else (
    echo   [FALLO] Puerto 19050 INACTIVO
)

echo.
echo [3/4] Enlaces de Acceso:
echo   - Tor Browser (Deep Web): http://x4wgcuog7p6i3gh5t2mcshhfe5cjlkiygl24vf4ac6xmqm5g62jkehyd.onion/
echo   - Red Wi-Fi Local (Cualquier navegador celular): http://192.168.1.6:8080/
echo   - Espejo Global Clearnet: https://samubusquedas.onrender.com/
echo.
echo ==============================================================================
pause
