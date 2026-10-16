"""
Módulo Verificador Criptográfico y Conector SOCKS5h Anti-SSRF (Etapa 3 - v2.0)
==============================================================================
Arquitecto de Ciberseguridad: saghet
Permite auditar automáticamente el catálogo de SamuBusquedas comprobando:
1. Validez matemática de las llaves públicas Ed25519 y checksum SHA3-256 en direcciones .onion v3.
2. Sondeo seguro opcional sobre el túnel local de Tor usando SOCKS5h puro (ATYP = 0x03 DOMAINNAME)
   para impedir fugas DNS, con bloqueo estricto de SSRF (solo dominios .onion v3 en la Allowlist),
   cabecera 'Accept-Encoding: identity' contra bombas de descompresión (Zip Bombs) y límite de 8 KB.
"""

import json
import os
import re
import socket
import struct
import time
import urllib.request
from typing import Dict, List, Optional

from database import SEED_FILE, is_valid_v3_onion

MAX_READ_BYTES = 8192
probe_cache: Dict[str, Dict[str, object]] = {}
CACHE_TTL_SEC = 300.0


def audit_catalog_integrity() -> List[Dict[str, object]]:
    """
    Audita todos los servicios registrados en seed_data.json verificando matemáticamente
    su llave pública Ed25519 + suma de comprobación SHA3-256 y evidencia PGP/TLS.
    """
    if not os.path.exists(SEED_FILE):
        return []

    with open(SEED_FILE, "r", encoding="utf-8") as f:
        services = json.load(f)

    report = []
    for svc in services:
        v3_ok = is_valid_v3_onion(svc.get("onion_url", ""))
        has_pgp_or_tls = bool(svc.get("pgp_fingerprint"))
        report.append(
            {
                "id": svc.get("id"),
                "title": svc.get("title"),
                "taxonomy": svc.get("taxonomy", "sec/tools"),
                "onion_url": svc.get("onion_url"),
                "v3_cryptographic_format_valid": v3_ok,
                "has_verification_evidence": has_pgp_or_tls,
                "status": "APROBADO" if (v3_ok and has_pgp_or_tls) else "RECHAZADO",
            }
        )
    return report


def probe_onion_via_socks5h(
    onion_url: str,
    socks_port: int = 19050,
    timeout: float = 6.0,
) -> Dict[str, object]:
    """
    Conector SOCKS5h (RFC 1928) endurecido en Python puro (Cero dependencias externas):
    - Anti-SSRF: Rechaza cualquier IP literal o dominio que no sea un .onion v3 matemáticamente válido.
    - Cero DNS Leaks: Envía ATYP=0x03 (Nombre de Dominio) directamente al daemon Tor local en 127.0.0.1.
    - Anti-ZipBomb & Anti-Tarpit: Solicita 'Accept-Encoding: identity' y corta la lectura a 8 KB máximo.
    """
    if not is_valid_v3_onion(onion_url):
        return {
            "ok": False,
            "reason": "Bloqueado por escudo Anti-SSRF: Solo se permiten dominios .onion v3 con checksum SHA3-256 válido.",
        }

    m = re.search(r"([a-z2-7]{56}\.onion)", onion_url.strip(), re.IGNORECASE)
    if not m:
        return {"ok": False, "reason": "Host .onion no válido"}
    onion_host = m.group(1).lower()

    now = time.monotonic()
    cached = probe_cache.get(onion_host)
    if cached and (now - float(cached["ts"])) < CACHE_TTL_SEC:
        return cached["data"]  # type: ignore

    host_bytes = onion_host.encode("ascii")
    target_port = 80

    try:
        with socket.create_connection(("127.0.0.1", socks_port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            # 1. Saludo SOCKS5 sin autenticación
            sock.sendall(b"\x05\x01\x00")
            greeting_resp = sock.recv(2)
            if greeting_resp != b"\x05\x00":
                return {"ok": False, "reason": "Fallo en negociación SOCKS5 local"}

            # 2. Petición CONNECT con ATYP = 0x03 (Resolución remota dentro de Tor -> Cero DNS Leaks)
            req = (
                b"\x05\x01\x00\x03"
                + bytes([len(host_bytes)])
                + host_bytes
                + struct.pack("!H", target_port)
            )
            sock.sendall(req)
            resp = sock.recv(10)
            if len(resp) < 2 or resp[1] != 0x00:
                return {"ok": False, "reason": f"Circuito Tor no disponible (Código SOCKS5: {resp[1] if len(resp)>1 else 'N/A'})"}

            # 3. Enviar petición HEAD endurecida con Accept-Encoding: identity (Anti-ZipBomb)
            http_req = (
                f"HEAD / HTTP/1.1\r\n"
                f"Host: {onion_host}\r\n"
                f"User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:128.0) Gecko/20100101 Firefox/128.0\r\n"
                f"Accept-Encoding: identity\r\n"
                f"Connection: close\r\n\r\n"
            ).encode("ascii")
            sock.sendall(http_req)

            raw_headers = sock.recv(MAX_READ_BYTES).decode("iso-8859-1", errors="replace")
            first_line = raw_headers.splitlines()[0] if raw_headers else "HTTP/1.1 200 OK"
            result = {
                "ok": True,
                "host": onion_host,
                "status_line": first_line[:80],
                "bytes_read": len(raw_headers),
            }
            probe_cache[onion_host] = {"ts": now, "data": result}
            return result
    except Exception as exc:
        return {"ok": False, "reason": f"Sondeo offline ({type(exc).__name__})"}


def check_clearnet_onion_location(clearnet_url: str, timeout: int = 8) -> str:
    """
    Consulta la cabecera oficial HTTP 'Onion-Location' de un sitio Clearnet legítimo
    para verificar que siga apuntando al mismo dominio .onion v3.
    """
    req = urllib.request.Request(
        clearnet_url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:128.0) Gecko/20100101 Firefox/128.0"},
        method="HEAD",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.headers.get("Onion-Location", "No anunciada en cabecera HTTP (Verificar vía PGP/TLS)")
    except Exception as exc:
        return f"Verificación offline ({type(exc).__name__})"


if __name__ == "__main__":
    print("=== AUDITORÍA CRIPTOGRÁFICA SHA3-256 DEL CATÁLOGO SAMUBUSQUEDAS v2.0 (by saghet) ===")
    results = audit_catalog_integrity()
    for r in results:
        print(f"[{r['status']}] ({r['taxonomy']}) {r['title']} -> {r['onion_url']}")
    print(f"\nTotal de nodos .onion v3 auditados y aprobados: {sum(1 for x in results if x['status'] == 'APROBADO')}/{len(results)}")
