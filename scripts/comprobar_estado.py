"""
SamuBusquedas (.onion v3) — Diagnóstico Rápido de Estado y Salud del Servicio (v1.99.11)
Arquitecto: saghet
"""

import os
import socket
import subprocess
import sys


def is_port_open(host: str, port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    try:
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False


def main() -> None:
    print("=" * 72)
    print("  SamuBusquedas (.onion v3) — Diagnostico de Estado y Salud del Servicio")
    print("  Arquitecto: saghet | Version: 1.99.11")
    print("=" * 72)
    print()

    # 1. Proceso Tor
    print("[1/3] Verificando Proceso Tor (tor.exe)...")
    try:
        out = subprocess.check_output('tasklist /FI "IMAGENAME eq tor.exe"', shell=True, text=True)
        if "tor.exe" in out:
            print("  [OK] tor.exe esta activo y en ejecucion.")
        else:
            print("  [ALERTA] tor.exe no esta en ejecucion.")
    except Exception as e:
        print(f"  [ERROR] No se pudo consultar procesos: {e}")

    print()
    # 2. Puertos
    print("[2/3] Verificando Puertos Locales...")
    p8080 = is_port_open("127.0.0.1", 8080)
    p8443 = is_port_open("127.0.0.1", 8443)
    p19050 = is_port_open("127.0.0.1", 19050)

    print(f"  [{'OK' if p8080 else 'FALLO'}] Puerto 8080 (HTTP / Wi-Fi LAN): {'ACTIVO' if p8080 else 'INACTIVO'}")
    print(f"  [{'OK' if p8443 else 'FALLO'}] Puerto 8443 (HTTPS / Tor Movil): {'ACTIVO' if p8443 else 'INACTIVO'}")
    print(f"  [{'OK' if p19050 else 'FALLO'}] Puerto 19050 (Tor SOCKS5h): {'ACTIVO' if p19050 else 'INACTIVO'}")

    print()
    # 3. Enlaces
    print("[3/3] Enlaces de Acceso:")
    print("  * Tor Browser (Deep Web): http://x4wgcuog7p6i3gh5t2mcshhfe5cjlkiygl24vf4ac6xmqm5g62jkehyd.onion/")
    print("  * Red Wi-Fi Local (Celular): http://192.168.1.6:8080/")
    print("  * Espejo Global Clearnet: https://samubusquedas.onrender.com/")
    print("=" * 72)


if __name__ == "__main__":
    main()
