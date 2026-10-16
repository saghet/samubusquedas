from typing import Dict


# Indicadores conocidos de pasarelas Tor2Web (proxies inseguros que rompen el cifrado E2E de Tor)
TOR2WEB_HEADERS = (
    "x-tor2web",
    "x-tor2web-encrypted",
    "cf-connecting-ip",
    "x-forwarded-host",
)

TOR2WEB_HOST_SUFFIXES = (
    ".onion.ly",
    ".onion.ws",
    ".onion.pet",
    ".onion.dog",
    ".onion.link",
    ".tor2web.org",
)


def evaluate_client_connection_security(headers: Dict[str, str]) -> Dict[str, object]:
    """
    Evalúa pasivamente (sin almacenar logs ni IPs) las cabeceras de la petición HTTP
    para proteger al usuario frente a riesgos de desanonimización, proxies Tor2Web
    o navegadores convencionales mal configurados.
    """
    normalized = {k.lower(): v for k, v in headers.items()}
    warnings = []
    risk_level = "SEGURO"

    # 1. Detección de proxies Tor2Web (Riesgo Crítico de Interceptación MitM)
    host = normalized.get("host", "").lower()
    is_tor2web = any(h in normalized for h in TOR2WEB_HEADERS) or any(
        host.endswith(suffix) for suffix in TOR2WEB_HOST_SUFFIXES
    )

    if is_tor2web:
        risk_level = "CRÍTICO"
        warnings.append(
            "ALERTA CRÍTICA: Estás accediendo mediante un proxy intermedio (Tor2Web / Gateway). "
            "El operador de ese proxy puede leer todo tu tráfico, inyectar código malicioso y ver tu IP real. "
            "Descarga y utiliza exclusivamente Tor Browser oficial."
        )

    # 2. Inspección del User-Agent para detectar huella digital (Browser Fingerprinting)
    user_agent = normalized.get("user-agent", "")
    # Tor Browser estandariza su User-Agent a Firefox ESR genérico
    is_likely_tor_browser = (
        "Firefox/" in user_agent
        and "Chrome/" not in user_agent
        and "Edg/" not in user_agent
        and "Safari/" not in user_agent
    )

    if not is_likely_tor_browser and risk_level != "CRÍTICO":
        risk_level = "ADVERTENCIA"
        warnings.append(
            "Tu navegador envía un identificador (User-Agent) distinto al estándar de Tor Browser. "
            "Esto facilita ataques de 'Browser Fingerprinting' en la Deep Web. Asegúrate de usar Tor Browser sin extensiones adicionales."
        )

    # 3. Verificación de envío accidental de Referer
    if "referer" in normalized:
        warnings.append(
            "Se detectó una cabecera 'Referer' en tu petición. SamuBusquedas bloquea automáticamente "
            "el reenvío de Referer hacia enlaces externos mediante 'Referrer-Policy: no-referrer'."
        )

    return {
        "risk_level": risk_level,
        "is_tor2web": is_tor2web,
        "is_likely_tor_browser": is_likely_tor_browser,
        "warnings": warnings,
        "active_protections": [
            "Zero-JS Activo (CSP script-src 'none')",
            "Zero-Logs en RAM (:memory:)",
            "Bloqueo de Referer Saliente (no-referrer)",
            "Aislamiento de Marcos (X-Frame-Options: DENY)",
        ],
    }
