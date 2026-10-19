#!/bin/bash
# ==============================================================================
# SamuBusquedas v1.99.13 (.onion v3) — Supervisor Cloud Auto-Curativo (24/7)
# Arquitecto: saghet
# Publicación Oficial en la Deep Web sin Depender de la PC Local
# ==============================================================================
set -e

PORT=${PORT:-8080}

echo "======================================================================"
echo "  Iniciando SamuBusquedas v1.99.13 (.onion v3) en la Nube (24/7)      "
echo "  Arquitecto: saghet                                                  "
echo "  Puerto Asignado por Render: ${PORT}                                 "
echo "======================================================================"

# 1. Configurar dinámicamente el puerto del Hidden Service en /etc/tor/torrc
if [ -f "/etc/tor/torrc" ]; then
    sed -i "s/__PORT__/${PORT}/g" /etc/tor/torrc
fi

# 2. Asegurar permisos estrictos requeridos por Tor (0700 en dir, 0600 en llaves)
mkdir -p /var/lib/tor/samubusquedas_hs /var/lib/tor/data
chmod 700 /var/lib/tor/samubusquedas_hs /var/lib/tor/data
if [ -d "/var/lib/tor/samubusquedas_hs" ]; then
    chmod 600 /var/lib/tor/samubusquedas_hs/* 2>/dev/null || true
fi
chown -R debian-tor:debian-tor /var/lib/tor

# 3. Bucle auto-reiniciable para el demonio Tor oficial (Publicador .onion + Proxy SOCKS5h)
(
    while true; do
        echo "[*] [Tor Cloud] Iniciando/Verificando demonio Tor oficial..."
        su -s /bin/bash debian-tor -c "tor -f /etc/tor/torrc" || true
        echo "[!] [Tor Cloud] Demonio Tor se detuvo; reiniciando en 2 segundos..."
        sleep 2
    done
) &

sleep 2

# 4. Bucle auto-reiniciable para el servidor web Python (SSR Zero-JS + Onion Guardian)
while true; do
    echo "[*] [Web Cloud] Ejecutando servidor web Zero-JS en 0.0.0.0:${PORT} y HTTPS 8443..."
    PORT=${PORT} HOST=0.0.0.0 python3 /app/app/main.py || true
    echo "[!] [Web Cloud] Servidor web se detuvo; reiniciando en 1 segundo..."
    sleep 1
done
