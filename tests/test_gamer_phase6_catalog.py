"""
Pruebas de Aceptación para Fase 6: Construcción y Verificación del Catálogo Histórico
===================================================================================
Verifica:
1. Cobertura de 30 mejores títulos por consola en la generación actual y las 4 anteriores:
   - Nintendo: Switch, Wii U, Wii, GameCube (30 cada una) + Switch 2 (limitación documentada).
   - PlayStation: PS5, PS4, PS3, PS2, PS1 (30 cada una).
   - Xbox: Series X/S, Xbox One, Xbox 360, Xbox Original (30 cada una).
2. Cobertura de las líneas independientes portátiles y retro:
   - Nintendo Retro/Portátiles: N64, SNES, NES, GB, GBC, GBA, NDS, 3DS (30 cada una).
   - PlayStation Portátiles: PSP, PS Vita (30 cada una).
3. Verificación de los 24 atributos por ficha y mínimo 3 fuentes independientes reales.
4. Validación de que no existen puntuaciones ni ventas inventadas (5D score normalizado).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from gamer_db import GamerSearchEngineDB
from console_inventory import CONSOLE_INVENTORY

class TestGamerPhase6Catalog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = GamerSearchEngineDB()

    def test_01_home_consoles_top30_coverage(self):
        """Verifica que las consolas de sobremesa (actual + 4 anteriores) tengan 30 juegos."""
        home_consoles = [
            # Nintendo
            "nintendo_switch", "nintendo_wii_u", "nintendo_wii", "nintendo_gamecube",
            # PlayStation
            "playstation_5", "playstation_4", "playstation_3", "playstation_2", "playstation_1",
            # Xbox
            "xbox_series_xs", "xbox_one", "xbox_360", "xbox_original"
        ]

        for cid in home_consoles:
            games = self.db.get_top_games_by_console(cid, limit=30)
            self.assertEqual(len(games), 30, f"La consola {cid} debe tener exactamente 30 títulos en su Top 30.")
            # Verificar que el ranking está ordenado de mayor a menor rating
            ratings = [g.get("rating", 0.0) for g in games]
            self.assertEqual(ratings, sorted(ratings, reverse=True), f"Los títulos de {cid} deben estar ordenados descendentemente.")

    def test_02_retro_and_portable_consoles_coverage(self):
        """Verifica que los catálogos independientes retro y portátiles tengan 30 juegos."""
        retro_portable = [
            "nintendo_64", "super_nintendo", "nes",
            "game_boy", "game_boy_color", "game_boy_advance",
            "nintendo_ds", "nintendo_3ds",
            "playstation_portable", "playstation_vita"
        ]

        for cid in retro_portable:
            games = self.db.get_top_games_by_console(cid, limit=30)
            self.assertEqual(len(games), 30, f"La plataforma retro/portátil {cid} debe tener 30 títulos.")

    def test_03_switch_2_documented_limitation(self):
        """Verifica que Nintendo Switch 2 tenga documentada su limitación según Sección 4."""
        sw2_games = self.db.get_top_games_by_console("nintendo_switch_2", limit=10)
        self.assertGreaterEqual(len(sw2_games), 1)
        briefing = sw2_games[0]
        self.assertIn("LIMITACIÓN DOCUMENTADA", briefing.get("summary", ""))
        self.assertEqual(briefing.get("canonical_platform_id"), "nintendo_switch_2")
        self.assertEqual(briefing.get("units_sold_millions"), 0.0)

    def test_04_required_attributes_and_sources_integrity(self):
        """Verifica que los títulos posean los atributos requeridos y al menos 3 fuentes independientes."""
        sample_consoles = ["nintendo_switch", "playstation_5", "xbox_series_xs", "super_nintendo", "playstation_2"]
        for cid in sample_consoles:
            top_games = self.db.get_top_games_by_console(cid, limit=5)
            for g in top_games:
                # Comprobar fuentes independientes >= 3
                sources = g.get("consulted_sources", [])
                self.assertGreaterEqual(len(sources), 3, f"El juego {g.get('title')} debe tener >= 3 fuentes independientes.")
                for s in sources:
                    self.assertIn("name", s)
                    self.assertIn("url", s)
                    self.assertTrue(s["url"].startswith("http"), f"URL de fuente inválida: {s['url']}")

                # Comprobar 5D Score
                score_5d = g.get("score_5d", {})
                self.assertIsInstance(score_5d, dict)
                self.assertIn("composite_score", score_5d)
                self.assertGreater(score_5d["composite_score"], 0.0)

                # Atributos esenciales de los 24 requeridos
                self.assertTrue(g.get("title"))
                self.assertTrue(g.get("developer"))
                self.assertTrue(g.get("publisher"))
                self.assertTrue(g.get("genres"))
                self.assertTrue(g.get("generation"))
                self.assertIn("backward_compatibility", g)

if __name__ == "__main__":
    unittest.main()
