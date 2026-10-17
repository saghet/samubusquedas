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

# Sincronizar el puerto del Hidden Service de Tor con el puerto HTTP de la nube
echo "[*] Configurando redirección del Hidden Service Tor hacia 127.0.0.1:${PORT}..."
sed -i "s/127.0.0.1:8080/127.0.0.1:${PORT}/g" /etc/tor/torrc

# Bucle auto-reiniciable para el demonio Tor oficial en segundo plano
(
    while true; do
        echo "[*] [Guardian] Iniciando/Verificando demonio Tor oficial..."
        su -s /bin/bash debian-tor -c "tor -f /etc/tor/torrc" || true
        echo "[!] [Guardian] Demonio Tor se detuvo; reiniciando en 2 segundos..."
        sleep 2
    done
) &

sleep 2

if [ -f /var/lib/tor/samubusquedas_hs/hostname ]; then
    ONION_URL=$(cat /var/lib/tor/samubusquedas_hs/hostname)
    echo "======================================================================"
    echo "  [ONLINE] SERVICIO .ONION V3 PUBLICADO EXITOSAMENTE EN LA RED TOR:   "
    echo "  http://${ONION_URL}"
    echo "======================================================================"
fi

# Bucle auto-reiniciable para el servidor web Python (incluye OnionAlwaysOnGuardian)
while true; do
    echo "[*] [Guardian] Ejecutando servidor web Zero-JS en 0.0.0.0:${PORT}..."
    PORT=${PORT} HOST=0.0.0.0 python3 /app/app/main.py || true
    echo "[!] [Guardian] Servidor web se detuvo; reiniciando en 1 segundo..."
    sleep 1
done
