"""
Suite de Pruebas Unitarias - Fase 3: Motor de Puntuación Ponderada 5D y Rankings
===============================================================================
Verifica la metodología de selección multivariante (25/25/20/15/15),
la normalización de escalas, el cálculo del índice 5D y los 5 clasificadores
intercambiables.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from gamer_ranker import (
    GAMER_RANKER,
    GamerRankerEngine,
    RankingCriteria,
    Score5DBreakdown,
)


class TestGamerRankerPhase3(unittest.TestCase):

    def setUp(self):
        self.ranker = GAMER_RANKER

    def test_01_weights_sum_to_one(self):
        """Verifica que los pesos por defecto sean 25%, 25%, 20%, 15% y 15%."""
        self.assertAlmostEqual(self.ranker.w_critic, 0.25)
        self.assertAlmostEqual(self.ranker.w_user, 0.25)
        self.assertAlmostEqual(self.ranker.w_history, 0.20)
        self.assertAlmostEqual(self.ranker.w_sales, 0.15)
        self.assertAlmostEqual(self.ranker.w_community, 0.15)
        total = self.ranker.w_critic + self.ranker.w_user + self.ranker.w_history + self.ranker.w_sales + self.ranker.w_community
        self.assertAlmostEqual(total, 1.0)

    def test_02_normalization_of_critic_and_user_scores(self):
        """Verifica la normalización de Metascore (100) y User Score (10)."""
        # Famitsu 38/40 -> 95.0
        norm_famitsu = self.ranker.normalize_critic_score(38.0, scale_max=40.0)
        self.assertEqual(norm_famitsu, 95.0)

        # Metacritic User 9.1/10 -> 91.0
        norm_user = self.ranker.normalize_user_score(9.1, scale_max=10.0)
        self.assertEqual(norm_user, 91.0)

    def test_03_sales_attach_rate_normalization(self):
        """Verifica el cálculo de ventas ponderado por la base instalada de la consola."""
        # Smash Melee: 7.4M en GameCube (21.7M consolas) = attach rate 34% -> Puntaje >= 90
        score_melee = self.ranker.calculate_sales_score(
            units_sold_millions=7.4,
            console_install_base_millions=21.7
        )
        self.assertGreaterEqual(score_melee, 90.0)

        # Juego sin cifra pública -> neutral 50.0
        score_unreported = self.ranker.calculate_sales_score(None)
        self.assertEqual(score_unreported, 50.0)

    def test_04_calculate_5d_composite_and_rationale(self):
        """Verifica el cálculo del puntaje compuesto y la generación de la explicación analítica."""
        res = self.ranker.calculate_5d_composite(
            critic_score=97.0,
            user_score=91.0,
            historical_importance=99.0,
            sales_popularity=95.0,
            community_activity=92.0,
            game_title="The Legend of Zelda: Breath of the Wild",
            sales_info="32.8 millones de copias",
            historical_milestone="Redefinición del diseño de mundo abierto y física emergente"
        )
        # 97*0.25 (24.25) + 91*0.25 (22.75) + 99*0.20 (19.8) + 95*0.15 (14.25) + 92*0.15 (13.8) = 94.85
        self.assertAlmostEqual(res.composite_score, 94.85, delta=0.1)
        self.assertIn("Índice 5D", res.rank_rationale)
        self.assertIn("Hito clave: Redefinición del diseño de mundo abierto", res.rank_rationale)

    def test_05_interchangeable_sorting_criteria(self):
        """Verifica que los 5 modos de ordenamiento clasifiquen correctamente según la dimensión activa."""
        sample_games = [
            {
                "title": "Juego A - Best-seller Masivo",
                "score_5d": {
                    "critic_score": 80.0,
                    "user_score": 75.0,
                    "historical_importance": 70.0,
                    "sales_popularity": 99.0,
                    "community_activity": 85.0,
                    "composite_score": 80.85
                }
            },
            {
                "title": "Juego B - Pionero Histórico de Nicho",
                "score_5d": {
                    "critic_score": 88.0,
                    "user_score": 86.0,
                    "historical_importance": 98.0,
                    "sales_popularity": 55.0,
                    "community_activity": 70.0,
                    "composite_score": 81.85
                }
            },
            {
                "title": "Juego C - Aclamado por Crítica y Usuarios",
                "score_5d": {
                    "critic_score": 98.0,
                    "user_score": 96.0,
                    "historical_importance": 85.0,
                    "sales_popularity": 75.0,
                    "community_activity": 80.0,
                    "composite_score": 88.75
                }
            }
        ]

        # 1. Ranking General -> Juego C primero (88.75)
        ranked_gen = self.ranker.sort_games(sample_games, criteria=RankingCriteria.RANKING_GENERAL)
        self.assertEqual(ranked_gen[0]["title"], "Juego C - Aclamado por Crítica y Usuarios")
        self.assertEqual(ranked_gen[0]["rank_position"], 1)

        # 2. Mayor Importancia Histórica -> Juego B primero (98.0)
        ranked_hist = self.ranker.sort_games(sample_games, criteria=RankingCriteria.MAYOR_IMPORTANCIA_HISTORICA)
        self.assertEqual(ranked_hist[0]["title"], "Juego B - Pionero Histórico de Nicho")

        # 3. Más Populares -> Juego A primero (99.0 ventas)
        ranked_pop = self.ranker.sort_games(sample_games, criteria=RankingCriteria.MAS_POPULARES)
        self.assertEqual(ranked_pop[0]["title"], "Juego A - Best-seller Masivo")


if __name__ == "__main__":
    unittest.main()
