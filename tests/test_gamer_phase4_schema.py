"""
Suite de Pruebas Unitarias - Fase 4: Ampliación del Esquema y Modelo de 24 Atributos
===================================================================================
Verifica el almacenamiento, indexación y recuperación íntegra de la ficha técnica
exhaustiva de 24 atributos por videojuego requerida en la Sección 7 del proyecto.
"""

import os
import sys
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from gamer_models import GameRecord
from gamer_db import GamerSearchEngineDB


class TestGamerSchemaPhase4(unittest.TestCase):

    def setUp(self):
        # Base de datos en archivo temporal aislado
        self.tmp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp_dir, "test_phase4.db")
        self.db = GamerSearchEngineDB(db_path=self.db_path)

    def tearDown(self):
        try:
            self.db._conn.close()
        except Exception:
            pass

    def test_01_game_record_complete_24_attributes(self):
        """Verifica que GameRecord contenga los 24 atributos requeridos."""
        record = GameRecord(
            id="totk_test",
            title="The Legend of Zelda: Tears of the Kingdom",  # 1. Nombre oficial
            aliases=["TOTK", "Zelda TOTK", "ゼルダの伝説 ティアーズ オブ ザ キングダム"],  # 2. Nombre alternativo
            cover_url="https://images.igdb.com/igdb/image/upload/t_cover_big/co5vmg.png",  # 3. Portada
            screenshots=[  # 4. Capturas
                "https://images.igdb.com/igdb/image/upload/t_screenshot_huge/sc8b9c.jpg",
                "https://images.igdb.com/igdb/image/upload/t_screenshot_huge/sc8b9d.jpg"
            ],
            platforms=["Nintendo Switch"],  # 5. Plataforma
            canonical_platform_id="nintendo_switch",
            generation="Generación Actual (9ª Generación)",  # 6. Generación
            generation_number=9,
            release_date="2023-05-12",  # 7. Fecha de lanzamiento
            release_year=2023,
            developer="Nintendo EPD",  # 8. Desarrollador
            publisher="Nintendo",  # 9. Distribuidor
            genres=["Acción-Aventura", "Mundo Abierto"],  # 10. Género
            languages=["Español", "Inglés", "Japonés", "Francés", "Alemán"],  # 11. Idiomas
            regions_released=["Global", "Japón", "Norteamérica", "Europa"],  # 12. Regiones
            critic_score=96.0,  # 13. Crítica
            user_score=85.0,  # 14. Usuarios
            sales_documented="20.61 millones de copias (CESA 2024)",  # 15. Ventas
            units_sold_millions=20.61,
            rank_position=1,  # 16. Posición
            summary="Aventura épica por tierra y cielo en el reino de Hyrule.",  # 17. Descripción
            features=["Habilidad Ultramano", "Fusión de Armas", "Islas Celestes", "Profundidades subterráneas"],  # 18. Características
            dlcs=[],  # 19. DLC
            expansions=[],  # 20. Expansiones
            versions=["Edición Estándar", "Edición Coleccionista", "Nintendo Switch OLED TOTK Edition"],  # 21. Versiones
            remasters=[],  # 22. Remasters
            remakes=[],  # 23. Remakes
            backward_compatibility={  # 24. Retrocompatibilidad
                "playable_on_future": "Nintendo Switch 2 (Compatible)",
                "enhancements": "Modo de alto rendimiento y resolución nativa"
            },
            score_5d={
                "critic_score": 96.0,
                "user_score": 85.0,
                "historical_importance": 94.0,
                "sales_popularity": 92.0,
                "community_activity": 91.0,
                "composite_score": 91.85
            },
            consulted_sources=[  # >= 3 fuentes independientes
                {"name": "Metacritic", "url": "https://www.metacritic.com/game/the-legend-of-zelda-tears-of-the-kingdom/"},
                {"name": "IGDB", "url": "https://www.igdb.com/games/the-legend-of-zelda-tears-of-the-kingdom"},
                {"name": "Wikipedia CESA Report", "url": "https://en.wikipedia.org/wiki/The_Legend_of_Zelda:_Tears_of_the_Kingdom"}
            ],
            updated_date="2026-11-08T18:00:00Z"
        )

        d = record.to_dict()
        self.assertEqual(d["title"], "The Legend of Zelda: Tears of the Kingdom")
        self.assertEqual(len(d["screenshots"]), 2)
        self.assertEqual(len(d["consulted_sources"]), 3)
        self.assertEqual(d["canonical_platform_id"], "nintendo_switch")

    def test_02_database_persistence_and_retrieval_24_attributes(self):
        """Verifica la inserción y recuperación íntegra de los 24 atributos en SQLite."""
        record = GameRecord(
            id="sm_odyssey_test",
            title="Super Mario Odyssey",
            aliases=["SMO", "Mario Odyssey"],
            cover_url="https://images.igdb.com/igdb/image/upload/t_cover_big/co1m35.png",
            screenshots=["https://images.igdb.com/sc01.jpg", "https://images.igdb.com/sc02.jpg"],
            platforms=["Nintendo Switch"],
            canonical_platform_id="nintendo_switch",
            generation="9ª Generación",
            generation_number=9,
            release_date="2017-10-27",
            release_year=2017,
            developer="Nintendo EPD",
            publisher="Nintendo",
            genres=["Plataformas 3D"],
            languages=["Español", "Inglés", "Japonés"],
            regions_released=["Global"],
            critic_score=97.0,
            user_score=89.0,
            sales_documented="27.65 millones de unidades (Marzo 2024)",
            units_sold_millions=27.65,
            rank_position=2,
            summary="Aventura 3D estilo sandbox recorriendo reinos con Cappy.",
            features=["Mecánica de captura con Cappy", "Reinos abiertos estilo sandbox"],
            dlcs=[],
            expansions=[],
            versions=["Física", "Digital eShop"],
            remasters=[],
            remakes=[],
            backward_compatibility={"switch_2": "Compatible con Game Boost"},
            score_5d={"composite_score": 93.5},
            consulted_sources=[
                {"name": "Metacritic", "url": "https://metacritic.com"},
                {"name": "OpenCritic", "url": "https://opencritic.com"},
                {"name": "Nintendo Official IR", "url": "https://nintendo.co.jp"}
            ],
            updated_date="2026-11-08T18:00:00Z"
        )

        self.db.insert_game(record)
        retrieved = self.db.get_game_by_id("sm_odyssey_test")

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["title"], "Super Mario Odyssey")
        self.assertEqual(retrieved["canonical_platform_id"], "nintendo_switch")
        self.assertEqual(len(retrieved["screenshots"]), 2)
        self.assertEqual(len(retrieved["languages"]), 3)
        self.assertEqual(retrieved["critic_score"], 97.0)
        self.assertEqual(retrieved["units_sold_millions"], 27.65)
        self.assertEqual(len(retrieved["consulted_sources"]), 3)
        self.assertIn("switch_2", retrieved["backward_compatibility"])

    def test_03_top_games_by_console_query(self):
        """Verifica la consulta de los mejores juegos de una consola ordenados mediante el motor 5D."""
        g1 = GameRecord(
            id="g1", title="Top Game 1", platforms=["Nintendo Switch"],
            canonical_platform_id="nintendo_switch",
            score_5d={"composite_score": 95.0, "critic_score": 97.0, "user_score": 93.0}
        )
        g2 = GameRecord(
            id="g2", title="Top Game 2", platforms=["Nintendo Switch"],
            canonical_platform_id="nintendo_switch",
            score_5d={"composite_score": 88.0, "critic_score": 89.0, "user_score": 87.0}
        )
        self.db.insert_game(g1)
        self.db.insert_game(g2)

        top_games = self.db.get_top_games_by_console("nintendo_switch", criteria="ranking_general")
        self.assertGreaterEqual(len(top_games), 2)
        # Top Game 1 tiene composite score 95.0, debe ser #1
        self.assertEqual(top_games[0]["title"], "Top Game 1")
        self.assertEqual(top_games[0]["rank_position"], 1)


if __name__ == "__main__":
    unittest.main()
