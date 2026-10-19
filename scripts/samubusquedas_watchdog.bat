@echo off
REM ==============================================================================
REM SamuBusquedas (.onion v3) — Watchdog Supervisor de Persistencia 24/7 (v1.99.11)
REM Arquitecto: saghet
REM Supervisa continuamente:
REM 1. El servidor web SSR Zero-JS en puertos 8080 (HTTP) y 8443 (HTTPS)
REM 2. El demonio Tor con 8 Introduction Points y descriptor actualizado
REM ==============================================================================

cd /d "c:\Users\saghe\Documents\DeepWeb"

:WATCHDOG_LOOP
REM 1. Verificar si el puerto 8080 está escuchando
netstat -ano | findstr ":8080" | findstr "LISTENING" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [%date% %time%] Servidor 8080 no detectado. Iniciando run_onion_live.py... >> .tor_runtime\watchdog.log
    start "" /b python app\run_onion_live.py >> .tor_runtime\onion_live.log 2>&1
    timeout /t 5 /nobreak >nul
)

REM 2. Verificar si tor.exe está en ejecución
tasklist /FI "IMAGENAME eq tor.exe" 2>NUL | find /I /N "tor.exe" >NUL
if %ERRORLEVEL% NEQ 0 (
    echo [%date% %time%] Proceso tor.exe no detectado. Invocando recuperacion... >> .tor_runtime\watchdog.log
    start "" /b python app\run_onion_live.py >> .tor_runtime\onion_live.log 2>&1
    timeout /t 5 /nobreak >nul
)

REM Esperar 15 segundos antes de la siguiente verificación
timeout /t 15 /nobreak >nul
goto WATCHDOG_LOOP
