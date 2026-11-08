"""
Gamer Search Engine - Escudo de Ciberseguridad y Reputación de Fuentes
======================================================================
Analiza dominios, evalúa reputación (0-100), detecta enlaces maliciosos,
trampas de falsas descargas, extensiones peligrosas (.exe, .scr, .bat, .apk sospechosas)
y emite advertencias técnicas preventivas.
"""

import re
import urllib.parse
from typing import Dict, List, Optional, Set, Tuple
from gamer_models import SourceSecurityReport

# Dominios oficiales de máxima reputación (95 - 100)
TRUSTED_GAMING_DOMAINS: Dict[str, Tuple[float, str]] = {
    # Repositorios y preservación oficial
    "github.com": (100.0, "Repositorio oficial de código abierto revisado por pares"),
    "archive.org": (100.0, "Archivo cultural sin fines de lucro con excepción DMCA oficial"),
    "speedrun.com": (98.0, "Comunidad y tablas de récords mundiales verificadas por moderadores"),
    "wikipedia.org": (96.0, "Enciclopedia comunitaria verificada"),
    "wikidata.org": (97.0, "Base de datos estructurada abierta de Wikidata"),
    # Fabricantes oficiales
    "nintendo.com": (100.0, "Portal oficial de Nintendo"),
    "playstation.com": (100.0, "Portal oficial de Sony PlayStation"),
    "xbox.com": (100.0, "Portal oficial de Microsoft Xbox"),
    # Emuladores oficiales verificados
    "retroarch.com": (99.0, "Sitio oficial de RetroArch / Libretro"),
    "dolphin-emu.org": (99.0, "Sitio oficial del emulador Dolphin"),
    "pcsx2.net": (99.0, "Sitio oficial del emulador PCSX2"),
    "rpcs3.net": (99.0, "Sitio oficial del emulador RPCS3"),
    "ppsspp.org": (98.0, "Sitio oficial del emulador PPSSPP"),
    "xemu.app": (98.0, "Sitio oficial del emulador xemu"),
    "xenia.jp": (98.0, "Sitio oficial del emulador Xenia"),
    "vita3k.org": (98.0, "Sitio oficial del emulador Vita3K"),
    "shipofharkinian.com": (98.0, "Sitio oficial del proyecto Ship of Harkinian"),
    # Comunidades y guías consolidadas
    "reddit.com": (92.0, "Comunidad de foros moderada"),
    "gamefaqs.gamespot.com": (94.0, "Base de datos histórica de trucos y guías de GameFAQs"),
    "playstationtrophies.org": (92.0, "Comunidad y guías de trofeos de PlayStation"),
    "trueachievements.com": (93.0, "Comunidad oficial de seguimiento de logros de Xbox"),
    "powerpyx.com": (94.0, "Guías profesionales de trofeos y platino"),
    "fextralife.com": (90.0, "Wikis comunitarias especializadas en RPGs y Soulslike"),
    "nintendolife.com": (92.0, "Portal de noticias y foros de Nintendo"),
    "resetera.com": (88.0, "Foro comunitario independiente de videojuegos"),
}

# Dominios o TLDs conocidos de distribución de adware, instaladores falsos o estafas
SUSPICIOUS_DOMAINS: Set[str] = {
    "freerobuxgenerator.com",
    "freevbucks.net",
    "switchromsfree.com",
    "crackgamespc.net",
    "downloadfreeisopc.com",
    "romspackgenerator.online",
    "emulatorbiosdownload.cc",
    "keygenserialsfree.biz",
}

# Extensiones de archivo que representan riesgo de ejecución arbitraria
DANGEROUS_EXTENSIONS: Set[str] = {
    ".exe", ".scr", ".bat", ".cmd", ".vbs", ".js", ".msi", ".jar", ".pif", ".ps1"
}

# Extensiones de preservación seguras habituales
SAFE_GAMING_EXTENSIONS: Set[str] = {
    ".ips", ".bps", ".ups", ".xdelta", ".patch", ".zip", ".7z", ".tar.gz",
    ".nes", ".sfc", ".smc", ".z64", ".n64", ".gb", ".gbc", ".gba", ".nds", ".3dsx",
    ".chd", ".cso", ".pbp", ".pdf", ".txt", ".md"
}


class GamerSecurityShield:
    """Escudo de seguridad para análisis de enlaces, reputación de dominios y prevención de malware."""

    def evaluate_url(self, target_url: str) -> SourceSecurityReport:
        """Evalúa una URL y genera un informe de seguridad y reputación con flags y nivel de riesgo."""
        if not target_url or not target_url.strip():
            return SourceSecurityReport(
                domain="",
                reputation_score=0.0,
                safety_tier="PELIGROSO_BLOQUEADO",
                warning_message="URL vacía o no válida",
                is_known_malicious=True
            )

        parsed = urllib.parse.urlparse(target_url.strip())
        domain = parsed.netloc.lower()
        # Remover puerto si existe
        if ":" in domain:
            domain = domain.split(":")[0]
        # Remover prefijo www.
        if domain.startswith("www."):
            clean_domain = domain[4:]
        else:
            clean_domain = domain

        flags: List[str] = []
        is_known_malicious = False
        has_fake_download_traps = False
        reputation = 75.0  # Base neutral para sitios web estándar
        warning_msg = ""

        # 1. Validación de HTTPS
        if parsed.scheme.lower() == "https":
            flags.append("https_cifrado_valido")
            reputation += 5.0
        else:
            flags.append("http_inseguro_sin_cifrar")
            reputation -= 20.0
            warning_msg = "La conexión no utiliza cifrado seguro HTTPS."

        # 2. Análisis de dominios sospechosos conocidos
        if clean_domain in SUSPICIOUS_DOMAINS or any(clean_domain.endswith("." + bad) for bad in SUSPICIOUS_DOMAINS):
            is_known_malicious = True
            has_fake_download_traps = True
            reputation = 10.0
            flags.append("dominio_malicioso_identificado")
            warning_msg = "ALERTA CRÍTICA: Dominio reportado en listas de amenazas por distribuir instaladores fraudulentos o malware."

        # 3. Análisis de dominios verificados oficiales
        matched_trusted = None
        for trusted_dom, (t_score, reason) in TRUSTED_GAMING_DOMAINS.items():
            if clean_domain == trusted_dom or clean_domain.endswith("." + trusted_dom):
                matched_trusted = (t_score, reason)
                break

        if matched_trusted:
            t_score, reason = matched_trusted
            reputation = t_score
            flags.append("fuente_oficial_verificada")
            flags.append("sin_malware")
            flags.append("sin_falsas_descargas")

        # 4. Análisis de la ruta y extensión del archivo
        path_lower = parsed.path.lower()
        detected_ext = None
        for ext in DANGEROUS_EXTENSIONS:
            if path_lower.endswith(ext):
                detected_ext = ext
                break

        if detected_ext:
            has_fake_download_traps = True
            reputation = min(reputation, 30.0)
            flags.append(f"archivo_ejecutable_peligroso_{detected_ext}")
            warning_msg = f"ADVERTENCIA DE SEGURIDAD: El enlace apunta a un archivo ejecutable ({detected_ext}). El motor nunca descarga ni ejecuta archivos automáticamente. Verifica la procedencia antes de ejecutar cualquier archivo."

        # Si apunta a parches limpios
        for safe_ext in SAFE_GAMING_EXTENSIONS:
            if path_lower.endswith(safe_ext):
                flags.append(f"formato_preservacion_seguro_{safe_ext}")
                break

        # 5. Determinación del Nivel de Seguridad (Tier)
        reputation = max(0.0, min(100.0, reputation))
        if reputation >= 90.0 and not is_known_malicious and not has_fake_download_traps:
            safety_tier = "CONFIABLE_VERIFICADO"
        elif reputation >= 65.0 and not is_known_malicious:
            safety_tier = "COMUNITARIO_SEGURO"
        elif reputation >= 40.0 and not is_known_malicious:
            safety_tier = "PRECAUCION"
        else:
            safety_tier = "PELIGROSO_BLOQUEADO"

        return SourceSecurityReport(
            domain=clean_domain,
            reputation_score=round(reputation, 1),
            safety_tier=safety_tier,
            flags=flags,
            warning_message=warning_msg,
            is_known_malicious=is_known_malicious,
            has_fake_download_traps=has_fake_download_traps
        )


# Instancia de seguridad singleton
GAMER_SECURITY = GamerSecurityShield()
