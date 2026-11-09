"""
Gaming Discovery & Intelligence Engine - Motor de Puntuación Ponderada 5D y Rankings (Fase 3)
=============================================================================================
Metodología de selección rigurosa para evaluar videojuegos sin depender de un único ranking.

Modelo de 5 Dimensiones Ponderadas:
1. Crítica Especializada (25%): Metacritic, OpenCritic, Famitsu, IGN, GameSpot, Eurogamer.
2. Valoración de Jugadores (25%): User Score, Steam Reviews, GameFAQs, comunidades.
3. Importancia Histórica (20%): Hall of Fame, pioneros de género, impacto arquitectónico.
4. Popularidad y Ventas Documentadas (15%): Cifras oficiales auditadas normalizadas por base instalada.
5. Actividad e Interés de la Comunidad (15%): Speedrun.com, Reddit, modding en Nexus/GitHub.

Modos de Clasificación Intercambiables:
- Ranking General (Score 5D Ponderado)
- Mejores Valorados (Crítica + Jugadores)
- Más Populares (Ventas + Interés Masivo)
- Mayor Importancia Histórica (Hitos culturales e influencia técnica)
- Mejores según la Comunidad (Valoración de usuarios + Actividad en foros/mods)
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
import math
from typing import Any, Dict, List, Optional, Tuple


class RankingCriteria(str, Enum):
    RANKING_GENERAL = "ranking_general"
    MEJORES_VALORADOS = "mejores_valorados"
    MAS_POPULARES = "mas_populares"
    MAYOR_IMPORTANCIA_HISTORICA = "mayor_importancia_historica"
    MEJORES_SEGUN_COMUNIDAD = "mejores_segun_comunidad"


@dataclass
class Score5DBreakdown:
    critic_score: float  # 0.0 - 100.0 (25%)
    user_score: float  # 0.0 - 100.0 (25%)
    historical_importance: float  # 0.0 - 100.0 (20%)
    sales_popularity: float  # 0.0 - 100.0 (15%)
    community_activity: float  # 0.0 - 100.0 (15%)

    # Puntuación global calculada
    composite_score: float = 0.0

    # Metadatos auditables
    sales_documented: str = "No reportada oficialmente"
    historical_milestone: str = ""
    community_hub: str = ""
    critic_sources_count: int = 1
    rank_rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GamerRankerEngine:
    """Motor de cálculo multivariante, normalización y ordenamiento de rankings."""

    def __init__(
        self,
        weight_critic: float = 0.25,
        weight_user: float = 0.25,
        weight_history: float = 0.20,
        weight_sales: float = 0.15,
        weight_community: float = 0.15
    ):
        self.w_critic = weight_critic
        self.w_user = weight_user
        self.w_history = weight_history
        self.w_sales = weight_sales
        self.w_community = weight_community

        # Asegurar suma unitaria
        total_w = self.w_critic + self.w_user + self.w_history + self.w_sales + self.w_community
        if not math.isclose(total_w, 1.0, rel_tol=1e-3):
            self.w_critic /= total_w
            self.w_user /= total_w
            self.w_history /= total_w
            self.w_sales /= total_w
            self.w_community /= total_w

    def normalize_critic_score(self, raw_score: float, scale_max: float = 100.0) -> float:
        """Normaliza puntajes de crítica a escala 0.0 - 100.0."""
        if raw_score <= 0.0:
            return 50.0
        normalized = (raw_score / scale_max) * 100.0
        return max(0.0, min(100.0, round(normalized, 1)))

    def normalize_user_score(self, raw_score: float, scale_max: float = 10.0) -> float:
        """Normaliza puntajes de usuarios a escala 0.0 - 100.0."""
        if raw_score <= 0.0:
            return 50.0
        normalized = (raw_score / scale_max) * 100.0
        return max(0.0, min(100.0, round(normalized, 1)))

    def calculate_sales_score(
        self,
        units_sold_millions: Optional[float],
        console_install_base_millions: Optional[float] = None
    ) -> float:
        """
        Calcula el puntaje de ventas normalizado por la base instalada de la consola
        para evitar sesgos contra plataformas con menor parque de consolas pero altos attach rates.
        """
        if units_sold_millions is None or units_sold_millions <= 0.0:
            return 50.0  # Cifra neutral para juegos sin ventas públicas registradas

        # Tie-ratio (porcentaje de poseedores de la consola que adquirieron el juego)
        attach_rate = (units_sold_millions / console_install_base_millions) if console_install_base_millions and console_install_base_millions > 0 else 0.0

        if units_sold_millions >= 25.0 or attach_rate >= 0.40:
            return 98.0
        elif units_sold_millions >= 15.0 or attach_rate >= 0.30:
            return 93.0
        elif units_sold_millions >= 10.0 or attach_rate >= 0.20:
            return 88.0
        elif units_sold_millions >= 5.0 or attach_rate >= 0.12:
            return 80.0
        elif units_sold_millions >= 2.5 or attach_rate >= 0.06:
            return 72.0
        elif units_sold_millions >= 1.0:
            return 65.0
        else:
            return 58.0

    def calculate_5d_composite(
        self,
        critic_score: float,
        user_score: float,
        historical_importance: float,
        sales_popularity: float,
        community_activity: float,
        game_title: str = "",
        sales_info: str = "",
        historical_milestone: str = ""
    ) -> Score5DBreakdown:
        """Calcula el índice 5D compuesto con desglose y justificación analítica."""
        c = max(0.0, min(100.0, float(critic_score)))
        u = max(0.0, min(100.0, float(user_score)))
        h = max(0.0, min(100.0, float(historical_importance)))
        s = max(0.0, min(100.0, float(sales_popularity)))
        comm = max(0.0, min(100.0, float(community_activity)))

        composite = (c * self.w_critic) + (u * self.w_user) + (h * self.w_history) + (s * self.w_sales) + (comm * self.w_community)
        composite = round(composite, 2)

        # Generar justificación automática
        rationale = (
            f"Índice 5D: {composite:.1f}/100. Respaldado por una crítica especializada de {c:.0f} pts (25%), "
            f"aprobación de jugadores de {u:.0f} pts (25%), peso histórico e influencia de {h:.0f} pts (20%), "
            f"rendimiento comercial de {s:.0f} pts (15%) y actividad comunitaria activa de {comm:.0f} pts (15%)."
        )
        if historical_milestone:
            rationale += f" Hito clave: {historical_milestone}."

        return Score5DBreakdown(
            critic_score=c,
            user_score=u,
            historical_importance=h,
            sales_popularity=s,
            community_activity=comm,
            composite_score=composite,
            sales_documented=sales_info or "Documentado",
            historical_milestone=historical_milestone,
            rank_rationale=rationale
        )

    def sort_games(
        self,
        games: List[Dict[str, Any]],
        criteria: RankingCriteria = RankingCriteria.RANKING_GENERAL,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Ordena una colección de videojuegos según el criterio seleccionado
        y asigna la posición ordinal en el ranking.
        """
        def sort_key(item: Dict[str, Any]) -> float:
            score_5d = item.get("score_5d")
            if isinstance(score_5d, dict):
                c = score_5d.get("critic_score", 50.0)
                u = score_5d.get("user_score", 50.0)
                h = score_5d.get("historical_importance", 50.0)
                s = score_5d.get("sales_popularity", 50.0)
                comm = score_5d.get("community_activity", 50.0)
                comp = score_5d.get("composite_score", 50.0)
            else:
                c = u = h = s = comm = comp = float(item.get("rating", 70.0))

            if criteria == RankingCriteria.RANKING_GENERAL:
                return comp
            elif criteria == RankingCriteria.MEJORES_VALORADOS:
                return (c * 0.5) + (u * 0.5)
            elif criteria == RankingCriteria.MAS_POPULARES:
                return (s * 0.6) + (comm * 0.4)
            elif criteria == RankingCriteria.MAYOR_IMPORTANCIA_HISTORICA:
                return h
            elif criteria == RankingCriteria.MEJORES_SEGUN_COMUNIDAD:
                return (u * 0.5) + (comm * 0.5)
            return comp

        sorted_list = sorted(games, key=sort_key, reverse=True)

        # Asignar posición ordinal en el ranking (1 a N)
        ranked_results: List[Dict[str, Any]] = []
        for idx, g in enumerate(sorted_list[:limit], 1):
            g_copy = dict(g)
            g_copy["rank_position"] = idx
            g_copy["active_sorting_criteria"] = criteria.value
            ranked_results.append(g_copy)

        return ranked_results


# Instancia singleton del motor de ranking
GAMER_RANKER = GamerRankerEngine()
