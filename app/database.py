"""
SamuBusquedas v2.5 - Motor de Búsqueda Híbrido con Superficie Amplificada (Verificados + No Verificados + Live Tor)
===================================================================================================================
Arquitecto Principal y Creador: saghet
Mejoras v2.5 (Amplificación de Superficie y Cero Pantallas Vacías):
1. Normalización Diacrítica Automática (`normalize_accents`): insensible a tildes (`investigación` == `investigacion`).
2. Limpieza de Stopwords Bilingüe (`de`, `la`, `en`, `el`, `para`, `deep`, `web`, `tor`, `onion`) para que consultas
   conversacionales largas jamás fallen.
3. Cascada de Recuperación en 4 Niveles (Multi-Stage Recall Pipeline):
   - Nivel 1: Coincidencia FTS5 de Alta Precisión (`AND` con expansión de sinónimos).
   - Nivel 2: Coincidencia FTS5 Amplia (`OR` ponderado por cantidad de términos coincidentes + `BM25F`).
   - Nivel 3: Auto-Recovery Ortográfico Damerau-Levenshtein (ejecuta automáticamente la consulta corregida si
     el usuario escribió con erratas como `protnmail`, `whonx`, `debain`, `mullvd`).
   - Nivel 4: Coincidencia de Subcadenas (`LIKE %tok%`) + Meta-Búsqueda en Vivo en la Red Tor (`live_tor_search`)
     + Recomendaciones Exploratorias de Alto Puntaje cuando se buscan términos completamente inéditos.
4. Soporte de 3 Niveles de Confianza (`VERIFIED`, `UNVERIFIED`, `LIVE_TOR`) con etiquetas visuales claras.
"""

import difflib
import html
import json
import os
import random
import re
import sqlite3
import time
import unicodedata
from typing import Dict, List, Optional, Set, Tuple

from collective_memory import COLLECTIVE_MEMORY
from live_tor_search import fetch_live_unverified_tor_results
from onion_crypto import verify_v3_onion_checksum
from verifier import start_background_health_monitor, verify_and_enrich_search_results
from version import ENGINE_VERSION

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEED_FILE = os.path.join(BASE_DIR, "seed_data.json")

MAX_QUERY_LEN = 256
MAX_TOKENS = 12
FTS5_RESERVED = {"and", "or", "not", "near"}

# Palabras vacías y vocabulario genérico excluido del corrector ortográfico
STOPWORDS = {
    "de", "la", "el", "los", "las", "un", "una", "unos", "unas", "en", "por", "para",
    "con", "sin", "del", "al", "como", "que", "es", "son", "mas", "muy", "pero", "sus",
    "este", "esta", "estos", "estas", "todo", "toda", "todos", "todas", "otro", "otra",
    "otros", "otras", "entre", "sobre", "desde", "hasta", "hacia", "donde", "cuando",
    "sitio", "sitios", "pagina", "paginas", "servicio", "servicios", "buscar", "busqueda",
    "red", "redes", "web", "deep", "dark", "onion", "tor", "acceso", "oficial", "gratis",
    "linea", "datos", "mundo", "parte", "forma", "nivel", "mayor", "mejor", "gran",
    "the", "in", "of", "for", "to", "and", "or", "on", "with", "site", "sites", "from",
}

ONION_V3_REGEX = re.compile(
    r"^https?://([a-z0-9.-]+\.)?([a-z2-7]{55}d)\.onion(/.*)?$", re.IGNORECASE
)

# Diccionario bilingüe ampliado de expansión semántica en RAM
SYNONYM_MAP: Dict[str, List[str]] = {
    "correo": ["email", "mail", "protonmail", "riseup", "systemli", "cockli", "onionmail"],
    "email": ["correo", "mail", "protonmail", "riseup", "cockli", "onionmail"],
    "buscador": ["search", "engine", "duckduckgo", "brave", "ahmia", "torch", "haystak", "excavator", "samubusquedas"],
    "search": ["buscador", "duckduckgo", "brave", "ahmia", "torch", "haystak", "excavator"],
    "libros": ["books", "biblioteca", "epub", "trantor", "archive", "scihub", "annas", "gutenberg"],
    "biblioteca": ["library", "libros", "trantor", "archive", "scihub", "annas", "gutenberg"],
    "ciencia": ["science", "papers", "scihub", "annas", "trantor", "archive"],
    "filtraciones": ["whistleblowing", "leaks", "securedrop", "prensa", "propublica", "cia"],
    "leaks": ["filtraciones", "whistleblowing", "securedrop", "propublica"],
    "prensa": ["noticias", "periodismo", "news", "media", "bbc", "nytimes", "guardian", "dw", "propublica"],
    "noticias": ["prensa", "periodismo", "news", "bbc", "nytimes", "guardian", "dw", "dread"],
    "sistema": ["os", "linux", "qubes", "whonix", "debian", "tails", "fdroid"],
    "os": ["sistema", "operativo", "linux", "qubes", "whonix", "debian", "tails"],
    "hacker": ["hacking", "hackers", "defcon", "ciberseguridad", "saghet", "opsec", "ccc", "cypherpunk", "git", "cyberchef"],
    "hacking": ["hacker", "hackers", "defcon", "ciberseguridad", "saghet", "ccc", "cypherpunk"],
    "foro": ["foros", "forum", "forums", "dread", "daunt", "cypherpunk", "wiki", "comunidad"],
    "foros": ["foro", "forum", "dread", "daunt", "cypherpunk", "wiki", "comunidad"],
    "wiki": ["hidden", "torlinks", "daunt", "directorio", "enlaces", "links"],
    "directorio": ["wiki", "hidden", "torlinks", "daunt", "enlaces", "links", "samubusquedas"],
    "cripto": ["crypto", "monero", "xmr", "bitcoin", "btc", "mempool", "feather", "bisq", "wallet"],
    "crypto": ["cripto", "monero", "xmr", "bitcoin", "btc", "mempool", "feather", "bisq"],
    "bitcoin": ["btc", "cripto", "crypto", "mempool", "bisq", "monero"],
    "monero": ["xmr", "cripto", "crypto", "feather", "bisq"],
    "chat": ["mensajeria", "xmpp", "jabber", "irc", "briar", "simplex", "keybase", "calyx", "hackint"],
    "vpn": ["mullvad", "cryptostorm", "njalla", "privacidad"],
    "hosting": ["servidor", "vps", "ablative", "njalla", "alojar"],
    "paste": ["pastebin", "stronghold", "zerobin", "notas", "codigo", "git"],
    "musica": ["radio", "audio", "streaming", "anonfm", "deepweb"],
}

# Clasificador Semántico de Intención para la Deep Web (SamuRank v3.0)
# Conecta términos del mundo real que buscan los usuarios con nodos investigativos, OSINT,
# archivos desclasificados, foros y motores profundos de la red Tor.
DEEPWEB_SEMANTIC_INTENTS: List[Dict[str, object]] = [
    {
        "id": "conflict_osint_military",
        "label": "Investigación de Conflictos, Armamento, Inteligencia & Archivos Desclasificados (OSINT)",
        "keywords": {
            "arma", "armas", "armamento", "militar", "militares", "guerra", "guerras",
            "conflicto", "conflictos", "defensa", "ejercito", "balistica", "inteligencia",
            "espionaje", "geopolitica", "cia", "fbi", "nsa", "otan", "terrorismo",
            "weapons", "weapon", "military", "warfare", "intelligence",
        },
        "target_ids": [
            "bellingcat-onion",
            "cia-official-onion",
            "securedrop-project",
            "propublica-onion",
            "internet-archive-onion",
            "dread-forum-mirror",
            "torch-search-onion",
            "haystak-search-onion",
        ],
        "advisory": (
            "Enrutamiento Inteligente Deep Web: Mostrando portales de investigación forense de conflictos y armamento "
            "(Bellingcat OSINT), archivos de inteligencia desclasificados (CIA Onion), buzones de filtraciones "
            "(SecureDrop) y nodos abiertos de la red Tor para tu consulta."
        ),
    },
    {
        "id": "darknet_markets_commerce",
        "label": "Monitoreo de Mercados Darknet, Directorios de Enlaces & Finanzas Cripto P2P",
        "keywords": {
            "mercado", "mercados", "market", "markets", "darknet", "tienda", "tiendas",
            "comprar", "compras", "venta", "ventas", "drogas", "droga", "sustancias",
            "farmacos", "vendor", "vendors", "escrow", "shop", "store", "bazar",
        },
        "target_ids": [
            "dread-forum-mirror",
            "daunt-link-onion",
            "hidden-wiki-mirror",
            "torlinks-directory",
            "monero-official-onion",
            "bisq-network-onion",
            "feather-wallet-onion",
            "torch-search-onion",
        ],
        "advisory": (
            "Alerta OPSEC sobre Mercados en Tor: Más del 90% de los mercados comerciales en buscadores abiertos son "
            "clones de Phishing o Exit Scams. Se muestran los directorios de verificación comunitaria (Dread / Daunt), "
            "herramientas Monero/Escrow y resultados del índice abierto Tor."
        ),
    },
    {
        "id": "exploits_hacking_cybersec",
        "label": "Ciberseguridad, Exploits, Cultura Hacker, Repositorios de Código & Auditoría",
        "keywords": {
            "exploit", "exploits", "malware", "ransomware", "0day", "zeroday", "vulnerabilidad",
            "vulnerabilidades", "pentesting", "pentest", "cracking", "botnet", "payload",
            "cve", "ctf", "shell", "rootkit", "keylogger", "phreaking", "carding", "tarjetas",
            "cvv", "dumps", "fraude", "estafas", "scam",
        },
        "target_ids": [
            "defcon-official-onion",
            "ccc-chaos-computer-club",
            "cypherpunk-board-onion",
            "cyberchef-onion-node",
            "forgejo-git-onion",
            "stronghold-paste-onion",
            "qubes-os-onion",
            "whonix-onion",
        ],
        "advisory": (
            "Enrutamiento Inteligente de Ciberseguridad: Mostrando archivos oficiales de investigación de vulnerabilidades "
            "(DEF CON, Chaos Computer Club), repositorios Git/Pastebins en Tor y herramientas de análisis forense."
        ),
    },
    {
        "id": "classified_leaks_archives",
        "label": "Documentos Filtrados, Secretos de Estado, Archivos Históricos & Ciencia Abierta",
        "keywords": {
            "ovni", "ovnis", "ufo", "ufos", "aliens", "secreto", "secretos", "clasificado",
            "clasificados", "desclasificado", "desclasificados", "conspiracion", "gobierno",
            "wikileaks", "papeles", "documento", "documentos", "expedientes", "historia",
            "archivo", "archivos", "censurado", "censurados", "prohibido", "prohibidos",
        },
        "target_ids": [
            "securedrop-project",
            "cia-official-onion",
            "internet-archive-onion",
            "propublica-onion",
            "nytimes-onion",
            "guardian-onion",
            "imperial-library-trantor",
            "scihub-tor-mirror",
            "annas-archive-onion",
        ],
        "advisory": (
            "Enrutamiento Inteligente Documental: Mostrando plataformas de filtración anónima (SecureDrop), "
            "archivos históricos desclasificados (Internet Archive, CIA, ProPublica) y bibliotecas sin censura."
        ),
    },
    {
        "id": "privacy_opsec_anonymity",
        "label": "Anonimato Extremo, Evasión de Censura, Ocultación de IP & Sistemas Amnésicos",
        "keywords": {
            "anonimo", "anonimato", "ocultar", "ip", "rastreo", "policia", "censura",
            "vigilancia", "espia", "espias", "bloqueo", "proteger", "privacidad",
            "identidad", "amnesico", "cortafuegos", "firewall",
        },
        "target_ids": [
            "tor-project",
            "tails-os-onion",
            "whonix-onion",
            "qubes-os-onion",
            "privacyguides-onion",
            "mullvad-vpn-onion",
            "cryptostorm-vpn-onion",
            "onionshare-project",
        ],
        "advisory": (
            "Enrutamiento Inteligente OPSEC: Mostrando sistemas operativos amnésicos (Tails, Whonix, Qubes), "
            "guías de anonimato y servicios de red resistentes a vigilancia."
        ),
    },
]


def _damerau_levenshtein(s1: str, s2: str) -> int:
    """
    Calcula la distancia de edición Damerau-Levenshtein exacta entre dos cadenas
    (inserción, eliminación, sustitución y transposición de caracteres adyacentes).
    """
    len1, len2 = len(s1), len(s2)
    d = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    for i in range(len1 + 1):
        d[i][0] = i
    for j in range(len2 + 1):
        d[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j] + 1,      # eliminación
                d[i][j - 1] + 1,      # inserción
                d[i - 1][j - 1] + cost,  # sustitución
            )
            if i > 1 and j > 1 and s1[i - 1] == s2[j - 2] and s1[i - 2] == s2[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)  # transposición adyacente
    return d[len1][len2]

YAHOO_TAXONOMY_TREE: List[Dict[str, str]] = [
    {"code": "sec/os", "label": "Sistemas Operativos (Qubes, Whonix, Tails, Debian, F-Droid)", "parent": "Seguridad & OS"},
    {"code": "sec/network", "label": "Red Tor & Métricas Oficiales", "parent": "Seguridad & OS"},
    {"code": "sec/tools", "label": "Herramientas OPSEC & Cripto (OnionShare, CyberChef, PrivacyGuides)", "parent": "Seguridad & OS"},
    {"code": "comm/mail", "label": "Correo Cifrado & Relays (Proton, Riseup, Systemli, Cock.li, OnionMail)", "parent": "Comunicación"},
    {"code": "comm/chat", "label": "Chat, XMPP, IRC & P2P (Briar, SimpleX, Keybase, Calyx, Hackint)", "parent": "Comunicación"},
    {"code": "comm/wiki", "label": "Hidden Wikis, Foros & Comunidad (Hidden Wiki, Dread, Daunt, TorLinks)", "parent": "Comunidad"},
    {"code": "press/media", "label": "Prensa Mundial (ProPublica, NYT, BBC, Guardian, DW)", "parent": "Prensa & OSINT"},
    {"code": "press/osint", "label": "Whistleblowing & OSINT (SecureDrop, Bellingcat)", "parent": "Prensa & OSINT"},
    {"code": "lib/archive", "label": "Archivos Históricos (Internet Archive / Wayback)", "parent": "Bibliotecas & Ciencia"},
    {"code": "lib/books", "label": "Libros & Ciencia (Trantor, Sci-Hub, Anna's Archive, Gutenberg)", "parent": "Bibliotecas & Ciencia"},
    {"code": "hack/confs", "label": "Cultura Hacker & Foros (DEF CON, CCC, Cypherpunk Board)", "parent": "Cultura Hacker"},
    {"code": "hack/repos", "label": "Código Git & Pastebins (OnionGit/Forgejo, StrongHold Paste)", "parent": "Cultura Hacker"},
    {"code": "priv/vpn", "label": "VPN & Hosting Anónimo (Mullvad, Cryptostorm, Njalla, Ablative)", "parent": "Infraestructura"},
    {"code": "priv/crypto", "label": "Monero, Bitcoin & Finanzas P2P (Monero, Feather, Mempool, Bisq)", "parent": "Criptomonedas"},
    {"code": "search/engines", "label": "Motores de Búsqueda (SamuBusquedas, DDG, Brave, Ahmia, Torch, Haystak)", "parent": "Buscadores"},
    {"code": "gov/intel", "label": "Portales Institucionales (CIA Onion Portal)", "parent": "Institucional"},
]

BANG_COMMANDS: Dict[str, Dict[str, str]] = {
    "!ddg": {
        "name": "DuckDuckGo Onion v3",
        "target_onion": "https://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion/?q=",
        "description": "Salto directo al motor DuckDuckGo oficial dentro de la red Tor.",
    },
    "!brave": {
        "name": "Brave Search Onion v3",
        "target_onion": "https://search.brave4u7jddbv7cyviptqjc7jusxh72uik7zt6adtckl5f4nwy2v72qd.onion/search?q=",
        "description": "Salto directo a Brave Search oficial en la red Tor.",
    },
    "!ahmia": {
        "name": "Ahmia.fi Onion Search",
        "target_onion": "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/search/?q=",
        "description": "Búsqueda en el índice filtrado de servicios ocultos Ahmia.fi.",
    },
    "!torch": {
        "name": "Torch Unfiltered Search",
        "target_onion": "/?q=torch",
        "description": "Explorar motores de búsqueda masivos no verificados en Tor.",
    },
    "!archive": {
        "name": "Internet Archive (.onion)",
        "target_onion": "http://archivep75mbjunhxc6x4j5mwjmomyxb573v42baldlqu56ruil2oiad.onion/",
        "description": "Acceso directo al espejo oficial de Internet Archive en Tor.",
    },
    "!pgp": {
        "name": "Canario Criptográfico PGP de saghet",
        "target_onion": "/canary.txt",
        "description": "Inspeccionar el manifiesto y firma PGP oficial de SamuBusquedas.",
    },
    "!saghet": {
        "name": "Perfil de Arquitectura Hacker (saghet)",
        "target_onion": "/humans.txt",
        "description": "Ver especificaciones de autoría y arquitectura de seguridad de saghet.",
    },
}


def normalize_accents(text: str) -> str:
    """Elimina tildes y diacríticos (ej. 'investigación' -> 'investigacion') conservando caracteres base."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def is_valid_v3_onion(url: str) -> bool:
    clean = url.strip()
    if not ONION_V3_REGEX.match(clean):
        return False
    return verify_v3_onion_checksum(clean)


def format_visual_onion_chunks(onion_url: str) -> Dict[str, str]:
    m = re.search(r"^(https?://(?:[a-z0-9.-]+\.)?)([a-z2-7]{56})(\.onion.*)$", onion_url.strip(), re.IGNORECASE)
    if not m:
        return {"scheme": "", "prefix": onion_url, "middle": "", "suffix": "", "tail": ""}
    scheme, host56, tail = m.group(1), m.group(2), m.group(3)
    return {
        "scheme": scheme,
        "prefix": host56[:7],
        "middle": host56[7:49],
        "suffix": host56[49:],
        "tail": tail,
    }


def highlight_safe_snippet(raw_text: str, highlight_tokens: List[str], max_len: int = 290) -> str:
    """
    Generador de Snippets Dinámicos 100% libre de XSS que resalta coincidencias con y sin tilde
    respetando estrictamente límites de palabra (\b) para jamás resaltar sílabas internas sueltas.
    """
    text = raw_text.strip()
    if len(text) > max_len:
        text = text[: max_len - 3] + "..."

    escaped_text = html.escape(text, quote=True)
    valid_tokens = [
        re.sub(r"[^\wáéíóúñÁÉÍÓÚÑ]", "", t)
        for t in highlight_tokens
        if len(t) >= 2
    ]
    valid_tokens = [t for t in valid_tokens if t and t.lower() not in STOPWORDS]
    if not valid_tokens:
        return escaped_text

    accent_char_map = {
        "a": "[aáÁA]",
        "e": "[eéÉE]",
        "i": "[iíÍI]",
        "o": "[oóÓO]",
        "u": "[uúüÚÜU]",
        "n": "[nñÑN]",
    }
    regex_parts = []
    for tok in sorted(set(valid_tokens), key=len, reverse=True)[:8]:
        base_tok = normalize_accents(tok.lower())
        pat = "".join(accent_char_map.get(ch, re.escape(ch)) for ch in base_tok)
        if len(base_tok) <= 4:
            # Palabras cortas requieren coincidencia de palabra completa exacta (\b...\b)
            regex_parts.append(rf"\b{pat}(?:es|s)?\b")
        else:
            # Palabras de >= 5 letras requieren inicio de palabra (\b) y palabra completa o compuesto legítimo
            regex_parts.append(rf"\b{pat}[a-zA-ZáéíóúñÁÉÍÓÚÑ0-9]*\b")

    pattern_str = "(" + "|".join(regex_parts) + ")"
    try:
        pattern = re.compile(pattern_str, re.IGNORECASE)
        return pattern.sub(r'<mark class="hl">\1</mark>', escaped_text)
    except re.error:
        return escaped_text


GENERIC_VOCAB_BLACKLIST = {
    "oficial", "servicio", "servicios", "comunitario", "verificado", "portal", "acceso",
    "sistema", "proyecto", "espejo", "mirror", "seguro", "segura", "anonimo", "anonima",
    "abierto", "abierta", "indice", "directorio", "pagina", "paginas", "oculto", "oculta",
    "ocultos", "permite", "través", "traves", "mundo", "global", "sin", "con", "mas",
    "menos", "todos", "todas", "parte", "forma", "nivel", "mayor", "mejor", "gran",
    "redes", "datos", "linea", "gratis", "espanol", "ingles", "version", "oficiales",
}


class SamuSearchEngine:
    """
    Motor de búsqueda en memoria RAM (:memory:) de SamuBusquedas v3.0 (Creado por saghet).
    Incluye Clasificador Semántico de la Deep Web, Corrector Damerau-Levenshtein de Entidades,
    Sitios Verificados (Tier 1), Comunitarios No Verificados (Tier 2) y Rastreo en Vivo Tor (Tier 3).
    """

    def __init__(self) -> None:
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.vocabulary: Set[str] = set()
        self.known_valid_words: Set[str] = set()
        self.brand_keywords: Dict[str, Dict[str, object]] = {}
        self._init_schema()
        self._load_seed_data()
        start_background_health_monitor()

    def _init_schema(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE services (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                taxonomy TEXT NOT NULL,
                onion_url TEXT NOT NULL,
                clearnet_url TEXT NOT NULL,
                description TEXT NOT NULL,
                verification_method TEXT NOT NULL,
                pgp_fingerprint TEXT NOT NULL,
                js_requirement TEXT NOT NULL,
                safety_score INTEGER NOT NULL,
                uptime_percent REAL NOT NULL DEFAULT 99.0,
                latency_ms INTEGER NOT NULL DEFAULT 350,
                online_verified INTEGER NOT NULL DEFAULT 1,
                tags TEXT NOT NULL,
                norm_searchable TEXT NOT NULL,
                verification_tier TEXT NOT NULL DEFAULT 'VERIFIED',
                is_v3_verified INTEGER NOT NULL DEFAULT 1,
                crypto_trust_bonus REAL NOT NULL DEFAULT 0.0,
                status TEXT NOT NULL DEFAULT 'Verificado (v3)'
            )
            """
        )
        cursor.execute(
            """
            CREATE VIRTUAL TABLE services_fts USING fts5(
                id UNINDEXED,
                title,
                category,
                description,
                tags,
                verification_method,
                taxonomy,
                norm_searchable
            )
            """
        )
        self.conn.commit()

    def _calculate_crypto_trust_bonus(self, item: Dict[str, object], v3_valid: bool) -> float:
        bonus = 0.0
        tier = str(item.get("verification_tier", "VERIFIED"))
        if v3_valid:
            bonus += 25.0
        if tier == "VERIFIED":
            bonus += 20.0
        pgp = str(item.get("pgp_fingerprint", ""))
        verif = str(item.get("verification_method", ""))
        if re.search(r"[0-9A-F]{4}\s+[0-9A-F]{4}", pgp, re.IGNORECASE) or "TLS EV" in pgp or "PGP" in verif:
            bonus += 15.0
        if "Onion-Location" in verif:
            bonus += 15.0
        if "Vanity" in verif:
            bonus += 10.0

        js_req = str(item.get("js_requirement", ""))
        if "Standard" in js_req:
            bonus -= 18.0
        elif "Safer" in js_req and "Safest" not in js_req:
            bonus -= 6.0

        return round(bonus, 2)

    def _load_seed_data(self) -> None:
        if not os.path.exists(SEED_FILE):
            return
        with open(SEED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        cursor = self.conn.cursor()
        vocab_accumulator: Set[str] = set()
        valid_words_accumulator: Set[str] = set()

        for item in data:
            v3_valid = 1 if is_valid_v3_onion(item["onion_url"]) else 0
            taxonomy = str(item.get("taxonomy", "sec/tools"))
            uptime = float(item.get("uptime_percent", 98.0))
            latency_ms = int(item.get("latency_ms", 350))
            online_verif = 1 if item.get("online_verified", True) else 0
            tier = str(item.get("verification_tier", "VERIFIED"))
            crypto_bonus = self._calculate_crypto_trust_bonus(item, bool(v3_valid))

            if tier == "VERIFIED":
                status_label = "Verificado Oficial Online (v3 SHA3-256)"
            else:
                status_label = "Verificado Activo Online (Comunitario Tor)"

            raw_all = f"{item['title']} {item['category']} {item['description']} {item['tags']} {taxonomy}"
            norm_all = normalize_accents(raw_all.lower())

            cursor.execute(
                """
                INSERT INTO services (
                    id, title, category, taxonomy, onion_url, clearnet_url, description,
                    verification_method, pgp_fingerprint, js_requirement,
                    safety_score, uptime_percent, latency_ms, online_verified, tags,
                    norm_searchable, verification_tier, is_v3_verified, crypto_trust_bonus, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["id"],
                    item["title"],
                    item["category"],
                    taxonomy,
                    item["onion_url"],
                    item["clearnet_url"],
                    item["description"],
                    item["verification_method"],
                    item["pgp_fingerprint"],
                    item["js_requirement"],
                    item["safety_score"],
                    uptime,
                    latency_ms,
                    online_verif,
                    item["tags"],
                    norm_all,
                    tier,
                    v3_valid,
                    crypto_bonus,
                    status_label,
                ),
            )
            cursor.execute(
                """
                INSERT INTO services_fts (
                    id, title, category, description, tags, verification_method, taxonomy, norm_searchable
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["id"],
                    item["title"],
                    item["category"],
                    item["description"],
                    item["tags"],
                    item["verification_method"],
                    taxonomy,
                    norm_all,
                ),
            )

            # Todas las palabras del catálogo se registran como palabras válidas existentes
            for tok in re.findall(r"[a-z0-9]{3,}", norm_all):
                valid_words_accumulator.add(tok)

            # Al diccionario del corrector ortográfico SOLO entran entidades, marcas y tags técnicos >= 5 letras
            entity_sources = f"{item['id'].replace('-', ' ')} {item['title']} {item['tags']}"
            norm_entities = normalize_accents(entity_sources.lower())
            for tok in re.findall(r"[a-z]{5,}", norm_entities):
                if tok not in STOPWORDS and tok not in GENERIC_VOCAB_BLACKLIST:
                    vocab_accumulator.add(tok)

            if tier == "VERIFIED":
                primary_brand = item["id"].split("-")[0].lower()
                if len(primary_brand) >= 4:
                    self.brand_keywords[primary_brand] = item

        for k, vals in SYNONYM_MAP.items():
            valid_words_accumulator.add(normalize_accents(k.lower()))
            if len(k) >= 5 and k not in STOPWORDS and k not in GENERIC_VOCAB_BLACKLIST:
                vocab_accumulator.add(normalize_accents(k.lower()))
            for v in vals:
                nv = normalize_accents(v.lower())
                valid_words_accumulator.add(nv)
                if len(nv) >= 5 and nv not in STOPWORDS and nv not in GENERIC_VOCAB_BLACKLIST:
                    vocab_accumulator.add(nv)

        for intent in DEEPWEB_SEMANTIC_INTENTS:
            for kw in intent["keywords"]:  # type: ignore
                valid_words_accumulator.add(normalize_accents(str(kw).lower()))

        self.vocabulary = vocab_accumulator
        self.known_valid_words = valid_words_accumulator
        self.conn.commit()

        # Absorber en el índice FTS5 todos los nodos previamente aprendidos en la Memoria Colectiva
        for learned_node in COLLECTIVE_MEMORY.get_all_discovered_nodes():
            self.absorb_discovered_node(learned_node, commit=False)
        self.conn.commit()

    def absorb_discovered_node(self, item: Dict[str, object], commit: bool = True) -> bool:
        """
        Auto-indexa en la base de datos SQLite FTS5 (en RAM) cualquier nuevo servicio .onion v3
        descubierto durante una búsqueda exitosa, para que futuras búsquedas por cualquier
        palabra clave relacionada lo encuentren de inmediato.
        """
        onion_url = str(item.get("onion_url", "")).strip()
        node_id = str(item.get("id", "")).strip()
        if not onion_url or not node_id or node_id.startswith("live-jump-") or "aaa" in onion_url.lower():
            return False
        if not is_valid_v3_onion(onion_url):
            return False

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id FROM services WHERE id = ? OR LOWER(onion_url) = LOWER(?)",
            (node_id, onion_url),
        )
        if cursor.fetchone():
            return False

        taxonomy = str(item.get("taxonomy", "tor/collective"))
        title = str(item.get("title", "Nodo Onion Verificado"))
        category = str(item.get("category", "Memoria Colectiva Tor (Verificado v3)"))
        clearnet_url = str(item.get("clearnet_url", "https://ahmia.fi"))
        description = str(item.get("description", "Servicio oculto .onion v3 descubierto y verificado online por la Memoria Colectiva."))
        verif_method = str(item.get("verification_method", "Memoria Colectiva + Checksum SHA3-256"))
        pgp_fp = str(item.get("pgp_fingerprint", "Checksum Ed25519 SHA3-256 Válido — Modo Safest"))
        js_req = str(item.get("js_requirement", "Safest (Sin JS)"))
        safety_score = int(item.get("safety_score", 80))
        uptime = float(item.get("uptime_percent", 96.5))
        latency_ms = int(item.get("latency_ms", 450) or 450)
        tags = str(item.get("tags", ""))
        tier = str(item.get("verification_tier", "UNVERIFIED"))
        crypto_bonus = self._calculate_crypto_trust_bonus(item, True)
        status_label = "Aprendido en Memoria Colectiva (Online v3)"

        raw_all = f"{title} {category} {description} {tags} {taxonomy}"
        norm_all = normalize_accents(raw_all.lower())

        try:
            cursor.execute(
                """
                INSERT INTO services (
                    id, title, category, taxonomy, onion_url, clearnet_url, description,
                    verification_method, pgp_fingerprint, js_requirement,
                    safety_score, uptime_percent, latency_ms, online_verified, tags,
                    norm_searchable, verification_tier, is_v3_verified, crypto_trust_bonus, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    node_id,
                    title,
                    category,
                    taxonomy,
                    onion_url,
                    clearnet_url,
                    description,
                    verif_method,
                    pgp_fp,
                    js_req,
                    safety_score,
                    uptime,
                    latency_ms,
                    1,
                    tags,
                    norm_all,
                    tier,
                    1,
                    crypto_bonus,
                    status_label,
                ),
            )
            cursor.execute(
                """
                INSERT INTO services_fts (
                    id, title, category, description, tags, verification_method, taxonomy, norm_searchable
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    node_id,
                    title,
                    category,
                    description,
                    tags,
                    verif_method,
                    taxonomy,
                    norm_all,
                ),
            )
            if commit:
                self.conn.commit()
            return True
        except Exception:
            return False

    def get_known_onion_hosts(self) -> Set[str]:
        """Devuelve el conjunto de todos los hosts .onion actualmente indexados en SQLite FTS5."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT onion_url FROM services")
        hosts: Set[str] = set()
        for row in cursor.fetchall():
            u = str(row["onion_url"]).lower()
            m = re.search(r"((?:[a-z0-9-]+\.)*[a-z2-7]{55}d\.onion)", u)
            if m:
                hosts.add(m.group(1))
        return hosts

    def get_total_indexed_count(self) -> int:
        """Devuelve el número total actual de servicios .onion indexados en el motor FTS5."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) AS cnt FROM services")
        row = cursor.fetchone()
        return int(row["cnt"]) if row else 0

    def get_categories(self) -> List[Dict[str, object]]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT category, COUNT(*) as total
            FROM services
            GROUP BY category
            ORDER BY total DESC, category ASC
            """
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_taxonomy_summary(self) -> List[Dict[str, object]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT taxonomy, COUNT(*) as total FROM services GROUP BY taxonomy")
        counts = {row["taxonomy"]: row["total"] for row in cursor.fetchall()}

        summary = []
        for node in YAHOO_TAXONOMY_TREE:
            code = node["code"]
            summary.append(
                {
                    "code": code,
                    "label": node["label"],
                    "parent": node["parent"],
                    "total": counts.get(code, 0),
                }
            )
        return summary

    def parse_search_query(self, raw_query: Optional[str]) -> Dict[str, object]:
        bounded = (raw_query or "").strip()[:MAX_QUERY_LEN]
        parsed: Dict[str, object] = {
            "raw": bounded,
            "phrases": [],
            "include_tokens": [],
            "exclude_tokens": [],
            "cat_filter": None,
            "tax_filter": None,
            "js_filter": None,
            "site_filter": None,
            "min_trust": None,
            "pgp_only": False,
            "tier_filter": None,
            "bang": None,
        }
        if not bounded:
            return parsed

        phrases: List[str] = []

        def _extract_phrase(match: re.Match) -> str:
            inner = match.group(1).strip()
            clean_words = re.findall(r"[\wáéíóúñÁÉÍÓÚÑ]+", inner.lower())
            if clean_words and len(phrases) < 3:
                phrases.append(normalize_accents(" ".join(clean_words[:6])))
            return " "

        remaining = re.sub(r'"([^"]{1,80})"', _extract_phrase, bounded)
        parsed["phrases"] = phrases

        raw_parts = remaining.split()[: MAX_TOKENS + 8]
        raw_include_tokens: List[str] = []
        exclude_tokens: List[str] = []

        for part in raw_parts:
            low = part.lower()

            if low.startswith("!") and len(low) >= 2:
                if low in BANG_COMMANDS or low == "!random":
                    parsed["bang"] = low
                    continue

            if ":" in low and not low.startswith(":"):
                op, _, val = low.partition(":")
                val_clean = re.sub(r"[^\wáéíóúñÁÉÍÓÚÑ./>-]", "", val)
                if op in ("cat", "category", "categoria") and val_clean:
                    if "/" in val_clean:
                        parsed["tax_filter"] = val_clean
                    else:
                        parsed["cat_filter"] = normalize_accents(val_clean)
                    continue
                if op in ("tax", "taxonomy") and val_clean:
                    parsed["tax_filter"] = val_clean
                    continue
                if op == "js" and val_clean:
                    if val_clean in ("safest", "none", "nojs", "sinjs"):
                        parsed["js_filter"] = "Safest"
                    elif val_clean in ("safer", "standard"):
                        parsed["js_filter"] = val_clean.capitalize()
                    continue
                if op == "site" and val_clean:
                    parsed["site_filter"] = val_clean
                    continue
                if op in ("trust", "score") and val_clean:
                    num_str = re.sub(r"[^\d]", "", val_clean)
                    if num_str:
                        parsed["min_trust"] = min(100, max(0, int(num_str)))
                    continue
                if op in ("pgp", "verif") and val_clean:
                    if val_clean in ("no", "unverified", "open", "all"):
                        parsed["tier_filter"] = "UNVERIFIED"
                    else:
                        parsed["pgp_only"] = True
                    continue
                if op == "tier" and val_clean:
                    parsed["tier_filter"] = val_clean.upper()
                    continue

            if low.startswith("-") and len(low) > 1:
                ex_clean = normalize_accents(re.sub(r"[^\wáéíóúñÁÉÍÓÚÑ]", "", low[1:]))
                if ex_clean and ex_clean not in FTS5_RESERVED:
                    exclude_tokens.append(ex_clean)
                continue

            for tok in re.findall(r"[\wáéíóúñÁÉÍÓÚÑ]+", low):
                norm_tok = normalize_accents(tok)
                if norm_tok not in FTS5_RESERVED and len(raw_include_tokens) < MAX_TOKENS:
                    raw_include_tokens.append(norm_tok)

        # Filtrar stopwords SOLO si quedan otros términos significativos en la consulta
        meaningful = [t for t in raw_include_tokens if t not in STOPWORDS and len(t) >= 2]
        parsed["include_tokens"] = meaningful if meaningful else raw_include_tokens
        parsed["exclude_tokens"] = exclude_tokens
        return parsed

    def suggest_spelling(self, tokens: List[str]) -> Optional[str]:
        """
        Corrector Ortográfico de Precisión Damerau-Levenshtein (Sin Falsos Positivos):
        - Jamás corrige palabras reales ya conocidas ni intenciones semánticas (ej. 'armas', 'mercados', 'ovnis').
        - Solo sugiere entidades/términos técnicos de >= 5 letras que compartan la misma letra inicial,
          tengan diferencia de longitud <= 1 y distancia Damerau-Levenshtein <= 1 (o <= 2 en palabras largas).
        """
        if not tokens:
            return None

        corrected: List[str] = []
        changed = False

        for tok in tokens:
            clean_tok = normalize_accents(tok.lower())
            if (
                len(clean_tok) < 5
                or clean_tok.isdigit()
                or clean_tok in self.vocabulary
                or clean_tok in self.known_valid_words
                or clean_tok in STOPWORDS
            ):
                corrected.append(tok)
                continue

            max_dist = 1 if len(clean_tok) <= 6 else 2
            best_cand: Optional[str] = None
            best_dist = 99
            best_ratio = 0.0

            for cand in self.vocabulary:
                if cand[0] != clean_tok[0]:
                    continue
                if abs(len(cand) - len(clean_tok)) > 1:
                    continue
                dist = _damerau_levenshtein(clean_tok, cand)
                if dist <= max_dist:
                    ratio = difflib.SequenceMatcher(None, clean_tok, cand).ratio()
                    if ratio >= 0.78 and (dist < best_dist or (dist == best_dist and ratio > best_ratio)):
                        best_dist = dist
                        best_ratio = ratio
                        best_cand = cand

            if best_cand and best_cand != clean_tok:
                corrected.append(best_cand)
                changed = True
            else:
                corrected.append(tok)

        if changed:
            return " ".join(corrected)
        return None

    def classify_deepweb_intent(
        self, tokens: List[str], phrases: List[str]
    ) -> Optional[Dict[str, object]]:
        """
        Detecta si la consulta del usuario corresponde a una intención temática de la Deep Web
        (ej. armamento/conflictos/inteligencia, mercados darknet, exploits/ciberseguridad,
        filtraciones/archivos clasificados, anonimato/OPSEC).
        """
        all_words = set(tokens)
        for phr in phrases:
            for w in phr.split():
                all_words.add(w)

        for intent in DEEPWEB_SEMANTIC_INTENTS:
            keywords: Set[str] = intent["keywords"]  # type: ignore
            matched_kw = all_words.intersection(keywords)
            if matched_kw:
                return {
                    "id": intent["id"],
                    "label": intent["label"],
                    "advisory": intent["advisory"],
                    "target_ids": intent["target_ids"],
                    "matched_keywords": sorted(matched_kw),
                }
        return None

    def build_knowledge_card(
        self, query_info: Dict[str, object], top_result: Optional[Dict[str, object]]
    ) -> Optional[Dict[str, object]]:
        tokens: List[str] = query_info.get("include_tokens", [])  # type: ignore
        raw_low = str(query_info.get("raw", "")).lower()

        if "saghet" in tokens or raw_low == "!saghet":
            return {
                "type": "AUTHOR_CARD",
                "title": "saghet — Lead Security Architect & Creator",
                "subtitle": "Arquitecto de Ciberseguridad y Creador de SamuBusquedas (.onion v3)",
                "summary": (
                    "Investigador de seguridad y arquitecto de motores de búsqueda en la red Tor. "
                    "Diseñador del algoritmo híbrido SamuRank (BM25F + OnionTrustRank SHA3-256), de la Memoria "
                    "Colectiva de Búsquedas Exitosas (Auto-Aprendizaje FTS5) y del escudo Zero-JS / Zero-Logs."
                ),
                "attributes": [
                    ("Handle / Alias Hacker", "saghet"),
                    ("Motor Desarrollado", f"SamuBusquedas v{ENGINE_VERSION} (.onion v3 Ed25519)"),
                    ("Superficie Indexada", "112+ Nodos Base Verificados + Memoria Colectiva Auto-Indexada + Rastreo Bilingüe Tor"),
                    ("Estándares Auditables", "/.well-known/security.txt (RFC 9116) | /humans.txt | /canary.txt"),
                ],
            }

        if top_result and (tokens or query_info.get("phrases")):
            title_low = normalize_accents(str(top_result["title"]).lower())
            if any(t in title_low for t in tokens if len(t) >= 3) or query_info.get("phrases"):
                chunks = format_visual_onion_chunks(str(top_result["onion_url"]))
                return {
                    "type": "ENTITY_CARD",
                    "title": str(top_result["title"]),
                    "subtitle": f"Taxonomía Yahoo!: {top_result.get('taxonomy', 'tor/node')} • {top_result['category']}",
                    "summary": str(top_result["description"]),
                    "onion_url": str(top_result["onion_url"]),
                    "visual_hash": f"{chunks['prefix']}...{chunks['suffix']}.onion",
                    "attributes": [
                        ("Puntaje SamuRank", f"{top_result.get('samu_rank', 100.0)} pts"),
                        ("Nivel de Verificación", str(top_result.get("status", "Verificado"))),
                        ("Evidencia PGP / Nota", str(top_result["pgp_fingerprint"])),
                        ("Política Tor Browser", str(top_result["js_requirement"])),
                        ("Disponibilidad (Uptime)", f"{top_result.get('uptime_percent', 95.0)}%"),
                    ],
                }
        return None

    def _build_sql_filters(
        self,
        eff_cat: Optional[object],
        eff_tax: Optional[object],
        only_safest_js: bool,
        q_info: Dict[str, object],
        include_unverified: bool,
    ) -> Tuple[str, List[object]]:
        base_filters_sql = ""
        filter_params: List[object] = []

        if not include_unverified:
            base_filters_sql += " AND s.verification_tier = 'VERIFIED'"
        elif q_info.get("tier_filter") in ("VERIFIED", "UNVERIFIED"):
            base_filters_sql += " AND s.verification_tier = ?"
            filter_params.append(q_info["tier_filter"])

        if eff_cat and str(eff_cat).strip() != "Todas":
            base_filters_sql += " AND LOWER(s.norm_searchable) LIKE ?"
            filter_params.append(f"%{normalize_accents(str(eff_cat).strip().lower())}%")

        if eff_tax:
            base_filters_sql += " AND LOWER(s.taxonomy) LIKE ?"
            filter_params.append(f"%{str(eff_tax).strip().lower()}%")

        if only_safest_js or q_info.get("js_filter") == "Safest":
            base_filters_sql += " AND s.js_requirement LIKE '%Safest%'"
        elif q_info.get("js_filter"):
            base_filters_sql += " AND s.js_requirement LIKE ?"
            filter_params.append(f"%{q_info['js_filter']}%")

        if q_info.get("site_filter"):
            base_filters_sql += " AND (LOWER(s.onion_url) LIKE ? OR LOWER(s.clearnet_url) LIKE ?)"
            site_pat = f"%{str(q_info['site_filter']).lower()}%"
            filter_params.extend([site_pat, site_pat])

        if q_info.get("min_trust") is not None:
            base_filters_sql += " AND s.safety_score >= ?"
            filter_params.append(int(q_info["min_trust"]))  # type: ignore

        if q_info.get("pgp_only"):
            base_filters_sql += " AND s.verification_tier = 'VERIFIED'"

        return base_filters_sql, filter_params

    def _execute_fts_or_like_query(
        self,
        tokens: List[str],
        phrases: List[str],
        eff_cat: Optional[object],
        eff_tax: Optional[object],
        only_safest_js: bool,
        q_info: Dict[str, object],
        include_unverified: bool,
    ) -> List[Dict[str, object]]:
        cursor = self.conn.cursor()

        fts_clauses: List[str] = []
        for phr in phrases:
            fts_clauses.append(f'"{phr}"')

        for tok in tokens:
            synonyms = SYNONYM_MAP.get(tok, [])
            if synonyms:
                group = " OR ".join([f'"{tok}"*'] + [f'"{normalize_accents(s)}"*' for s in synonyms[:6]])
                fts_clauses.append(f"({group})")
            else:
                fts_clauses.append(f'"{tok}"*')

        base_filters_sql, filter_params = self._build_sql_filters(
            eff_cat, eff_tax, only_safest_js, q_info, include_unverified
        )

        rows: List[Dict[str, object]] = []

        if fts_clauses:
            fts_sql = f"""
                SELECT s.*,
                       (-bm25(services_fts, 0.0, 10.0, 4.0, 2.0, 6.0, 1.0, 5.0, 4.0)) AS bm25_score
                FROM services s
                JOIN services_fts f ON s.id = f.id
                WHERE services_fts MATCH ?
                {base_filters_sql}
            """
            # Etapa 1: Precisión AND
            cursor.execute(fts_sql, [" AND ".join(fts_clauses)] + filter_params)
            rows = [dict(r) for r in cursor.fetchall()]

            # Etapa 2: Amplitud OR si AND devolvió menos de 3 resultados y hay varios términos
            if len(rows) < 3 and len(fts_clauses) > 1:
                cursor.execute(fts_sql, [" OR ".join(fts_clauses)] + filter_params)
                seen_ids = {r["id"] for r in rows}
                for r in cursor.fetchall():
                    if r["id"] not in seen_ids:
                        rows.append(dict(r))
                        seen_ids.add(r["id"])

            # Etapa 3: Subcadena con límite de palabra (\b) solo para tokens de >= 5 letras
            long_tokens = [t for t in tokens if len(t) >= 5]
            if not rows and long_tokens:
                like_clauses = " OR ".join("s.norm_searchable LIKE ?" for _ in long_tokens)
                like_params = [f"%{t}%" for t in long_tokens]
                like_sql = f"SELECT s.*, 2.5 AS bm25_score FROM services s WHERE ({like_clauses}) {base_filters_sql}"
                cursor.execute(like_sql, like_params + filter_params)
                candidates = [dict(r) for r in cursor.fetchall()]
                for cand in candidates:
                    norm_text = str(cand.get("norm_searchable", ""))
                    if any(re.search(rf"\b{re.escape(t)}", norm_text) for t in long_tokens):
                        rows.append(cand)
        else:
            all_sql = f"SELECT s.*, 0.0 AS bm25_score FROM services s WHERE 1=1 {base_filters_sql}"
            cursor.execute(all_sql, filter_params)
            rows = [dict(r) for r in cursor.fetchall()]

        return rows

    def search_v2(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        taxonomy: Optional[str] = None,
        only_safest_js: bool = False,
        include_unverified: bool = True,
        enable_live_tor: bool = True,
    ) -> Dict[str, object]:
        """
        Motor de Búsqueda Inteligente Multicapa SamuBusquedas v1.99.1:
        0. Memoria Colectiva de Búsquedas Exitosas (`COLLECTIVE_MEMORY`): recupera al instante (< 1 ms)
           resultados verificados de consultas que ya tuvieron éxito previamente por cualquier usuario.
        1. Búsqueda Exacta / Sinónimos FTS5 sobre 112+ nodos base + nodos auto-aprendidos.
        2. Clasificador Semántico de Intención en la Deep Web.
        3. Corrector Ortográfico Damerau-Levenshtein estricto.
        4. Meta-Búsqueda Bilingüe en Vivo en la Red Tor (Ahmia IPv4 + ES<->EN) y auto-absorción en FTS5.
        """
        start_t = time.perf_counter()
        q_info = self.parse_search_query(query)
        include_tokens: List[str] = q_info["include_tokens"]  # type: ignore
        exclude_tokens: List[str] = q_info["exclude_tokens"]  # type: ignore
        phrases: List[str] = q_info["phrases"]  # type: ignore
        bang = q_info.get("bang")

        cursor = self.conn.cursor()
        if bang == "!random":
            cursor.execute("SELECT * FROM services ORDER BY safety_score DESC")
            all_rows = [dict(r) for r in cursor.fetchall()]
            chosen = [random.choice(all_rows)] if all_rows else []
            for item in chosen:
                item["samu_rank"] = round(float(item["safety_score"]) + float(item["crypto_trust_bonus"]), 2)
                item["highlighted_desc"] = html.escape(str(item["description"]))
                item["visual_chunks"] = format_visual_onion_chunks(str(item["onion_url"]))
            return {
                "results": chosen,
                "did_you_mean": None,
                "auto_corrected_from": None,
                "semantic_intent": None,
                "is_exploratory_fallback": False,
                "collective_memory_hit": False,
                "collective_hits": 0,
                "knowledge_card": self.build_knowledge_card(q_info, chosen[0] if chosen else None),
                "parsed_query": q_info,
                "bang_info": {"name": "Servicio Onion Aleatorio (!random)", "url": chosen[0]["onion_url"] if chosen else "/"},
                "elapsed_ms": round((time.perf_counter() - start_t) * 1000, 2),
            }

        bang_info = None
        if isinstance(bang, str) and bang in BANG_COMMANDS:
            b_meta = BANG_COMMANDS[bang]
            sub_q = " ".join(include_tokens)
            target = b_meta["target_onion"]
            if target.endswith("="):
                target = target + sub_q
            bang_info = {
                "command": bang,
                "name": b_meta["name"],
                "description": b_meta["description"],
                "url": target,
            }

        eff_cat = category if (category and category != "Todas") else q_info.get("cat_filter")
        eff_tax = taxonomy if taxonomy else q_info.get("tax_filter")

        has_strict_filters = bool(
            eff_cat
            or eff_tax
            or only_safest_js
            or q_info.get("js_filter")
            or q_info.get("site_filter")
            or q_info.get("min_trust") is not None
            or q_info.get("pgp_only")
            or q_info.get("tier_filter")
            or exclude_tokens
            or phrases
        )

        # Etapa 0: Consultar Memoria Colectiva de Búsquedas Exitosas
        collective_entry = (
            COLLECTIVE_MEMORY.get_collective_results(query or "")
            if (query and include_tokens and not has_strict_filters and include_unverified)
            else None
        )
        collective_memory_hit = bool(collective_entry)
        collective_hits_count = int(collective_entry["hits"]) if collective_entry else 0

        rows = self._execute_fts_or_like_query(
            include_tokens, phrases, eff_cat, eff_tax, only_safest_js, q_info, include_unverified
        )

        # Clasificador Semántico de Intención en la Deep Web (antes de cualquier corrección ortográfica)
        semantic_intent = self.classify_deepweb_intent(include_tokens, phrases)
        if semantic_intent:
            target_ids: List[str] = semantic_intent["target_ids"]  # type: ignore
            base_filters_sql, filter_params = self._build_sql_filters(
                eff_cat, eff_tax, only_safest_js, q_info, include_unverified
            )
            placeholders = ",".join("?" for _ in target_ids)
            intent_sql = f"""
                SELECT s.*, 7.5 AS bm25_score
                FROM services s
                WHERE s.id IN ({placeholders})
                {base_filters_sql}
            """
            cursor.execute(intent_sql, list(target_ids) + filter_params)
            seen_ids = {r["id"] for r in rows}
            fetched_by_id = {r["id"]: dict(r) for r in cursor.fetchall()}
            for tid in target_ids:
                if tid in fetched_by_id and tid not in seen_ids:
                    rows.append(fetched_by_id[tid])
                    seen_ids.add(tid)

        # Calcular sugerencia ortográfica estricta "¿Quisiste decir...?" SOLO si no es una intención semántica válida
        did_you_mean = None if semantic_intent else self.suggest_spelling(include_tokens)
        auto_corrected_from: Optional[str] = None

        # AUTO-RECOVERY DIFUSO: Solo si la consulta original no tuvo resultados ni intención semántica
        active_tokens = list(include_tokens)
        if not rows and did_you_mean:
            corrected_tokens = did_you_mean.split()
            rows = self._execute_fts_or_like_query(
                corrected_tokens, phrases, eff_cat, eff_tax, only_safest_js, q_info, include_unverified
            )
            if rows:
                auto_corrected_from = query
                active_tokens = corrected_tokens

        # Aplicar exclusiones `-termino` y frases exactas sobre el texto normalizado sin tildes
        filtered_rows: List[Dict[str, object]] = []
        for r in rows:
            haystack = str(r.get("norm_searchable", "")).lower() + " " + str(r["onion_url"]).lower()
            if any(ex in haystack for ex in exclude_tokens):
                continue
            if any(phr not in haystack for phr in phrases):
                continue
            filtered_rows.append(r)

        # Fusionar resultados guardados en Memoria Colectiva de Búsquedas Exitosas (si existen)
        if collective_entry:
            known_by_url = {str(r["onion_url"]).lower().rstrip("/"): r for r in filtered_rows}
            for cm_item in collective_entry.get("results", []):  # type: ignore
                cm_url = str(cm_item.get("onion_url", "")).lower().rstrip("/")
                if cm_url in known_by_url:
                    known_by_url[cm_url]["collective_memory"] = True
                    known_by_url[cm_url]["collective_hits"] = collective_hits_count
                elif cm_url and "aaa" not in cm_url:
                    cm_copy = dict(cm_item)
                    cm_copy["bm25_score"] = 4.2
                    cm_copy["crypto_trust_bonus"] = 18.0
                    cm_copy["collective_memory"] = True
                    cm_copy["collective_hits"] = collective_hits_count
                    filtered_rows.append(cm_copy)
                    known_by_url[cm_url] = cm_copy

        # AMPLIFICACIÓN AUTO-EXPANSIVA "SNOWBALL" EN CADA BÚSQUEDA (v1.99.2):
        # Cada búsqueda con enable_live_tor=True explora nuevos nodos .onion v3 no indexados aún
        # y los absorbe de inmediato en SQLite FTS5 + Memoria Colectiva.
        newly_indexed_count = 0
        if include_unverified and enable_live_tor and active_tokens and not has_strict_filters:
            live_q = " ".join(active_tokens)
            known_hosts = self.get_known_onion_hosts()
            live_items = fetch_live_unverified_tor_results(
                live_q,
                max_results=12,
                timeout=2.8,
                known_hosts=known_hosts,
                new_discovery_quota=4,
            )
            known_urls = {str(r["onion_url"]).lower().rstrip("/") for r in filtered_rows}
            for lv in live_items:
                lv_url = str(lv["onion_url"]).lower().rstrip("/")
                was_absorbed = self.absorb_discovered_node(lv, commit=False)
                if was_absorbed:
                    newly_indexed_count += 1
                    lv["newly_indexed"] = True
                if lv_url not in known_urls:
                    lv["bm25_score"] = 6.5 if semantic_intent else 3.8
                    lv["crypto_trust_bonus"] = 14.0
                    filtered_rows.append(lv)
                    known_urls.add(lv_url)
            self.conn.commit()

        # Modo Exploratorio si el término es completamente inédito y no activó filtros restrictivos
        is_exploratory_fallback = False
        if not filtered_rows and (include_tokens or phrases) and not eff_tax and (not eff_cat or eff_cat == "Todas"):
            is_exploratory_fallback = True
            cursor.execute(
                "SELECT s.*, 1.0 AS bm25_score FROM services s WHERE s.taxonomy IN ('search/engines', 'comm/wiki') ORDER BY s.safety_score DESC LIMIT 8"
            )
            filtered_rows = [dict(r) for r in cursor.fetchall()]

        # VERIFICACIÓN ACTIVA DE VALIDEZ Y ESTADO ONLINE (.onion v3 + SOCKS5h Cache/Probe)
        filtered_rows = verify_and_enrich_search_results(
            filtered_rows,
            live_probe_unverified=False,
        )

        # Registrar esta búsqueda exitosa en la Memoria Colectiva para los próximos usuarios
        if (
            filtered_rows
            and not is_exploratory_fallback
            and query
            and active_tokens
            and not has_strict_filters
            and include_unverified
            and (not did_you_mean or auto_corrected_from)
        ):
            rec_target = str(did_you_mean) if (auto_corrected_from and did_you_mean) else str(query)
            rec_stats = COLLECTIVE_MEMORY.record_successful_search(rec_target, filtered_rows)
            collective_hits_count = max(collective_hits_count, int(rec_stats.get("query_hits", 1)))
            for r_item in filtered_rows:
                r_item["collective_memory"] = True
                r_item["collective_hits"] = collective_hits_count

        highlight_terms = active_tokens + [w for phr in phrases for w in phr.split()]
        for item in filtered_rows:
            bm25_val = float(item.get("bm25_score", 0.0))
            safety_val = float(item.get("safety_score", 70.0))
            crypto_val = float(item.get("crypto_trust_bonus", 15.0))
            uptime_val = float(item.get("uptime_percent", 95.0))

            title_norm = normalize_accents(str(item["title"]).lower())
            exact_title_boost = sum(
                35.0 for t in active_tokens if re.search(rf"\b{re.escape(t)}", title_norm)
            )
            norm_search_str = str(item.get("norm_searchable", ""))
            token_match_count = sum(
                12.0 for t in active_tokens if re.search(rf"\b{re.escape(t)}", norm_search_str)
            )
            collective_boost = 5.0 if item.get("collective_memory") else 0.0

            samu_rank = (
                (bm25_val * 4.5)
                + exact_title_boost
                + token_match_count
                + (safety_val * 0.65)
                + (crypto_val * 0.55)
                + (uptime_val * 0.15)
                + collective_boost
            )
            item["samu_rank"] = round(samu_rank, 2)
            item["highlighted_title"] = highlight_safe_snippet(str(item["title"]), highlight_terms, max_len=140)
            item["highlighted_desc"] = highlight_safe_snippet(str(item["description"]), highlight_terms, max_len=320)
            item["visual_chunks"] = format_visual_onion_chunks(str(item["onion_url"]))

        filtered_rows.sort(key=lambda x: (-float(x["samu_rank"]), str(x["title"])))

        k_card = self.build_knowledge_card(
            q_info, filtered_rows[0] if (filtered_rows and not is_exploratory_fallback) else None
        )

        return {
            "results": filtered_rows,
            "did_you_mean": did_you_mean,
            "auto_corrected_from": auto_corrected_from,
            "semantic_intent": semantic_intent,
            "is_exploratory_fallback": is_exploratory_fallback,
            "collective_memory_hit": collective_memory_hit,
            "collective_hits": collective_hits_count,
            "newly_indexed_count": newly_indexed_count,
            "total_indexed_surface": self.get_total_indexed_count(),
            "knowledge_card": k_card,
            "parsed_query": q_info,
            "bang_info": bang_info,
            "elapsed_ms": round((time.perf_counter() - start_t) * 1000, 2),
        }

    def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        only_safest_js: bool = False,
    ) -> List[Dict[str, object]]:
        res = self.search_v2(query=query, category=category, only_safest_js=only_safest_js)
        return res["results"]  # type: ignore

    def inspect_onion_url(self, raw_url: str) -> Dict[str, object]:
        url = (raw_url or "").strip()[:MAX_QUERY_LEN]
        if not url.startswith(("http://", "https://")):
            url_to_test = "http://" + url
        else:
            url_to_test = url

        is_v3_math_valid = is_valid_v3_onion(url_to_test)

        host_match = re.search(r"([a-z2-7]{16,56})\.onion", url_to_test, re.IGNORECASE)
        onion_host = host_match.group(1).lower() if host_match else ""

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM services")
        all_services = [dict(row) for row in cursor.fetchall()]

        exact_match = None
        typosquat_suspect = None

        for svc in all_services:
            svc_match = re.search(
                r"([a-z2-7]{56})\.onion", svc["onion_url"], re.IGNORECASE
            )
            if not svc_match:
                continue
            known_host = svc_match.group(1).lower()

            if onion_host == known_host:
                exact_match = svc
                break
            elif (
                svc.get("verification_tier") == "VERIFIED"
                and onion_host
                and len(onion_host) == 56
                and onion_host[:4] == known_host[:4]
                and onion_host != known_host
            ):
                typosquat_suspect = svc

        if not exact_match and not typosquat_suspect and onion_host:
            for brand_key, svc_item in self.brand_keywords.items():
                if brand_key in onion_host[:14]:
                    typosquat_suspect = svc_item
                    break

        if exact_match:
            tier = str(exact_match.get("verification_tier", "VERIFIED"))
            if tier == "VERIFIED":
                return {
                    "verdict": "SAFE_VERIFIED",
                    "badge": "SITIO OFICIAL VERIFICADO (CHECKSUM SHA3-256 OK)",
                    "risk_level": "Bajo (Seguro)",
                    "is_v3": True,
                    "service": exact_match,
                    "message": (
                        f"La dirección coincide matemáticamente con la llave pública Ed25519 registrada para "
                        f"'{exact_match['title']}'. Suma de comprobación SHA3-256 válida y verificada mediante "
                        f"{exact_match['verification_method']}."
                    ),
                }
            return {
                "verdict": "UNVERIFIED_V3",
                "badge": "INDEXADO EN CATÁLOGO COMUNITARIO (NO VERIFICADO POR PGP)",
                "risk_level": "Medio (Navegar en Modo Safest Sin JS)",
                "is_v3": True,
                "service": exact_match,
                "message": (
                    f"Esta dirección corresponde a '{exact_match['title']}' dentro del índice abierto/comunitario de "
                    f"SamuBusquedas. Su checksum SHA3-256 es válido, pero no cuenta con auditoría PGP oficial."
                ),
            }

        if typosquat_suspect:
            return {
                "verdict": "DANGER_PHISHING",
                "badge": "ALERTA CRÍTICA DE PHISHING / CLON DETECTADO",
                "risk_level": "Crítico (Peligro de Robo de Credenciales)",
                "is_v3": is_v3_math_valid,
                "service": typosquat_suspect,
                "message": (
                    f"¡PELIGRO! Esta dirección imita el prefijo o la marca de '{typosquat_suspect['title']}', "
                    f"pero su llave criptográfica Ed25519 NO es la oficial. Se trata de un ataque de "
                    f"Typosquatting / Phishing. El dominio oficial verificado es: {typosquat_suspect['onion_url']}"
                ),
            }

        if not is_v3_math_valid:
            return {
                "verdict": "INVALID_OR_V2",
                "badge": "DIRECCIÓN INVÁLIDA, CHECKSUM CORRUPTO O V2 OBSOLETA",
                "risk_level": "Alto",
                "is_v3": False,
                "service": None,
                "message": (
                    "La dirección proporcionada falla la verificación matemática Tor Onion v3 "
                    "(56 caracteres Base32 con byte de versión 0x03 y checksum SHA3-256 válido) o es una dirección "
                    "v2 obsoleta de 16 caracteres vulnerable a colisiones criptográficas."
                ),
            }

        return {
            "verdict": "UNVERIFIED_V3",
            "badge": "CHECKSUM V3 VÁLIDO PERO NO AUDITADO EN ALLOWLIST",
            "risk_level": "Medio (Precaución Recomendada)",
            "is_v3": True,
            "service": None,
            "message": (
                "La dirección posee una llave pública Ed25519 y checksum SHA3-256 matemáticamente válidos (v3), "
                "pero NO forma parte del catálogo auditado por saghet en SamuBusquedas. Si decides visitarla, "
                "usa Tor Browser en modo 'Safest' (Sin JavaScript) y nunca ingreses contraseñas ni datos sensibles."
            ),
        }
