"""
Suite de Pruebas Unitarias - Fase 3: Módulos de Búsqueda Especializada
======================================================================
Verifica los controladores de videojuegos, trucos/secretos, preservación/emuladores,
comunidades gamer, fichas técnicas, comparador de versiones y opciones de filtros dinámicos.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from gamer_service import GamerSearchService
from gamer_db import GamerSearchEngineDB


class TestGamerPhase3SpecializedModules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.db_path = os.path.join(cls.temp_dir.name, "test_gamer_phase3.db")
        cls.engine_db = GamerSearchEngineDB(db_path=cls.db_path)
        cls.service = GamerSearchService(db=cls.engine_db)

    @classmethod
    def tearDownClass(cls):
        cls.engine_db.close()
        cls.temp_dir.cleanup()

    def test_01_filter_options_integrity(self):
        """Verifica que las opciones de filtros dinámicos contengan las plataformas y categorías requeridas."""
        opts = self.service.get_filter_options()
        self.assertIn("Nintendo Switch", opts["platforms"])
        self.assertIn("PlayStation 5", opts["platforms"])
        self.assertIn("Xbox Series X", opts["platforms"])
        self.assertIn("NES", opts["platforms"])
        self.assertIn("Sega", opts["platforms"])
        self.assertIn("Atari", opts["platforms"])
        self.assertGreaterEqual(len(opts["genres"]), 8)
        self.assertGreaterEqual(len(opts["cheat_categories"]), 10)
        self.assertGreaterEqual(len(opts["preservation_types"]), 8)

    def test_02_games_module_filters_and_sorting(self):
        """Verifica el módulo de videojuegos con filtros de plataforma, género, año y ordenación."""
        # Filtro por año 2023 y ordenación por rating
        res_2023 = self.service.search_games_module(year="2023", sort_by="rating_desc")
        self.assertGreaterEqual(res_2023["count"], 1)
        for g in res_2023["results"]:
            self.assertEqual(g["release_year"], 2023)

        # Filtro por plataforma PlayStation 5
        res_ps5 = self.service.search_games_module(platform="PlayStation 5")
        self.assertGreaterEqual(res_ps5["count"], 1)
        self.assertTrue(any("Marvel's Spider-Man 2" in g["title"] or "God of War Ragnarök" in g["title"] for g in res_ps5["results"]))

        # Filtro por género Fighting
        res_fighting = self.service.search_games_module(genre="Fighting")
        self.assertGreaterEqual(res_fighting["count"], 1)
        self.assertIn("Super Smash Bros. Ultimate", res_fighting["results"][0]["title"])

    def test_03_game_detail_and_version_comparison(self):
        """Verifica la obtención de ficha detallada y el comparador de versiones."""
        detail = self.service.get_game_detail("zelda-totk")
        self.assertIsNotNone(detail)
        game = detail["game"]
        self.assertEqual(game["title"], "The Legend of Zelda: Tears of the Kingdom")
        self.assertGreater(len(game["editions"]), 0)
        self.assertGreater(len(game["updates_patches"]), 0)
        self.assertIn("18.2 GB", game["technical_requirements"])
        self.assertGreaterEqual(len(detail["cheats"]), 1)
        self.assertGreaterEqual(len(detail["communities"]), 1)

        # Comparador de versiones
        comp = self.service.compare_game_versions("zelda-totk")
        self.assertIsNotNone(comp)
        self.assertEqual(comp["title"], game["title"])
        self.assertIn("Standard Edition", comp["editions"])
        self.assertGreaterEqual(comp["rating"], 90.0)

    def test_04_cheats_module_categories(self):
        """Verifica el módulo de trucos con filtrado por categoría (glitches, desbloqueables, trofeos)."""
        # Glitches
        res_glitches = self.service.search_cheats_module(category="glitches")
        self.assertGreaterEqual(res_glitches["count"], 1)
        for c in res_glitches["results"]:
            self.assertEqual(c["category"], "glitches")

        # Desbloqueables
        res_unlock = self.service.search_cheats_module(category="desbloqueables")
        self.assertGreaterEqual(res_unlock["count"], 1)
        self.assertIn("Trajes", res_unlock["results"][0]["title"])

        # Trofeos de PlayStation
        res_trophies = self.service.search_cheats_module(category="trofeos_ps")
        self.assertGreaterEqual(res_trophies["count"], 1)
        self.assertIn("Platino", res_trophies["results"][0]["title"])

    def test_05_preservation_module_across_platforms(self):
        """Verifica que el módulo de preservación abarque todas las plataformas solicitadas (NES hasta PS5, Sega, Atari)."""
        # Emuladores legítimos
        res_emus = self.service.search_preservation_module(item_type="emulator", legal_only=True)
        self.assertGreaterEqual(res_emus["count"], 8)
        emu_titles = [e["title"] for e in res_emus["results"]]
        self.assertTrue(any("Dolphin" in t for t in emu_titles))
        self.assertTrue(any("PCSX2" in t for t in emu_titles))
        self.assertTrue(any("RPCS3" in t for t in emu_titles))
        self.assertTrue(any("SameBoy" in t for t in emu_titles))
        self.assertTrue(any("melonDS" in t for t in emu_titles))
        self.assertTrue(any("Lime3DS" in t for t in emu_titles))
        self.assertTrue(any("Vita3K" in t for t in emu_titles))
        self.assertTrue(any("Flycast" in t for t in emu_titles))
        self.assertTrue(any("Stella" in t for t in emu_titles))

        # Homebrew y dominio público
        res_homebrew = self.service.search_preservation_module(item_type="homebrew")
        self.assertGreaterEqual(res_homebrew["count"], 2)
        hb_ids = [h["id"] for h in res_homebrew["results"]]
        self.assertTrue(any("bladebuster" in hid or "tobu-tobu" in hid or "halo-2600" in hid for hid in hb_ids))

        # Parches de traducción
        res_patches = self.service.search_preservation_module(item_type="translation_patch")
        self.assertGreaterEqual(res_patches["count"], 1)
        self.assertEqual(res_patches["results"][0]["id"], "pres-mother-3-translation")

    def test_06_communities_module_types(self):
        """Verifica el módulo de comunidades por tipo de plataforma (Reddit, Discord, Foros, Speedrun)."""
        # Servidores de Discord oficiales
        res_discord = self.service.search_communities_module(platform_type="discord")
        self.assertGreaterEqual(res_discord["count"], 3)
        for comm in res_discord["results"]:
            self.assertEqual(comm["platform_type"], "discord")
            self.assertTrue(comm["official_url"].startswith("https://discord."))

        # Subreddits de Reddit
        res_reddit = self.service.search_communities_module(platform_type="reddit")
        self.assertGreaterEqual(res_reddit["count"], 3)
        for comm in res_reddit["results"]:
            self.assertEqual(comm["platform_type"], "reddit")
            self.assertTrue("reddit.com" in comm["official_url"])

        # Tablas de Speedrun
        res_speedrun = self.service.search_communities_module(platform_type="speedrun")
        self.assertGreaterEqual(res_speedrun["count"], 1)
        self.assertEqual(res_speedrun["results"][0]["id"], "comm-speedrun-com")

    def test_07_smart_search_coordinator(self):
        """Verifica el coordinador de búsqueda inteligente search_smart con resolución semántica."""
        smart_res = self.service.search_smart("como duplicar objetos en zelda totk")
        self.assertEqual(smart_res["intent"]["detected_game"], "The Legend of Zelda: Tears of the Kingdom")
        self.assertEqual(smart_res["priority_section"], "cheats")
        self.assertGreater(smart_res["total_hits"], 0)


if __name__ == "__main__":
    unittest.main()
