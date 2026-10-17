#!/bin/bash
# ==============================================================================
# SamuBusquedas v1.99.6 (.onion v3) — Supervisor Cloud Auto-Curativo (24/7)
# Arquitecto: saghet
# ==============================================================================
set -e

PORT=${PORT:-8080}

echo "======================================================================"
echo "  Iniciando SamuBusquedas (.onion v3) — Arquitectura por saghet       "
echo "======================================================================"

# Bucle auto-reiniciable para el demonio Tor oficial en segundo plano (SOCKS5h Proxy)
(
    while true; do
        echo "[*] [Guardian] Iniciando/Verificando demonio Tor oficial..."
        su -s /bin/bash debian-tor -c "tor -f /etc/tor/torrc" || true
        echo "[!] [Guardian] Demonio Tor se detuvo; reiniciando en 2 segundos..."
        sleep 2
    done
) &

sleep 2

# Bucle auto-reiniciable para el servidor web Python (incluye OnionAlwaysOnGuardian)
while true; do
    echo "[*] [Guardian] Ejecutando servidor web Zero-JS en 0.0.0.0:${PORT}..."
    PORT=${PORT} HOST=0.0.0.0 python3 /app/app/main.py || true
    echo "[!] [Guardian] Servidor web se detuvo; reiniciando en 1 segundo..."
    sleep 1
done
