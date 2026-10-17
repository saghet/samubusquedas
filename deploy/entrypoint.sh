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

# Sincronizar el puerto del Hidden Service de Tor con el puerto HTTP de la nube
echo "[*] Configurando redirección del Hidden Service Tor hacia 127.0.0.1:${PORT}..."
sed -i "s/127.0.0.1:8080/127.0.0.1:${PORT}/g" /etc/tor/torrc

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
