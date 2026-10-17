#!/bin/bash
set -e

PORT=${PORT:-8080}

echo "======================================================================"
echo "  Iniciando SamuBusquedas v3.0 (.onion v3) — Arquitectura por saghet  "
echo "======================================================================"

# Iniciar servidor web Python en segundo plano
echo "[*] Arrancando servidor web Zero-JS en 0.0.0.0:${PORT}..."
PORT=${PORT} HOST=0.0.0.0 python3 /app/app/main.py &
WEB_PID=$!

# Iniciar demonio oficial Tor en segundo plano bajo usuario debian-tor
echo "[*] Arrancando demonio Tor oficial..."
su -s /bin/bash debian-tor -c "tor -f /etc/tor/torrc" &
TOR_PID=$!

sleep 3

if [ -f /var/lib/tor/samubusquedas_hs/hostname ]; then
    ONION_URL=$(cat /var/lib/tor/samubusquedas_hs/hostname)
    echo "======================================================================"
    echo "  [ONLINE] SERVICIO .ONION V3 PUBLICADO EXITOSAMENTE EN LA RED TOR:   "
    echo "  http://${ONION_URL}"
    echo "======================================================================"
fi

# Mantener vivo el contenedor supervisando ambos procesos
wait -n $WEB_PID $TOR_PID
