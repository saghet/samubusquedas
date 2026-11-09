"""
Suite de Pruebas Unitarias - Fase 5: Conectores Multi-Fuente y Extracción Forense
================================================================================
Verifica que el sistema consulte, corrobore y certifique al menos tres fuentes
independientes por videojuego para Nintendo, PlayStation y Xbox.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from gamer_sources_collector import (
    SOURCES_CORROBORATOR,
    MultiSourceCorroborator,
    VerifiedGameSource
)


class TestGamerSourcesPhase5(unittest.TestCase):

    def setUp(self):
        self.corroborator = SOURCES_CORROBORATOR

    def test_01_platform_specialized_media_selection(self):
        """Verifica la selección de prensa según la plataforma (Nintendo Life, Push Square, Pure Xbox)."""
        src_nintendo = self.corroborator.query_specialized_platform_hub("Super Mario Odyssey", "Nintendo Switch")
        self.assertIsNotNone(src_nintendo)
        self.assertEqual(src_nintendo.name, "Nintendo Life Hub")

        src_ps = self.corroborator.query_specialized_platform_hub("God of War Ragnarok", "PlayStation 5")
        self.assertIsNotNone(src_ps)
        self.assertEqual(src_ps.name, "Push Square Hub")

        src_xbox = self.corroborator.query_specialized_platform_hub("Halo Infinite", "Xbox Series X")
        self.assertIsNotNone(src_xbox)
        self.assertEqual(src_xbox.name, "Pure Xbox Hub")

    def test_02_corroborate_at_least_three_independent_sources_live(self):
        """Verifica en vivo que se obtengan al menos 3 fuentes independientes para títulos clave."""
        test_cases = [
            ("The Legend of Zelda: Breath of the Wild", "Nintendo Switch"),
            ("Bloodborne", "PlayStation 4"),
            ("Halo 3", "Xbox 360")
        ]

        for game_title, platform in test_cases:
            res = self.corroborator.corroborate_game(game_title, platform)
            self.assertIn("sources", res)
            self.assertGreaterEqual(res["total_sources_found"], 3, f"Fallo de fuentes para {game_title}: {res}")
            self.assertTrue(res["min_sources_met"])
            # Verificar que haya variedad de tipos de fuentes
            source_types = {s["source_type"] for s in res["sources"]}
            self.assertGreaterEqual(len(source_types), 2)


if __name__ == "__main__":
    unittest.main()
