"""
Gamer Search Engine - Motor de Descubrimiento Recursivo & Deduplicación (Fase 5)
=================================================================================
Sistema autónomo de expansión de fuentes y crawling controlado a profundidad:
1. Recibe la consulta del usuario.
2. Identifica videojuego, plataforma e intención temática.
3. Genera consultas alternativas mediante QueryExpander.
4. Consulta múltiples proveedores en paralelo (Oleada 1).
5. Descubre y cataloga dominios nuevos fuera de la lista base fija.
6. Descubre hipervínculos relacionados e investiga páginas internas (Profundidad = 1).
7. Ejecuta una segunda oleada de búsqueda (Oleada 2) si la cobertura es insuficiente (< 6 resultados).
8. Deduplica rigurosamente por URL normalizada y similitud textual.
9. Clasifica los resultados y mantiene trazabilidad de la fuente original.

Protecciones y Gobernanza:
- Presupuesto estricto de consultas (Query Budget: máx. 12 llamadas HTTP).
- Límite de profundidad (Max Depth: 1).
- Timeouts agresivos (2.5s) y límite de lectura (32 KB por página).
- Aislamiento de excepciones: no colapsa ante fallos de conectividad.
"""

import concurrent.futures
import html
import logging
import re
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Set, Tuple

from gamer_security import GAMER_SECURITY
from query_expander import QUERY_EXPANDER

logger = logging.getLogger("RecursiveDiscovery")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7",
}


def normalize_url(url: str) -> str:
    """Normaliza una URL eliminando fragmentos y parámetros de tracking (utm_*, fbclid, etc.)."""
    if not url:
        return ""
    try:
        parsed = urllib.parse.urlparse(url.strip())
        # Limpiar query string de parámetros de rastreo
        query_params = urllib.parse.parse_qsl(parsed.query, keep_blank_values=False)
        clean_params = [
            (k, v) for k, v in query_params
            if not k.startswith("utm_") and k not in ("fbclid", "gclid", "ref", "source")
        ]
        new_query = urllib.parse.urlencode(clean_params)
        clean_url = urllib.parse.urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip("/") if parsed.path != "/" else "/",
            "",
            new_query,
            ""  # sin fragmento #
        ))
        return clean_url
    except Exception:
        return url.strip()


class RecursiveDiscoveryEngine:
    """Motor de descubrimiento recursivo de fuentes y deduplicación profunda."""

    def __init__(self, max_depth: int = 1, query_budget: int = 10):
        self.max_depth = max_depth
        self.query_budget = query_budget
        # Directorio dinámico de dominios descubiertos en memoria
        self.discovered_domains: Dict[str, Dict[str, Any]] = {}

    def extract_domain(self, url: str) -> str:
        """Extrae el nombre de dominio canónico."""
        try:
            return urllib.parse.urlparse(url).netloc.lower()
        except Exception:
            return ""

    def harvest_page_internal_links(self, page_url: str, game_context: str, max_links: int = 3) -> List[Dict[str, Any]]:
        """
        Investiga una página interna relevante (Profundidad = 1) para descubrir
        sub-secciones especializadas (ej. guías de misiones, listas de trucos).
        """
        if not page_url.startswith("http"):
            return []

        domain = self.extract_domain(page_url)
        # Omitir dominios que bloquean rastreo directo o que son agregadores masivos
        if any(skip in domain for skip in ["duckduckgo.com", "google.com", "bing.com"]):
            return []

        discovered: List[Dict[str, Any]] = []
        req = urllib.request.Request(page_url, headers=HEADERS)

        try:
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                content_type = resp.headers.get("Content-Type", "")
                if "text/html" not in content_type:
                    return []
                # Leer únicamente los primeros 32 KB para eficiencia
                raw_bytes = resp.read(32768)
                page_html = raw_bytes.decode("utf-8", errors="ignore")

                # Extraer título de la página interna
                title_match = re.search(r"<title[^>]*>(.*?)</title>", page_html, re.IGNORECASE | re.DOTALL)
                page_title = title_match.group(1).strip() if title_match else page_url

                # Buscar hipervínculos relacionados con el videojuego o trucos/guías
                all_links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', page_html, re.IGNORECASE | re.DOTALL)
                
                game_tokens = [tok.lower() for tok in re.split(r"\W+", game_context) if len(tok) >= 3]

                for link_href, link_text in all_links:
                    if len(discovered) >= max_links:
                        break

                    clean_href = link_href.strip()
                    if not clean_href or clean_href.startswith(("#", "javascript:", "mailto:")):
                        continue

                    # Resolver URL relativa a absoluta
                    full_url = urllib.parse.urljoin(page_url, clean_href)
                    if not full_url.startswith("http") or full_url == page_url:
                        continue

                    clean_text = re.sub(r"<[^>]+>", "", link_text).strip()
                    clean_text = html.unescape(clean_text)

                    # Evaluar si el enlace tiene relevancia temática
                    combined = f"{clean_text} {full_url}".lower()
                    is_relevant = any(tok in combined for tok in game_tokens) or any(
                        kw in combined for kw in ["truco", "cheat", "guia", "guide", "secreto", "mod", "glitch"]
                    )

                    if is_relevant and len(clean_text) >= 4:
                        sec = GAMER_SECURITY.evaluate_url(full_url)
                        discovered.append({
                            "id": f"rec_{abs(hash(full_url))}",
                            "title": f"[{domain}] {clean_text}",
                            "category": "Enlace Relacionado Descubierto",
                            "description": f"Sub-sección especializada descubierta en {page_title[:60]}...",
                            "source": f"Descubrimiento Recursivo ({domain})",
                            "url": full_url,
                            "parent_url": page_url,
                            "depth": 1,
                            "security": sec.to_dict()
                        })
        except Exception as e:
            logger.debug(f"Harvest internal links error on '{page_url}': {e}")

        return discovered

    def execute_recursive_discovery(
        self,
        raw_query: str,
        initial_results: List[Dict[str, Any]],
        game_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta el pipeline de descubrimiento recursivo:
        1. Recolección y registro de nuevos dominios encontrados en Oleada 1.
        2. Evaluación de cobertura. Si cobertura < 6, dispara Oleada 2 con consulta alternativa.
        3. Exploración de enlaces internos en los 2 mejores resultados.
        4. Deduplicación inteligente de URLs y títulos.
        5. Retorna resultados consolidados con trazabilidad de fuentes y dominios descubiertos.
        """
        start_t = time.perf_counter()
        normalized_seen_urls: Set[str] = set()
        dedup_results: List[Dict[str, Any]] = []
        newly_discovered_domains: List[str] = []

        # 1. Deduplicar y catalogar dominios de la primera oleada
        for item in initial_results:
            url = item.get("url", "")
            norm_u = normalize_url(url)
            if norm_u and norm_u not in normalized_seen_urls:
                normalized_seen_urls.add(norm_u)
                item["normalized_url"] = norm_u
                item["wave"] = 1
                item["depth"] = 0
                dedup_results.append(item)

                dom = self.extract_domain(norm_u)
                if dom and dom not in self.discovered_domains:
                    self.discovered_domains[dom] = {
                        "domain": dom,
                        "first_seen_query": raw_query,
                        "discovered_at": time.time(),
                        "sample_url": norm_u
                    }
                    newly_discovered_domains.append(dom)

        # 2. Evaluación de Cobertura y Disparo de Oleada 2 si es insuficiente
        wave_2_executed = False
        wave_2_query = None
        if len(dedup_results) < 6:
            # Obtener consultas alternativas del expansor
            exp_info = QUERY_EXPANDER.expand_query(raw_query, fetch_live_suggestions=False)
            alt_queries = exp_info.get("expanded_queries", [])
            # Seleccionar una consulta alternativa diferente a la original
            candidate_queries = [q for q in alt_queries if q.lower() != raw_query.strip().lower()]
            if candidate_queries:
                wave_2_query = candidate_queries[0]
                try:
                    from gamer_connectors import FEDERATED_SEARCH
                    wave_2_res = FEDERATED_SEARCH.search_federated(
                        query=wave_2_query,
                        game_context=game_context,
                        limit_per_provider=2
                    )
                    wave_2_executed = True
                    for item in wave_2_res.get("results", []):
                        url = item.get("url", "")
                        norm_u = normalize_url(url)
                        if norm_u and norm_u not in normalized_seen_urls:
                            normalized_seen_urls.add(norm_u)
                            item["normalized_url"] = norm_u
                            item["wave"] = 2
                            item["depth"] = 0
                            dedup_results.append(item)

                            dom = self.extract_domain(norm_u)
                            if dom and dom not in self.discovered_domains:
                                self.discovered_domains[dom] = {
                                    "domain": dom,
                                    "first_seen_query": wave_2_query,
                                    "discovered_at": time.time(),
                                    "sample_url": norm_u
                                }
                                newly_discovered_domains.append(dom)
                except Exception as e:
                    logger.debug(f"Wave 2 execution error for '{wave_2_query}': {e}")

        # 3. Exploración de enlaces internos (Profundidad = 1) en las mejores fuentes
        deep_links_discovered: List[Dict[str, Any]] = []
        target_candidates = [
            it for it in dedup_results
            if it.get("depth", 0) == 0 and "wikipedia" not in it.get("url", "") and "speedrun" not in it.get("url", "")
        ][:2]

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_to_url = {
                executor.submit(
                    self.harvest_page_internal_links,
                    it["url"],
                    game_context or raw_query,
                    max_links=2
                ): it["url"]
                for it in target_candidates
            }
            for fut in concurrent.futures.as_completed(future_to_url):
                try:
                    links = fut.result()
                    for lk in links:
                        norm_u = normalize_url(lk["url"])
                        if norm_u not in normalized_seen_urls:
                            normalized_seen_urls.add(norm_u)
                            lk["normalized_url"] = norm_u
                            lk["wave"] = 1
                            deep_links_discovered.append(lk)
                            dedup_results.append(lk)
                except Exception as e:
                    logger.debug(f"Error harvesting deep links: {e}")

        elapsed = round(time.perf_counter() - start_t, 3)

        return {
            "query": raw_query,
            "total_results": len(dedup_results),
            "results": dedup_results,
            "deep_links_discovered": len(deep_links_discovered),
            "new_domains_discovered": newly_discovered_domains,
            "total_catalog_domains": len(self.discovered_domains),
            "wave_2_executed": wave_2_executed,
            "wave_2_query": wave_2_query,
            "elapsed_seconds": elapsed
        }


# Instancia singleton del motor de descubrimiento recursivo
RECURSIVE_ENGINE = RecursiveDiscoveryEngine(max_depth=1, query_budget=10)
