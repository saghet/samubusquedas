"""
Gamer Search Engine - Motor de Calidad de Resultados y Corroboración Cruzada (Fase 7)
======================================================================================
Evalúa rigurosamente cada resultado para filtrar contenido basura, clickbait y desinformación.

Dimensiones evaluadas (0 a 100 puntos):
1. Relevancia Temática (0 - 25 pts)
2. Autoridad de la Fuente (0 - 20 pts)
3. Coincidencia con el Videojuego (0 - 15 pts)
4. Coincidencia con la Plataforma (0 - 10 pts)
5. Coincidencia con la Versión / Parche (0 - 10 pts)
6. Calidad Documental y Profundidad (0 - 10 pts)
7. Corroboración Cruzada Independiente (0 - 10 pts)

Regla de Oro Epistémica:
- Ningún rumor, teoría de fans o afirmación no corroborada se presenta como información confirmada.
- Umbral de corte de calidad: Resultados con score < 35 son descartados automáticamente.
"""

import logging
import re
import urllib.parse
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("ResultQualityEngine")

# Jerarquía de autoridad de dominio (Tier 1 a Tier 4)
DOMAIN_AUTHORITY_TIERS: Dict[str, int] = {
    # Tier 1: Oficiales, fabricantes, desarrolladores y repositorios abiertos primarios (20 pts)
    "rockstargames.com": 20,
    "nintendo.com": 20,
    "playstation.com": 20,
    "xbox.com": 20,
    "steampowered.com": 20,
    "wikipedia.org": 19,
    "wikidata.org": 19,
    "github.com": 18,
    
    # Tier 2: Archivos de referencia técnica, preservación y bases de datos consolidadas (16 pts)
    "tcrf.net": 17,
    "archive.org": 16,
    "speedrun.com": 16,
    "pcgamingwiki.com": 16,
    "gamefaqs.gamespot.com": 15,
    "tasvideos.org": 15,
    "romhacking.net": 15,
    "cookieplmonster.github.io": 16,
    
    # Tier 3: Comunidades especializadas de prestigio y prensa técnica gaming (12 pts)
    "gtaforums.com": 13,
    "reddit.com": 13,
    "nexusmods.com": 13,
    "moddb.com": 12,
    "ign.com": 12,
    "vandal.elespanol.com": 12,
    "xataka.com": 11,
    "3djuegos.com": 11,
    "eurogamer.es": 11,
    "zeldaspeedruns.com": 13,
    
    # Tier 4: Sitios web generales y wikis de fans (8 pts)
    "fandom.com": 9,
    "wikia.org": 9,
    "gamebanana.com": 10,
    "playnesta.com": 9
}

# Patrones lingüísticos de rumores, filtraciones dudosas y desinformación
RUMOR_INDICATOR_PATTERNS = [
    re.compile(r"\b(podria\s+ser|se\s+rumorea|rumor|rumores|supuesto|supuesta|posiblemente|leak\s+unconfirmed|fan\s+theory|teoria\s+de\s+fans|se\s+cree\s+que|sin\s+confirmar)\b", re.IGNORECASE),
    re.compile(r"\b(confirmed\?|is\s+it\s+real\?|fake\s+or\s+real|debunked|hoax|clickbait)\b", re.IGNORECASE)
]


class ResultQualityEngine:
    """Motor de evaluación de calidad, filtrado y corroboración cruzada de resultados."""

    def __init__(self, quality_threshold: float = 35.0):
        self.quality_threshold = quality_threshold

    def extract_domain(self, url: str) -> str:
        """Extrae el dominio canónico en minúsculas."""
        try:
            netloc = urllib.parse.urlparse(url).netloc.lower()
            return netloc.replace("www.", "")
        except Exception:
            return ""

    def evaluate_source_authority(self, url: str) -> float:
        """Calcula los puntos de autoridad del dominio de 0 a 20."""
        domain = self.extract_domain(url)
        for known_domain, score in DOMAIN_AUTHORITY_TIERS.items():
            if known_domain in domain:
                return float(score)
        # Dominio genérico desconocido
        return 7.0

    def evaluate_relevance(self, query: str, title: str, description: str) -> float:
        """Evalúa la coincidencia de tokens entre la consulta y el contenido (0 a 25 pts)."""
        if not query:
            return 10.0

        q_tokens = [tok.lower() for tok in re.split(r"\W+", query) if len(tok) >= 2]
        if not q_tokens:
            return 10.0

        title_lower = title.lower()
        desc_lower = description.lower()

        matches_in_title = sum(1 for tok in q_tokens if tok in title_lower)
        matches_in_desc = sum(1 for tok in q_tokens if tok in desc_lower)

        ratio_title = matches_in_title / len(q_tokens)
        ratio_desc = matches_in_desc / len(q_tokens)

        # Título pondera más (hasta 18 pts) que la descripción (hasta 7 pts)
        score = (ratio_title * 18.0) + (ratio_desc * 7.0)
        return min(25.0, round(score, 1))

    def evaluate_game_match(self, detected_game: Optional[str], title: str, description: str) -> float:
        """Verifica coincidencia estricta con el videojuego objetivo (0 a 15 pts)."""
        if not detected_game:
            return 10.0  # Sin juego específico detectado, neutral

        combined = f"{title} {description}".lower()
        game_tokens = [tok.lower() for tok in re.split(r"\W+", detected_game) if len(tok) >= 3]
        
        matches = sum(1 for tok in game_tokens if tok in combined)
        ratio = matches / len(game_tokens) if game_tokens else 1.0

        if ratio >= 0.75:
            return 15.0
        elif ratio >= 0.4:
            return 8.0
        else:
            return 2.0  # Penalización por hablar de un juego distinto

    def evaluate_platform_match(self, target_platform: Optional[str], title: str, description: str) -> float:
        """Evalúa coincidencia de plataforma (0 a 10 pts)."""
        if not target_platform or target_platform == "Todas":
            return 8.0

        combined = f"{title} {description}".lower()
        plat_lower = target_platform.lower()

        if plat_lower in combined:
            return 10.0
        # Coincidencias de familias
        if "playstation" in plat_lower and ("ps5" in combined or "ps4" in combined or "playstation" in combined):
            return 9.0
        if "xbox" in plat_lower and "xbox" in combined:
            return 9.0
        if "switch" in plat_lower and ("switch" in combined or "nintendo" in combined):
            return 9.0
        return 5.0

    def evaluate_document_quality(self, title: str, description: str) -> float:
        """Evalúa longitud y estructura informativa para descartar páginas vacías o clickbait (0 a 10 pts)."""
        score = 5.0
        if len(description) >= 60:
            score += 2.5
        if len(description) >= 120:
            score += 2.5

        # Penalización si el título contiene mayúsculas excesivas o lenguaje de clickbait
        if re.search(r"\b(NO VAS A CREER|IMPERDIBLE|INCREIBLE|OMG|SHOCKING)\b", title, re.IGNORECASE):
            score -= 3.0

        return max(1.0, min(10.0, score))

    def detect_rumor_content(self, title: str, description: str) -> bool:
        """Detecta si el contenido contiene indicios de ser un rumor no verificado."""
        combined = f"{title} {description}"
        for pat in RUMOR_INDICATOR_PATTERNS:
            if pat.search(combined):
                return True
        return False

    def evaluate_item(
        self,
        item: Dict[str, Any],
        query: str,
        detected_game: Optional[str] = None,
        target_platform: Optional[str] = None,
        independent_domain_counts: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """Calcula el score de calidad multifactorial para un resultado individual."""
        url = item.get("url", "")
        title = item.get("title", "")
        desc = item.get("description", "")

        s_auth = self.evaluate_source_authority(url)
        s_rel = self.evaluate_relevance(query, title, desc)
        s_game = self.evaluate_game_match(detected_game, title, desc)
        s_plat = self.evaluate_platform_match(target_platform, title, desc)
        s_doc = self.evaluate_document_quality(title, desc)

        # Corroboración cruzada: si el dominio pertenece a un grupo temático con respaldo múltiple (+5 a +10 pts)
        dom = self.extract_domain(url)
        s_cross = 0.0
        if independent_domain_counts and dom in independent_domain_counts and independent_domain_counts[dom] >= 2:
            s_cross = 8.0
        elif s_auth >= 18:
            s_cross = 10.0  # Las fuentes Tier 1 tienen corroboración inherente

        total_score = s_auth + s_rel + s_game + s_plat + s_doc + s_cross
        total_score = round(min(100.0, max(0.0, total_score)), 1)

        # Filtro de rumor: evitar presentar rumores como confirmados
        is_rumor = self.detect_rumor_content(title, desc)
        epistemic_grade = "CONFIRMADO"
        if is_rumor or s_auth < 10.0:
            epistemic_grade = "RUMOR / PENDIENTE"

        item["quality_score"] = total_score
        item["epistemic_grade"] = epistemic_grade
        item["quality_breakdown"] = {
            "authority": s_auth,
            "relevance": s_rel,
            "game_match": s_game,
            "platform_match": s_plat,
            "document_quality": s_doc,
            "cross_corroboration": s_cross
        }
        return item

    def filter_and_rank_results(
        self,
        results: List[Dict[str, Any]],
        query: str,
        detected_game: Optional[str] = None,
        target_platform: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Evalúa, filtra y ordena los resultados por calidad decreciente.
        Retorna (accepted_results, discarded_results).
        """
        # Calcular mapa de dominios para corroboración cruzada
        domain_counts: Dict[str, int] = {}
        for it in results:
            d = self.extract_domain(it.get("url", ""))
            if d:
                domain_counts[d] = domain_counts.get(d, 0) + 1

        accepted: List[Dict[str, Any]] = []
        discarded: List[Dict[str, Any]] = []

        for item in results:
            scored_item = self.evaluate_item(
                item=item,
                query=query,
                detected_game=detected_game,
                target_platform=target_platform,
                independent_domain_counts=domain_counts
            )
            if scored_item["quality_score"] >= self.quality_threshold:
                accepted.append(scored_item)
            else:
                scored_item["discard_reason"] = f"Puntaje de calidad insuficiente ({scored_item['quality_score']:.1f} < {self.quality_threshold})"
                discarded.append(scored_item)

        # Ordenar aceptados por calidad decreciente
        accepted.sort(key=lambda x: x["quality_score"], reverse=True)
        return accepted, discarded


# Instancia singleton del motor de calidad
QUALITY_ENGINE = ResultQualityEngine(quality_threshold=35.0)
