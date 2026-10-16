"""
Lanzador Unificado de SamuBusquedas (.onion v3) en Vivo
-------------------------------------------------------
Inicia simultáneamente:
1. El servidor web SSR Zero-JS de SamuBusquedas en 127.0.0.1:8080.
2. El demonio oficial de Tor (v0.4.9.13) con HiddenServiceVersion 3 y defensa PoW Equi-X.
"""

import os
import subprocess
import sys
import threading
import time

from main import run_server

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOR_EXE = r"C:\Users\saghe\Documents\Antivitus-SamuLibre\data\bin\tor\tor.exe"
TORRC_CONF = os.path.join(BASE_DIR, "config", "torrc.windows.conf")
HOSTNAME_FILE = os.path.join(BASE_DIR, ".tor_runtime", "samubusquedas_hs", "hostname")


def main() -> None:
    os.makedirs(os.path.join(BASE_DIR, ".tor_runtime", "data"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, ".tor_runtime", "samubusquedas_hs"), exist_ok=True)

    # 1. Iniciar servidor web en hilo daemon (127.0.0.1:8080)
    web_thread = threading.Thread(target=run_server, kwargs={"host": "127.0.0.1", "port": 8080}, daemon=True)
    web_thread.start()

    # 2. Iniciar demonio Tor oficial y mantenerlo vivo
    print("[*] Iniciando demonio Tor oficial para publicar el servicio .onion v3...")
    tor_proc = subprocess.Popen([TOR_EXE, "-f", TORRC_CONF], cwd=BASE_DIR)

    # Esperar a que exista el archivo hostname
    for _ in range(20):
        if os.path.exists(HOSTNAME_FILE):
            with open(HOSTNAME_FILE, "r", encoding="utf-8") as f:
                onion_domain = f.read().strip()
            print("======================================================================")
            print(f"  [ONLINE] DOMINIO .ONION V3 PUBLICADO: http://{onion_domain}")
            print("======================================================================")
            break
        time.sleep(1)

    try:
        tor_proc.wait()
    except KeyboardInterrupt:
        tor_proc.terminate()
        sys.exit(0)


if __name__ == "__main__":
    main()
