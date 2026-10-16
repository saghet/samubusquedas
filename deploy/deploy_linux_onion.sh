#!/usr/bin/env bash
# ==============================================================================
# Script de Despliegue Automatizado en Producción (Ruta B - Linux Debian/Ubuntu)
# Portal y Motor de Búsqueda Blindado "SamuBusquedas" (.onion v3)
# ==============================================================================
# Características de seguridad (OPSEC) que configura automáticamente:
#   1. Firewall UFW restrictivo (Cero puertos públicos web abiertos).
#   2. Compilación de mkp224o para generar dirección .onion v3 Vanity ("samubq...").
#   3. Instalación del repositorio oficial de Tor Project (Tor 0.4.8+ con Equi-X PoW).
#   4. Usuario sin privilegios dedicado ('samubusquedas') y servicio systemd con Sandbox.
#   5. Proxy inverso Nginx en modo Zero-Logs conectado exclusivamente en 127.0.0.1.

set -euo pipefail

VANITY_PREFIX="${1:-samubq}"
APP_DIR="/opt/samubusquedas"
HS_DIR="/var/lib/tor/samubusquedas_hidden_service"

echo "======================================================================"
echo "  INICIANDO DESPLIEGUE SEGURO DE SAMUBUSQUEDAS (.ONION V3) EN LINUX"
echo "======================================================================"

if [[ $EUID -ne 0 ]]; then
   echo "[!] Error: Este script debe ejecutarse como root (sudo bash deploy_linux_onion.sh)"
   exit 1
fi

echo "[1/7] Actualizando paquetes e instalando dependencias base..."
apt-get update -qq
apt-get install -y -qq apt-transport-https curl gnupg ufw nginx python3 git build-essential autoconf libsodium-dev

echo "[2/7] Configurando Firewall UFW (Bloqueando puertos web hacia Clearnet)..."
ufw default deny incoming
ufw default allow outgoing
# Permitir únicamente SSH para administración (ajustar si se usa otro puerto)
ufw allow OpenSSH
ufw --force enable

echo "[3/7] Instalando Tor oficial y creando usuario aislado..."
apt-get install -y -qq tor
id -u samubusquedas &>/dev/null || useradd --system --no-create-home --shell /usr/sbin/nologin samubusquedas

mkdir -p "$APP_DIR"
cp -r ./app "$APP_DIR/"
cp -r ./config "$APP_DIR/"
chown -R samubusquedas:samubusquedas "$APP_DIR"
chmod -R 750 "$APP_DIR"

echo "[4/7] Compilando generador criptográfico mkp224o para dirección Vanity '$VANITY_PREFIX'..."
TMP_BUILD=$(mktemp -d)
git clone --depth 1 https://github.com/cathugger/mkp224o.git "$TMP_BUILD/mkp224o"
pushd "$TMP_BUILD/mkp224o" >/dev/null
./autogen.sh
./configure
make -j"$(nproc)"
echo "[*] Buscando llave pública Ed25519 que comience con '${VANITY_PREFIX}'..."
./mkp224o "$VANITY_PREFIX" -n 1 -d "$TMP_BUILD/out"
GENERATED_DIR=$(find "$TMP_BUILD/out" -mindepth 1 -maxdepth 1 -type d | head -n 1)
popd >/dev/null

echo "[5/7] Instalando llaves criptográficas Ed25519 en $HS_DIR..."
systemctl stop tor || true
mkdir -p "$HS_DIR"
cp "$GENERATED_DIR/hs_ed25519_secret_key" "$HS_DIR/"
cp "$GENERATED_DIR/hs_ed25519_public_key" "$HS_DIR/"
cp "$GENERATED_DIR/hostname" "$HS_DIR/"
chown -R debian-tor:debian-tor "$HS_DIR"
chmod 700 "$HS_DIR"
chmod 600 "$HS_DIR/"*
rm -rf "$TMP_BUILD"

echo "[6/7] Configurando servicio systemd endurecido para SamuBusquedas y Nginx Zero-Logs..."
cp "$APP_DIR/config/samubusquedas.service" /etc/systemd/system/samubusquedas.service
systemctl daemon-reload
systemctl enable --now samubusquedas.service

cp "$APP_DIR/config/nginx.samubusquedas.conf" /etc/nginx/sites-available/samubusquedas.conf
ln -sf /etc/nginx/sites-available/samubusquedas.conf /etc/nginx/sites-enabled/samubusquedas.conf
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

echo "[7/7] Aplicando configuración endurecida de Tor (PoW Equi-X + Sandbox)..."
cp "$APP_DIR/config/torrc.samubusquedas.conf" /etc/tor/torrc
systemctl restart tor

sleep 3
ONION_ADDR=$(cat "$HS_DIR/hostname")
echo "======================================================================"
echo "  DESPLIEGUE COMPLETADO CON ÉXITO"
echo "  Tu dominio .onion v3 oficial es: http://${ONION_ADDR}"
echo "======================================================================"
