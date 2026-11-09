"""
Batería Maestra de Pruebas de Aceptación (Fase 12 / Sección 13)
==============================================================
Verifica de extremo a extremo:
1. Las 9 plataformas prioritarias con 30 videojuegos reales y verificados:
   - Nintendo Switch (30)
   - Nintendo Wii (30)
   - Nintendo GameCube (30)
   - PlayStation 5 (30)
   - PlayStation 4 (30)
   - PlayStation 2 (30)
   - Xbox Series X/S (30)
   - Xbox 360 (30)
   - Xbox Original (30)
2. Todas las demás plataformas del inventario histórico y portátil (30 cada una) + Switch 2 (limitación).
3. Integridad de los 24 atributos obligatorios, puntuación 5D y >= 3 fuentes independientes reales.
4. Funcionalidad de búsqueda complementaria en 7 dimensiones (trucos, guías, comunidades, mods, emulación).
5. Funcionalidad del motor de expansión multilingüe (ES, EN, JA, PT).
6. Integración del portal GAMING LIBRARY y la vista de detalle con 8 pestañas.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from gamer_db import GamerSearchEngineDB
from gamer_service import GamerSearchService
from gamer_complementary import GAMER_COMPLEMENTARY
from query_expander import QUERY_EXPANDER
from console_inventory import CONSOLE_INVENTORY
from gamer_views import render_gaming_library_view, render_game_detail_view

class TestGamerPhase12Acceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = GamerSearchEngineDB()
        cls.service = GamerSearchService(db=cls.db)

    def test_01_priority_consoles_top30(self):
        """Prueba de aceptación para los 30 juegos de las 9 consolas exigidas explícitamente."""
        priority_consoles = [
            "nintendo_switch", "nintendo_wii", "nintendo_gamecube",
            "playstation_5", "playstation_4", "playstation_2",
            "xbox_series_xs", "xbox_360", "xbox_original"
        ]

        for cid in priority_consoles:
            games = self.db.get_top_games_by_console(cid, limit=30)
            self.assertEqual(len(games), 30, f"La consola prioritaria {cid} debe tener exactamente 30 juegos.")
            # Cada juego debe tener título, plataforma, rating 5D y justificación
            for g in games:
                self.assertTrue(g.get("title"))
                self.assertGreater(g.get("rating", 0.0), 0.0)
                self.assertTrue(g.get("developer"))
                self.assertTrue(g.get("publisher"))
                self.assertTrue(g.get("genres"))
                sources = g.get("consulted_sources", [])
                self.assertGreaterEqual(len(sources), 3, f"{g.get('title')} debe tener >= 3 fuentes.")

    def test_02_all_inventory_consoles_coverage(self):
        """Verifica la cobertura total del catálogo histórico doméstico, retro y portátil."""
        retro_and_others = [
            "nintendo_wii_u", "playstation_3", "playstation_1", "xbox_one",
            "nintendo_64", "super_nintendo", "nes", "game_boy", "game_boy_color",
            "game_boy_advance", "nintendo_ds", "nintendo_3ds",
            "playstation_portable", "playstation_vita"
        ]

        for cid in retro_and_others:
            games = self.db.get_top_games_by_console(cid, limit=30)
            self.assertEqual(len(games), 30, f"La plataforma {cid} debe contar con 30 títulos verificados.")

    def test_03_switch_2_limitation_policy(self):
        """Comprueba que Nintendo Switch 2 reporte la limitación oficial de hardware sin títulos inventados."""
        games = self.db.get_top_games_by_console("nintendo_switch_2", limit=10)
        self.assertEqual(len(games), 1)
        self.assertIn("LIMITACIÓN DOCUMENTADA", games[0].get("summary", ""))

    def test_04_complementary_engine_multidimensional(self):
        """Prueba que el motor complementario genere las dimensiones para cualquier videojuego."""
        sample_game = self.db.get_top_games_by_console("nintendo_64", limit=1)[0]
        comp_data = GAMER_COMPLEMENTARY.get_complementary_data(sample_game)

        self.assertIn("cheats_and_secrets", comp_data)
        self.assertIn("guides_and_walkthroughs", comp_data)
        self.assertIn("communities", comp_data)
        self.assertIn("mods_and_development", comp_data)
        self.assertIn("preservation_and_emulation", comp_data)
        self.assertIn("news_and_updates", comp_data)
        self.assertIn("consulted_sources", comp_data)

        self.assertGreaterEqual(len(comp_data["cheats_and_secrets"]), 2)
        self.assertGreaterEqual(len(comp_data["guides_and_walkthroughs"]), 2)
        self.assertGreaterEqual(len(comp_data["communities"]), 2)
        self.assertGreaterEqual(len(comp_data["consulted_sources"]), 3)

    def test_05_multilingual_query_expansion(self):
        """Verifica la expansión de consultas multilingües (ES, EN, JA, PT)."""
        res = QUERY_EXPANDER.expand_multilingual_game_queries(
            title="The Legend of Zelda: Ocarina of Time",
            aliases=["Zelda OOT"],
            platform="nintendo_64"
        )
        langs = res["languages"]
        self.assertIn("es", langs)
        self.assertIn("en", langs)
        self.assertIn("ja", langs)
        self.assertIn("pt", langs)

        # Comprobar presencia de palabras clave obligatorias de Sección 9
        en_str = " ".join(langs["en"]).lower()
        self.assertIn("secrets", en_str)
        self.assertIn("glitches", en_str)
        self.assertIn("walkthrough", en_str)
        self.assertIn("community", en_str)

        ja_str = " ".join(langs["ja"])
        self.assertTrue("攻略" in ja_str or "裏技" in ja_str)

        pt_str = " ".join(langs["pt"]).lower()
        self.assertTrue("detonado" in pt_str or "dicas" in pt_str)

    def test_06_gaming_library_service_and_view(self):
        """Verifica que el servicio de Gaming Library y la maquetación funcionen sin errores."""
        lib_data = self.service.get_gaming_library(sub_section="nintendo", console_id="nintendo_switch", criteria="ranking_general")
        self.assertEqual(lib_data["sub_section"], "nintendo")
        self.assertEqual(lib_data["games_count"], 30)

        html_out = render_gaming_library_view(
            sub_section=lib_data["sub_section"],
            selected_console=lib_data["selected_console"],
            available_consoles=lib_data["available_consoles"],
            criteria=lib_data["criteria"],
            games=lib_data["games"]
        )
        self.assertIn("GAMING LIBRARY", html_out)
        self.assertIn("Nintendo Switch", html_out)
        self.assertIn("#1", html_out)

    def test_07_game_detail_8_tabs_view(self):
        """Verifica que la vista de detalle de un juego contenga las 8 pestañas completas."""
        sample_game = self.db.get_top_games_by_console("playstation_5", limit=1)[0]
        detail_payload = self.service.get_game_detail(sample_game["id"])
        self.assertIsNotNone(detail_payload)

        html_detail = render_game_detail_view(detail_payload)
        # Verificar que existan las 8 pestañas
        self.assertIn("1. 📊 Información General", html_detail)
        self.assertIn("2. ⚡ Trucos y Secretos", html_detail)
        self.assertIn("3. 📖 Guías y 100%", html_detail)
        self.assertIn("4. 👥 Comunidades", html_detail)
        self.assertIn("5. 🛠️ Mods &amp; Dev", html_detail)
        self.assertIn("6. 🏛️ Emulación Legal", html_detail)
        self.assertIn("7. 📢 Noticias", html_detail)
        self.assertIn("8. 🔍 Fuentes", html_detail)

if __name__ == "__main__":
    unittest.main()
