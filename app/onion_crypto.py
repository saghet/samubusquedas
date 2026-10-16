"""
Generador y Validador Criptográfico SHA3-256 de Direcciones Tor Onion v3
------------------------------------------------------------------------
Según la especificación oficial de Tor (rend-spec-v3.txt):
  onion_address = base32(PUBKEY || CHECKSUM || VERSION) + ".onion"
  CHECKSUM = H(".onion checksum" || PUBKEY || VERSION)[:2]
  donde:
    - H es SHA3-256
    - PUBKEY son 32 bytes (Ed25519)
    - VERSION es 1 byte (0x03)
"""

import base64
import hashlib


def build_valid_v3_onion_from_seed(seed_label: str, vanity_prefix: str = "") -> str:
    """Genera una dirección .onion v3 matemáticamente válida (con checksum SHA3-256 real) a partir de una semilla o prefijo."""
    raw_pubkey = bytearray(hashlib.sha256(seed_label.encode("utf-8")).digest())
    if vanity_prefix:
        # Ajustar primeros bytes para que en Base32 comience con el prefijo deseado
        clean_prefix = "".join(c for c in vanity_prefix.lower() if c in "abcdefghijklmnopqrstuvwxyz234567")
        padded = clean_prefix + "a" * ((8 - len(clean_prefix) % 8) % 8)
        prefix_bytes = base64.b32decode(padded.upper())
        raw_pubkey[: len(prefix_bytes)] = prefix_bytes[: min(len(prefix_bytes), 32)]

    pubkey = bytes(raw_pubkey[:32])
    version = b"\x03"
    checksum_input = b".onion checksum" + pubkey + version
    checksum = hashlib.sha3_256(checksum_input).digest()[:2]
    onion_host = base64.b32encode(pubkey + checksum + version).decode("ascii").lower()
    return onion_host + ".onion"


def verify_v3_onion_checksum(onion_host_or_url: str) -> bool:
    """
    Verifica matemáticamente los 56 caracteres Base32 de una dirección .onion v3:
    1. Longitud exacta de 56 caracteres Base32 (35 bytes decodificados).
    2. Byte de versión == 0x03.
    3. Primeros 2 bytes de SHA3-256('.onion checksum' || pubkey || 0x03) coinciden con el checksum embebido.
    """
    import re

    m = re.search(r"([a-z2-7]{56})\.onion", onion_host_or_url.strip(), re.IGNORECASE)
    if not m:
        return False
    host = m.group(1).upper()
    try:
        decoded = base64.b32decode(host)
    except Exception:
        return False
    if len(decoded) != 35:
        return False
    pubkey = decoded[:32]
    checksum = decoded[32:34]
    version = decoded[34:35]
    if version != b"\x03":
        return False
    expected_checksum = hashlib.sha3_256(b".onion checksum" + pubkey + version).digest()[:2]
    return checksum == expected_checksum
