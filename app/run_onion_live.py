"""
Lanzador Unificado y Guardián 24/7 de SamuBusquedas (.onion v3) en Vivo (v1.99.6)
---------------------------------------------------------------------------------
Arquitecto: saghet
Inicia y supervisa permanentemente:
1. El servidor web SSR Zero-JS de SamuBusquedas en 127.0.0.1:8080.
2. El demonio oficial de Tor con 6 Puntos de Introducción y KeepalivePeriod 45s.
3. El hilo `ONION_GUARDIAN` que hace auto-ping SOCKS5h cada 45s al dominio `.onion`
   para impedir que los circuitos de Tor entren en estado `idle`.
"""

import os
import sys
import threading
import time

from main import run_server
from onion_guardian import ONION_GUARDIAN, is_local_port_open

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOSTNAME_FILE = os.path.join(BASE_DIR, ".tor_runtime", "samubusquedas_hs", "hostname")


def main() -> None:
    os.makedirs(os.path.join(BASE_DIR, ".tor_runtime", "data"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, ".tor_runtime", "samubusquedas_hs"), exist_ok=True)

    # 1. Iniciar servidor web dual (HTTP 0.0.0.0:8080 para LAN Wi-Fi y HTTPS 127.0.0.1:8443 para Tor Mobile)
    if not is_local_port_open("127.0.0.1", 8080):
        web_thread = threading.Thread(
            target=run_server,
            kwargs={"host": "0.0.0.0", "port": 8080, "https_port": 8443},
            daemon=True,
        )
        web_thread.start()

    # 2. Garantizar que el demonio Tor esté corriendo y activar el Guardián Anti-Idle
    ONION_GUARDIAN.ensure_tor_daemon_running(force_restart=False)
    ONION_GUARDIAN.start_guardian_daemon(heartbeat_interval_seconds=45)

    for _ in range(20):
        if os.path.exists(HOSTNAME_FILE):
            with open(HOSTNAME_FILE, "r", encoding="utf-8") as f:
                onion_domain = f.read().strip()
            print("======================================================================")
            print(f"  [ONLINE 24/7] DOMINIO .ONION V3 PUBLICADO: http://{onion_domain}")
            print("  [GUARDIÁN]    6 Puntos de Introducción + Latido SOCKS5h cada 45s    ")
            print("======================================================================")
            break
        time.sleep(0.5)

    try:
        while True:
            ONION_GUARDIAN.ensure_tor_daemon_running(force_restart=False)
            time.sleep(15)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
