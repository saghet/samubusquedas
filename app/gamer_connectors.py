"""
Gamer Search Engine - Conectores OSINT y Agregación Multi-Fuente
================================================================
Arquitectura modular y extensible de adaptadores para consultar fuentes abiertas
legítimas en tiempo real:
- Speedrun.com API (Récords mundiales y categorías verificadas)
- Internet Archive API (Preservación histórica de software y dominio público)
- GitHub API (Repositorios oficiales de emuladores, homebrew y herramientas de modding)
- Reddit API (Búsqueda de comunidades y foros activos)
Cada conector cuenta con timeout estricto, manejo de fallos y evaluación de ciberseguridad.
"""

import concurrent.futures
import json
import logging
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional
from gamer_security import GAMER_SECURITY

logger = logging.getLogger("GamerConnectors")


class BaseGamerProvider:
    """Clase base abstracta para implementar nuevos proveedores de búsqueda."""
    name: str = "base"
    source_label: str = "Fuente Abierta"

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def health_check(self) -> bool:
        return True


class SpeedrunComProvider(BaseGamerProvider):
    """Conector a la API oficial de Speedrun.com para consultar juegos y tablas de tiempos."""
    name = "speedrun_com"
    source_label = "Speedrun.com Community & Leaderboards"

    def __init__(self, timeout: float = 2.0):
        self.timeout = timeout

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not query or len(query.strip()) < 2:
            return []
        encoded_q = urllib.parse.quote(query.strip())
        url = f"https://www.speedrun.com/api/v1/games?name={encoded_q}&max={limit}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "GamerSearchEngine/2.0 (OSINT Research Bot; Ethical)"}
        )
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
            # Fallback silencioso sin colapsar el motor
            logger.debug(f"Speedrun.com provider timeout/error for '{query}': {e}")
        return results


class InternetArchiveProvider(BaseGamerProvider):
    """Conector a la API de búsqueda avanzada de Internet Archive (Software Preservado)."""
    name = "internet_archive"
    source_label = "Internet Archive (Preservación Histórica)"

    def __init__(self, timeout: float = 2.0):
        self.timeout = timeout

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not query or len(query.strip()) < 2:
            return []
        clean_q = urllib.parse.quote(f"{query} AND mediatype:(software)")
        url = f"https://archive.org/advancedsearch.php?q={clean_q}&fl[]=identifier,title,description,year,licenseurl&sort[]=&rows={limit}&page=1&output=json"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "GamerSearchEngine/2.0 (Digital Preservation Research)"}
        )
        results: List[Dict[str, Any]] = []
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    docs = data.get("response", {}).get("docs", [])
                    for doc in docs:
                        ident = doc.get("identifier")
                        title = doc.get("title") or ident
                        desc = doc.get("description", "Software histórico preservado disponible en el archivo público.")
                        if isinstance(desc, list):
                            desc = " ".join(desc)
                        weblink = f"https://archive.org/details/{ident}"
                        sec_report = GAMER_SECURITY.evaluate_url(weblink)
                        results.append({
                            "id": f"archive_{ident}",
                            "title": title,
                            "category": "Preservación & Dominio Público",
                            "description": str(desc)[:180] + "...",
                            "source": self.source_label,
                            "url": weblink,
                            "security": sec_report.to_dict()
                        })
        except Exception as e:
            logger.debug(f"Internet Archive provider timeout/error for '{query}': {e}")
        return results


class GitHubGamerProvider(BaseGamerProvider):
    """Conector a la API de GitHub para descubrir repositorios de emuladores, modding y homebrew."""
    name = "github"
    source_label = "GitHub Open Source Gaming"

    def __init__(self, timeout: float = 2.0):
        self.timeout = timeout

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not query or len(query.strip()) < 2:
            return []
        clean_q = urllib.parse.quote(f"{query} topic:emulator OR topic:homebrew OR topic:gaming")
        url = f"https://api.github.com/search/repositories?q={clean_q}&sort=stars&order=desc&per_page={limit}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "GamerSearchEngine/2.0",
                "Accept": "application/vnd.github.v3+json"
            }
        )
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
                            "category": "Código Abierto / Emulación",
                            "description": f"⭐ {stars:,} estrellas • Licencia {lic_name} — {desc}",
                            "source": self.source_label,
                            "url": html_url,
                            "security": sec_report.to_dict()
                        })
        except Exception as e:
            logger.debug(f"GitHub provider timeout/error for '{query}': {e}")
        return results


class OSINTAggregator:
    """Agregador concurrente multi-proveedor con control de tiempo de respuesta y aislamiento de errores."""

    def __init__(self, timeout_per_provider: float = 1.8):
        self.providers: List[BaseGamerProvider] = [
            SpeedrunComProvider(timeout=timeout_per_provider),
            InternetArchiveProvider(timeout=timeout_per_provider),
            GitHubGamerProvider(timeout=timeout_per_provider)
        ]

    def register_provider(self, provider: BaseGamerProvider) -> None:
        """Permite conectar dinámicamente nuevos proveedores sin modificar el núcleo del buscador."""
        self.providers.append(provider)

    def search_all(self, query: str, limit_per_provider: int = 4) -> Dict[str, Any]:
        """Ejecuta búsquedas paralelas en todos los proveedores registrados."""
        if not query or len(query.strip()) < 2:
            return {"query": query, "results": [], "total": 0}

        all_results: List[Dict[str, Any]] = []
        # Ejecución concurrente usando ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.providers)) as executor:
            future_to_provider = {
                executor.submit(prov.search, query, limit_per_provider): prov
                for prov in self.providers
            }
            for future in concurrent.futures.as_completed(future_to_provider):
                prov = future_to_provider[future]
                try:
                    res = future.result()
                    all_results.extend(res)
                except Exception as e:
                    logger.debug(f"Error executing provider {prov.name}: {e}")

        return {
            "query": query,
            "results": all_results,
            "total": len(all_results)
        }


# Instancia singleton del agregador OSINT
OSINT_AGGREGATOR = OSINTAggregator()
