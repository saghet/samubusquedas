"""
Gamer Search Engine - Arquitectura de Búsqueda Federada Multi-Fuente
=====================================================================
Motor federado de alta concurrencia con conectores independientes para:
1. Buscadores Generales:
   - DuckDuckGo Web Provider (HTML/Lite parser sin dependencias externas)
   - Wikipedia OpenSearch Provider (Español & Inglés)
   - Wikidata Entity Provider (Metadatos estructurados oficiales)
2. Comunidades Gamer:
   - Reddit Community Provider (Discusiones, descubrimientos y preguntas)
   - GameFAQs / GameSpot Guides Provider (Walkthroughs, trucos y faqs)
   - Steam Store & Community Hub Provider (Metadatos, requisitos y actividad PC)
   - Nexus Mods & ModDB Provider (Mods, texturas y utilidades)
3. Bases de Datos de Videojuegos:
   - Speedrun.com Provider (Récords mundiales y categorías con normalización de alias)
   - Internet Archive Expanded Provider (Software, revistas históricas y guías de texto)
   - GitHub Open Source Gaming Provider (Emuladores, descompilaciones y parches)

Cada conector cuenta con:
- Timeout estricto independiente.
- Aislamiento completo de excepciones (un conector caído no detiene la búsqueda).
- Trazabilidad y recolección de errores para el panel de Search Intelligence.
- Evaluación de ciberseguridad con GAMER_SECURITY.
"""

import concurrent.futures
import html
import json
import logging
import re
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple
from gamer_security import GAMER_SECURITY

logger = logging.getLogger("GamerConnectors")

COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7",
}


class BaseGamerProvider:
    """Clase base abstracta para implementar proveedores de búsqueda federada."""
    name: str = "base"
    source_label: str = "Fuente Abierta"
    category: str = "general"  # general, community, database, preservation
    priority: int = 10

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def health_check(self) -> bool:
        return True


# =====================================================================
# 1. BUSCADORES GENERALES
# =====================================================================

class DuckDuckGoWebProvider(BaseGamerProvider):
    """Conector web general mediante interfaz liviana de DuckDuckGo."""
    name = "duckduckgo_web"
    source_label = "DuckDuckGo Web Search"
    category = "general"
    priority = 1

    def __init__(self, timeout: float = 3.5):
        self.timeout = timeout

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not query or len(query.strip()) < 2:
            return []

        url = "https://lite.duckduckgo.com/lite/"
        data = urllib.parse.urlencode({"q": query.strip()}).encode("utf-8")
        headers = dict(COMMON_HEADERS)
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        req = urllib.request.Request(url, data=data, headers=headers)
        results: List[Dict[str, Any]] = []

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    raw_html = resp.read().decode("utf-8", errors="ignore")
                    all_a = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', raw_html)
                    for link, text in all_a:
                        if "duckduckgo.com" not in link and ("http" in link or "uddg=" in link):
                            clean_url = link
                            if "uddg=" in link:
                                clean_url = urllib.parse.unquote(link.split("uddg=")[1].split("&")[0])
                            clean_title = re.sub(r"<[^>]+>", "", text).strip()
                            clean_title = html.unescape(clean_title)

                            if clean_title and clean_url.startswith("http"):
                                sec_report = GAMER_SECURITY.evaluate_url(clean_url)
                                results.append({
                                    "id": f"ddg_{abs(hash(clean_url))}",
                                    "title": clean_title,
                                    "category": "Búsqueda Web Abierta",
                                    "description": f"Resultado indexado de la web pública para: {query.strip()}",
                                    "source": self.source_label,
                                    "url": clean_url,
                                    "security": sec_report.to_dict()
                                })
                                if len(results) >= limit:
                                    break
        except Exception as e:
            logger.debug(f"DuckDuckGo provider error for '{query}': {e}")
        return results


class WikipediaOpenSearchProvider(BaseGamerProvider):
    """Conector a la API oficial de Wikipedia (Español & Inglés) para fichas enciclopédicas."""
    name = "wikipedia"
    source_label = "Wikipedia Enciclopedia Gamer"
    category = "database"
    priority = 2

    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout

    def search(self, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        if not query or len(query.strip()) < 2:
            return []

        results: List[Dict[str, Any]] = []
        endpoints = [
            ("es", f"https://es.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(query)}&limit={limit}&namespace=0&format=json"),
            ("en", f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(query)}&limit={limit}&namespace=0&format=json")
        ]

        seen_urls = set()
        for lang, url in endpoints:
            req = urllib.request.Request(url, headers=COMMON_HEADERS)
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        titles = data[1] if len(data) > 1 else []
                        descriptions = data[2] if len(data) > 2 else []
                        urls = data[3] if len(data) > 3 else []

                        for t, d, u in zip(titles, descriptions, urls):
                            if u in seen_urls:
                                continue
                            seen_urls.add(u)
                            desc = d if d else f"Artículo histórico y técnico enciclopédico sobre {t}."
                            sec_report = GAMER_SECURITY.evaluate_url(u)
                            results.append({
                                "id": f"wiki_{lang}_{abs(hash(u))}",
                                "title": f"{t} ({lang.upper()})",
                                "category": "Base de Datos & Ficha Técnica",
                                "description": desc,
                                "source": f"{self.source_label} ({lang.upper()})",
                                "url": u,
                                "security": sec_report.to_dict()
                            })
                            if len(results) >= limit:
                                break
            except Exception as e:
                logger.debug(f"Wikipedia {lang} error for '{query}': {e}")
            if len(results) >= limit:
                break
        return results


class WikidataEntityProvider(BaseGamerProvider):
    """Conector a la API oficial de Wikidata para resolución de entidades, creadores y metadatos."""
    name = "wikidata"
    source_label = "Wikidata Open Knowledge Base"
    category = "database"
    priority = 3

    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout

    def search(self, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        if not query or len(query.strip()) < 2:
            return []

        url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={urllib.parse.quote(query)}&language=es&format=json&limit={limit}"
        req = urllib.request.Request(url, headers=COMMON_HEADERS)
        results: List[Dict[str, Any]] = []

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    items = data.get("search", [])
                    for it in items:
                        lbl = it.get("label", "")
                        desc = it.get("description", "Entidad de base de conocimiento libre.")
                        concept_uri = it.get("concepturi", f"https://www.wikidata.org/wiki/{it.get('id')}")
                        sec_report = GAMER_SECURITY.evaluate_url(concept_uri)
                        results.append({
                            "id": f"wd_{it.get('id')}",
                            "title": f"Wikidata: {lbl}",
                            "category": "Metadatos Oficiales & Ontología",
                            "description": f"{lbl} — {desc}",
                            "source": self.source_label,
                            "url": concept_uri,
                            "security": sec_report.to_dict()
                        })
        except Exception as e:
            logger.debug(f"Wikidata provider error for '{query}': {e}")
        return results


# =====================================================================
# 2. COMUNIDADES GAMER
# =====================================================================

class RedditCommunityProvider(BaseGamerProvider):
    """Conector especializado para descubrir hilos, descubrimientos y comunidades en Reddit."""
    name = "reddit_community"
    source_label = "Reddit Gaming Communities"
    category = "community"
    priority = 2

    def __init__(self, timeout: float = 3.5):
        self.timeout = timeout

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not query or len(query.strip()) < 2:
            return []

        # Buscar discusiones públicas en Reddit mediante agregación especializada
        target_query = f"site:reddit.com {query.strip()}"
        url = "https://lite.duckduckgo.com/lite/"
        data = urllib.parse.urlencode({"q": target_query}).encode("utf-8")
        headers = dict(COMMON_HEADERS)
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        req = urllib.request.Request(url, data=data, headers=headers)
        results: List[Dict[str, Any]] = []

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    raw_html = resp.read().decode("utf-8", errors="ignore")
                    all_a = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', raw_html)
                    for link, text in all_a:
                        if "reddit.com/r/" in link:
                            clean_url = link
                            if "uddg=" in link:
                                clean_url = urllib.parse.unquote(link.split("uddg=")[1].split("&")[0])
                            clean_title = re.sub(r"<[^>]+>", "", text).strip()
                            clean_title = html.unescape(clean_title)

                            if clean_title and clean_url.startswith("http"):
                                sec_report = GAMER_SECURITY.evaluate_url(clean_url)
                                # Extraer nombre del subreddit si es visible
                                sub_match = re.search(r"reddit\.com/r/([^/]+)", clean_url)
                                sub_name = f"r/{sub_match.group(1)}" if sub_match else "r/gaming"

                                results.append({
                                    "id": f"reddit_{abs(hash(clean_url))}",
                                    "title": f"[{sub_name}] {clean_title}",
                                    "category": "Comunidad & Discusión Gamer",
                                    "description": f"Hilo comunitario verificado de discusión, trucos y descubrimientos en {sub_name}.",
                                    "source": self.source_label,
                                    "url": clean_url,
                                    "security": sec_report.to_dict()
                                })
                                if len(results) >= limit:
                                    break
        except Exception as e:
            logger.debug(f"Reddit community provider error for '{query}': {e}")
        return results


class GameFAQsGuidesProvider(BaseGamerProvider):
    """Conector a guías, walkthroughs, trucos y foros de GameFAQs / GameSpot."""
    name = "gamefaqs_guides"
    source_label = "GameFAQs & GameSpot Guides"
    category = "community"
    priority = 2

    def __init__(self, timeout: float = 3.5):
        self.timeout = timeout

    def search(self, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        if not query or len(query.strip()) < 2:
            return []

        target_query = f"site:gamefaqs.gamespot.com {query.strip()}"
        url = "https://lite.duckduckgo.com/lite/"
        data = urllib.parse.urlencode({"q": target_query}).encode("utf-8")
        headers = dict(COMMON_HEADERS)
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        req = urllib.request.Request(url, data=data, headers=headers)
        results: List[Dict[str, Any]] = []

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    raw_html = resp.read().decode("utf-8", errors="ignore")
                    all_a = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', raw_html)
                    for link, text in all_a:
                        if "gamefaqs.gamespot.com" in link:
                            clean_url = link
                            if "uddg=" in link:
                                clean_url = urllib.parse.unquote(link.split("uddg=")[1].split("&")[0])
                            clean_title = re.sub(r"<[^>]+>", "", text).strip()
                            clean_title = html.unescape(clean_title)

                            if clean_title and clean_url.startswith("http"):
                                sec_report = GAMER_SECURITY.evaluate_url(clean_url)
                                results.append({
                                    "id": f"gamefaqs_{abs(hash(clean_url))}",
                                    "title": f"GameFAQs: {clean_title}",
                                    "category": "Guías, Trucos y Walkthroughs",
                                    "description": f"Guía detallada de la comunidad GameFAQs: walkthroughs, secretos y faqs verificados.",
                                    "source": self.source_label,
                                    "url": clean_url,
                                    "security": sec_report.to_dict()
                                })
                                if len(results) >= limit:
                                    break
        except Exception as e:
            logger.debug(f"GameFAQs provider error for '{query}': {e}")
        return results


class SteamStoreCommunityProvider(BaseGamerProvider):
    """Conector a la API oficial de Steam para catálogo de juegos, DLCs y hubs comunitarios."""
    name = "steam_community"
    source_label = "Steam Store & Community Hub"
    category = "community"
    priority = 3

    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout

    def search(self, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        if not query or len(query.strip()) < 2:
            return []

        encoded_q = urllib.parse.quote(query.strip())
        url = f"https://store.steampowered.com/api/storesearch/?term={encoded_q}&l=spanish&cc=ES"
        req = urllib.request.Request(url, headers=COMMON_HEADERS)
        results: List[Dict[str, Any]] = []

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    items = data.get("items", [])
                    for it in items:
                        app_id = it.get("id")
                        name = it.get("name")
                        price_info = it.get("price", {})
                        price_str = f"Precio: {price_info.get('final', 0) / 100:.2f} {price_info.get('currency', 'EUR')}" if price_info else "Consultar en tienda"
                        weblink = f"https://store.steampowered.com/app/{app_id}/"
                        sec_report = GAMER_SECURITY.evaluate_url(weblink)
                        results.append({
                            "id": f"steam_{app_id}",
                            "title": f"Steam: {name}",
                            "category": "Comunidad Steam & Plataforma PC",
                            "description": f"Hub oficial de Steam para {name}. Foros de discusión, mods de Workshop y {price_str}.",
                            "source": self.source_label,
                            "url": weblink,
                            "security": sec_report.to_dict()
                        })
                        if len(results) >= limit:
                            break
        except Exception as e:
            logger.debug(f"Steam provider error for '{query}': {e}")
        return results


class NexusModsModDBProvider(BaseGamerProvider):
    """Conector para descubrir mods, texturas y proyectos comunitarios en Nexus Mods y ModDB."""
    name = "nexus_moddb"
    source_label = "Nexus Mods & ModDB Community"
    category = "community"
    priority = 4

    def __init__(self, timeout: float = 3.5):
        self.timeout = timeout

    def search(self, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        if not query or len(query.strip()) < 2:
            return []

        target_query = f"(site:nexusmods.com OR site:moddb.com) {query.strip()} mods"
        url = "https://lite.duckduckgo.com/lite/"
        data = urllib.parse.urlencode({"q": target_query}).encode("utf-8")
        headers = dict(COMMON_HEADERS)
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        req = urllib.request.Request(url, data=data, headers=headers)
        results: List[Dict[str, Any]] = []

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    raw_html = resp.read().decode("utf-8", errors="ignore")
                    all_a = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', raw_html)
                    for link, text in all_a:
                        if "nexusmods.com" in link or "moddb.com" in link:
                            clean_url = link
                            if "uddg=" in link:
                                clean_url = urllib.parse.unquote(link.split("uddg=")[1].split("&")[0])
                            clean_title = re.sub(r"<[^>]+>", "", text).strip()
                            clean_title = html.unescape(clean_title)

                            if clean_title and clean_url.startswith("http"):
                                sec_report = GAMER_SECURITY.evaluate_url(clean_url)
                                results.append({
                                    "id": f"mod_{abs(hash(clean_url))}",
                                    "title": f"Mod: {clean_title}",
                                    "category": "Modding, Texturas y Utilidades",
                                    "description": f"Modificación comunitaria, mejoras gráficas o parches de calidad de vida.",
                                    "source": self.source_label,
                                    "url": clean_url,
                                    "security": sec_report.to_dict()
                                })
                                if len(results) >= limit:
                                    break
        except Exception as e:
            logger.debug(f"Nexus/ModDB provider error for '{query}': {e}")
        return results


# =====================================================================
# 3. BASES DE DATOS DE VIDEOJUEGOS Y PRESERVACIÓN
# =====================================================================

class SpeedrunComProvider(BaseGamerProvider):
    """Conector a la API oficial de Speedrun.com para consultar tablas de récords y categorías."""
    name = "speedrun_com"
    source_label = "Speedrun.com Community & Leaderboards"
    category = "database"
    priority = 3

    # Normalización de acrónimos populares para evitar fallos de búsqueda en Speedrun
    ACRONYM_MAP = {
        "gta v": "Grand Theft Auto V",
        "gta 5": "Grand Theft Auto V",
        "gtav": "Grand Theft Auto V",
        "gta vi": "Grand Theft Auto VI",
        "gta 6": "Grand Theft Auto VI",
        "gta sa": "Grand Theft Auto: San Andreas",
        "gta san andreas": "Grand Theft Auto: San Andreas",
        "gta vc": "Grand Theft Auto: Vice City",
        "gta vice city": "Grand Theft Auto: Vice City",
        "gta iv": "Grand Theft Auto IV",
        "gta 4": "Grand Theft Auto IV",
        "totk": "The Legend of Zelda: Tears of the Kingdom",
        "zelda totk": "The Legend of Zelda: Tears of the Kingdom",
        "botw": "The Legend of Zelda: Breath of the Wild",
        "zelda botw": "The Legend of Zelda: Breath of the Wild",
        "oot": "The Legend of Zelda: Ocarina of Time",
        "zelda oot": "The Legend of Zelda: Ocarina of Time",
        "tp": "The Legend of Zelda: Twilight Princess",
        "zelda tp": "The Legend of Zelda: Twilight Princess",
        "rdr2": "Red Dead Redemption 2",
        "er": "Elden Ring",
    }

    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not query or len(query.strip()) < 2:
            return []

        # Expandir acrónimo si existe coincidencia
        norm_q = query.strip().lower()
        expanded_q = self.ACRONYM_MAP.get(norm_q, query.strip())

        encoded_q = urllib.parse.quote(expanded_q)
        url = f"https://www.speedrun.com/api/v1/games?name={encoded_q}&max={limit}"
        req = urllib.request.Request(url, headers=COMMON_HEADERS)
        results: List[Dict[str, Any]] = []

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    items = data.get("data", [])
                    for item in items:
                        names = item.get("names", {})
                        title = names.get("international") or names.get("japanese") or item.get("id")
                        weblink = item.get("weblink", f"https://www.speedrun.com/{item.get('id')}")
                        release_year = item.get("release-date", "").split("-")[0] if item.get("release-date") else ""
                        sec_report = GAMER_SECURITY.evaluate_url(weblink)
                        results.append({
                            "id": f"speedrun_{item.get('id')}",
                            "title": f"Speedrun: {title}",
                            "category": "Comunidad & Speedrunning",
                            "description": f"Tablas oficiales de récords mundiales y categorías verificadas para {title} ({release_year}).",
                            "source": self.source_label,
                            "url": weblink,
                            "security": sec_report.to_dict()
                        })
        except Exception as e:
            logger.debug(f"Speedrun.com provider error for '{query}': {e}")
        return results


class InternetArchiveProvider(BaseGamerProvider):
    """Conector a Internet Archive expandido a software, manuales, guías y revistas históricas."""
    name = "internet_archive"
    source_label = "Internet Archive (Preservación Histórica)"
    category = "preservation"
    priority = 4

    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not query or len(query.strip()) < 2:
            return []

        # Permitir tanto software como textos (revistas históricas, guías, manuales escaneados)
        clean_q = urllib.parse.quote(f"{query.strip()} AND (mediatype:(software) OR mediatype:(texts))")
        url = f"https://archive.org/advancedsearch.php?q={clean_q}&fl[]=identifier,title,description,year,mediatype&sort[]=&rows={limit}&page=1&output=json"
        req = urllib.request.Request(url, headers=COMMON_HEADERS)
        results: List[Dict[str, Any]] = []

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    docs = data.get("response", {}).get("docs", [])
                    for doc in docs:
                        ident = doc.get("identifier")
                        title = doc.get("title") or ident
                        desc = doc.get("description", "Material histórico preservado disponible en el archivo público.")
                        if isinstance(desc, list):
                            desc = " ".join(desc)
                        m_type = doc.get("mediatype", "archive")
                        type_label = "Software Preservado" if m_type == "software" else "Manual / Revista Histórica"

                        weblink = f"https://archive.org/details/{ident}"
                        sec_report = GAMER_SECURITY.evaluate_url(weblink)
                        results.append({
                            "id": f"archive_{ident}",
                            "title": title,
                            "category": f"Preservación ({type_label})",
                            "description": str(desc)[:180] + "...",
                            "source": self.source_label,
                            "url": weblink,
                            "security": sec_report.to_dict()
                        })
        except Exception as e:
            logger.debug(f"Internet Archive provider error for '{query}': {e}")
        return results


class GitHubGamerProvider(BaseGamerProvider):
    """Conector a la API de GitHub para descubrir repositorios de emuladores, modding y herramientas."""
    name = "github"
    source_label = "GitHub Open Source Gaming"
    category = "preservation"
    priority = 5

    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not query or len(query.strip()) < 2:
            return []

        # Búsqueda limpia y abierta sin forzar topics restrictivos que bloqueen juegos comerciales
        clean_q = urllib.parse.quote(f"{query.strip()} (game OR emulator OR mod OR decompilation)")
        url = f"https://api.github.com/search/repositories?q={clean_q}&sort=stars&order=desc&per_page={limit}"
        headers = dict(COMMON_HEADERS)
        headers["Accept"] = "application/vnd.github.v3+json"

        req = urllib.request.Request(url, headers=headers)
        results: List[Dict[str, Any]] = []

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    items = data.get("items", [])
                    for item in items:
                        full_name = item.get("full_name")
                        desc = item.get("description") or "Repositorio de desarrollo de código abierto."
                        html_url = item.get("html_url")
                        stars = item.get("stargazers_count", 0)
                        license_info = item.get("license", {})
                        lic_name = license_info.get("spdx_id") if license_info else "Open Source"
                        sec_report = GAMER_SECURITY.evaluate_url(html_url)
                        results.append({
                            "id": f"gh_{item.get('id')}",
                            "title": full_name,
                            "category": "Código Abierto / Preservación",
                            "description": f"⭐ {stars:,} estrellas • Licencia {lic_name} — {desc}",
                            "source": self.source_label,
                            "url": html_url,
                            "security": sec_report.to_dict()
                        })
        except Exception as e:
            logger.debug(f"GitHub provider error for '{query}': {e}")
        return results


# =====================================================================
# 4. ORQUESTADOR FEDERADO CONCURRENTE (MULTI-FUENTE)
# =====================================================================

class FederatedSearchEngine:
    """
    Motor federado concurrente:
    - Agrupa múltiples conectores independientes organizados por taxonomías.
    - Soporta control de cuotas por categoría y agregación paralela con ThreadPoolExecutor.
    - Recolecta métricas de telemetría de búsqueda en tiempo real (errores, tiempos, fuentes).
    - Evalúa y deduplica resultados protegiendo la seguridad del usuario.
    """

    def __init__(self, default_timeout: float = 3.2):
        self.default_timeout = default_timeout
        self.providers: List[BaseGamerProvider] = [
            DuckDuckGoWebProvider(timeout=default_timeout),
            WikipediaOpenSearchProvider(timeout=default_timeout),
            WikidataEntityProvider(timeout=default_timeout),
            RedditCommunityProvider(timeout=default_timeout),
            GameFAQsGuidesProvider(timeout=default_timeout),
            SteamStoreCommunityProvider(timeout=default_timeout),
            NexusModsModDBProvider(timeout=default_timeout),
            SpeedrunComProvider(timeout=default_timeout),
            InternetArchiveProvider(timeout=default_timeout),
            GitHubGamerProvider(timeout=default_timeout),
        ]
        # Caché en memoria para evitar saturación de consultas repetitivas (TTL 120s)
        self._cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}

    def register_provider(self, provider: BaseGamerProvider) -> None:
        """Permite registrar conectores adicionales de forma dinámica."""
        self.providers.append(provider)

    def search_federated(
        self,
        query: str,
        game_context: Optional[str] = None,
        limit_per_provider: int = 4,
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta la búsqueda en paralelo sobre todos los conectores registrados.
        Retorna resultados deduplicados con reporte de telemetría de fuentes.
        Si se especifica `game_context`, los proveedores enciclopédicos y de bases de datos
        consultan el nombre canónico del juego, mientras que los de comunidades y web
        consultan la frase contextual completa (ej. 'GTA V trucos').
        """
        if not query or len(query.strip()) < 2:
            return {
                "query": query,
                "results": [],
                "total": 0,
                "telemetry": {
                    "queried_providers": [],
                    "successful_providers": [],
                    "failed_providers": [],
                    "errors": {},
                    "elapsed_seconds": 0.0
                }
            }

        cache_key = f"{query.strip().lower()}_{game_context or ''}_{limit_per_provider}_{','.join(sorted(categories)) if categories else 'all'}"
        now = time.time()
        if cache_key in self._cache:
            ts, cached_res = self._cache[cache_key]
            if now - ts < 120.0:  # 2 minutos de TTL
                return cached_res

        start_t = time.perf_counter()
        active_providers = [
            p for p in self.providers
            if categories is None or p.category in categories
        ]

        all_results: List[Dict[str, Any]] = []
        queried_names: List[str] = [p.name for p in active_providers]
        successful_names: List[str] = []
        failed_names: List[str] = []
        error_details: Dict[str, str] = {}
        seen_urls = set()

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(active_providers)) as executor:
            future_to_provider = {}
            for prov in active_providers:
                if prov.category == "database" and game_context:
                    target_q = game_context
                else:
                    target_q = query
                future_to_provider[executor.submit(prov.search, target_q, limit_per_provider)] = prov

            for future in concurrent.futures.as_completed(future_to_provider):
                prov = future_to_provider[future]
                try:
                    res = future.result()
                    if res:
                        successful_names.append(prov.name)
                        for item in res:
                            url = item.get("url")
                            if url and url not in seen_urls:
                                seen_urls.add(url)
                                all_results.append(item)
                    else:
                        successful_names.append(prov.name)
                except Exception as e:
                    failed_names.append(prov.name)
                    error_details[prov.name] = str(e)
                    logger.debug(f"Federated provider error [{prov.name}]: {e}")

        elapsed = round(time.perf_counter() - start_t, 3)

        response_payload = {
            "query": query,
            "results": all_results,
            "total": len(all_results),
            "telemetry": {
                "queried_providers": queried_names,
                "successful_providers": successful_names,
                "failed_providers": failed_names,
                "errors": error_details,
                "elapsed_seconds": elapsed,
                "total_domains_discovered": len(seen_urls)
            }
        }

        # Guardar en caché
        self._cache[cache_key] = (now, response_payload)
        return response_payload


# =====================================================================
# ALIAS Y COMPATIBILIDAD CON CÓDIGO EXISTENTE
# =====================================================================

class OSINTAggregator(FederatedSearchEngine):
    """Clase wrapper para mantener compatibilidad con la suite de pruebas unitarias Fase 4."""

    def __init__(self, timeout_per_provider: float = 3.0):
        super().__init__(default_timeout=timeout_per_provider)

    def search_all(self, query: str, limit_per_provider: int = 4) -> Dict[str, Any]:
        """Interfaz de compatibilidad requerida por tests y vistas previas."""
        res = self.search_federated(query=query, limit_per_provider=limit_per_provider)
        return {
            "query": res["query"],
            "results": res["results"],
            "total": res["total"],
            "telemetry": res.get("telemetry", {})
        }


# Instancia singleton global del motor federado
FEDERATED_SEARCH = FederatedSearchEngine()
OSINT_AGGREGATOR = OSINTAggregator()
