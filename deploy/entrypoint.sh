#!/bin/bash
set -e

echo "======================================================================"
echo "  Iniciando SamuBusquedas v3.0 (.onion v3) — Arquitectura por saghet  "
echo "======================================================================"

# Iniciar servidor web Python en segundo plano
echo "[*] Arrancando servidor web Zero-JS en 127.0.0.1:8080..."
python3 /app/app/main.py --host 127.0.0.1 --port 8080 &
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
