"""
Suite de Pruebas Unitarias - Fase 1: Arquitectura del Motor y Modelo Gamer
==========================================================================
Verifica el correcto funcionamiento del motor relacional + SQLite FTS5,
los esquemas de datos, la persistencia, la búsqueda unificada y el aislamiento de datos.
"""

import os
import sys
import tempfile
import unittest

# Asegurar importación de app/
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from gamer_models import GameRecord, CheatRecord, PreservationRecord, CommunityRecord
from gamer_db import GamerSearchEngineDB, normalize_gamer_query, highlight_safe_snippet


class TestGamerPhase1Engine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Crear base de datos temporal en disco para aislamiento total
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.db_path = os.path.join(cls.temp_dir.name, "test_gamer_phase1.db")
        cls.engine = GamerSearchEngineDB(db_path=cls.db_path)

    @classmethod
    def tearDownClass(cls):
        cls.engine.close()
        cls.temp_dir.cleanup()

    def test_01_schema_and_seed_initialization(self):
        """Verifica que las tablas e índices FTS5 se hayan creado y poblado con la semilla verificada."""
        stats = self.engine.get_database_stats()
        self.assertGreaterEqual(stats["total_games"], 10, "Deben existir al menos 10 juegos base verificados")
        self.assertGreaterEqual(stats["total_cheats"], 7, "Deben existir al menos 7 trucos y secretos base")
        self.assertGreaterEqual(stats["total_preservation"], 8, "Deben existir al menos 8 recursos de preservación/emulación")
        self.assertGreaterEqual(stats["total_communities"], 8, "Deben existir al menos 8 comunidades gamer verificadas")

    def test_02_search_games_nintendo_ps5_xbox(self):
        """Verifica la búsqueda de videojuegos para los tres ecosistemas prioritarios."""
        # Nintendo Switch
        zelda_hits = self.engine.search_games(query="Zelda", platform="Nintendo Switch")
        self.assertGreaterEqual(len(zelda_hits), 1)
        self.assertTrue(any("Tears of the Kingdom" in g["title"] or "Breath of the Wild" in g["title"] for g in zelda_hits))
        self.assertEqual(zelda_hits[0]["region"], "Global")

        # PlayStation 5
        ps5_hits = self.engine.search_games(query="Spider-Man", platform="PlayStation 5")
        self.assertGreaterEqual(len(ps5_hits), 1)
        self.assertIn("Spider-Man 2", ps5_hits[0]["title"])
        self.assertIn("PlayStation 5", ps5_hits[0]["platforms"])

        # Xbox Series X/S
        xbox_hits = self.engine.search_games(query="Halo", platform="Xbox Series X")
        self.assertGreaterEqual(len(xbox_hits), 1)
        self.assertTrue(any("Halo" in g["title"] for g in xbox_hits))

    def test_03_accent_insensitive_and_diacritics_matching(self):
        """Verifica que 'Ragnarök' y 'Ragnarok' devuelvan el mismo resultado exacto mediante unicode61 remove_diacritics."""
        res_with_accent = self.engine.search_games(query="Ragnarök")
        res_no_accent = self.engine.search_games(query="Ragnarok")
        self.assertGreaterEqual(len(res_with_accent), 1)
        self.assertEqual(res_with_accent[0]["id"], res_no_accent[0]["id"])
        self.assertEqual(res_with_accent[0]["id"], "god-of-war-ragnarok")

    def test_04_search_cheats_and_trophies(self):
        """Verifica el módulo de trucos, secretos, glitches y trofeos."""
        # Glitch de duplicación en Zelda
        glitch_hits = self.engine.search_cheats(query="duplicacion", category="glitches")
        self.assertGreaterEqual(len(glitch_hits), 1)
        self.assertIn("Duplicación", glitch_hits[0]["title"])
        self.assertIn("Tears of the Kingdom", glitch_hits[0]["game_title"])

        # Trofeos de PlayStation en Elden Ring
        trophy_hits = self.engine.search_cheats(query="platino", category="trofeos_ps")
        self.assertGreaterEqual(len(trophy_hits), 1)
        self.assertIn("Elden Lord", trophy_hits[0]["title"])

        # Logros de Xbox en Halo Infinite
        achieve_hits = self.engine.search_cheats(query="Calaveras", category="logros_xbox")
        self.assertGreaterEqual(len(achieve_hits), 1)
        self.assertIn("Catacomb", achieve_hits[0]["title"])

    def test_05_preservation_and_emulators_legal_filtering(self):
        """Verifica que el módulo de preservación localice emuladores legítimos y proyectos autorizados."""
        # Emulador Dolphin
        dolphin_res = self.engine.search_preservation(query="Dolphin", item_type="emulator")
        self.assertGreaterEqual(len(dolphin_res), 1)
        self.assertEqual(dolphin_res[0]["id"], "emu-dolphin")
        self.assertEqual(dolphin_res[0]["legal_status"], "LEGAL_VERIFIED")
        self.assertTrue(dolphin_res[0]["download_safe"])

        # PCSX2 (PS2)
        pcsx2_res = self.engine.search_preservation(query="PCSX2")
        self.assertGreaterEqual(len(pcsx2_res), 1)
        self.assertEqual(pcsx2_res[0]["id"], "emu-pcsx2")

        # Proyecto de descompilación SM64 PC Port
        decomp_res = self.engine.search_preservation(query="Decompilation", legal_only=True)
        self.assertGreaterEqual(len(decomp_res), 1)
        self.assertIn("pres-sm64-decomp", [r["id"] for r in decomp_res])

    def test_06_search_gamer_communities(self):
        """Verifica el buscador de comunidades (Reddit, Discord, Foros, Speedrun) sin datos inventados."""
        # Subreddits de consolas
        sub_nintendo = self.engine.search_communities(query="NintendoSwitch", platform_type="reddit")
        self.assertGreaterEqual(len(sub_nintendo), 1)
        self.assertEqual(sub_nintendo[0]["id"], "comm-r-nintendoswitch")
        self.assertGreaterEqual(sub_nintendo[0]["members_count"], 4000000)

        # Discord oficial de RetroArch
        discord_retro = self.engine.search_communities(query="RetroArch", platform_type="discord")
        self.assertGreaterEqual(len(discord_retro), 1)
        self.assertIn("discord.gg/libretro", discord_retro[0]["official_url"])

        # Speedrun.com
        speedrun_comm = self.engine.search_communities(query="Speedrun")
        self.assertGreaterEqual(len(speedrun_comm), 1)
        self.assertTrue(any("Speedrun.com" in c["name"] for c in speedrun_comm))

    def test_07_unified_search_pipeline(self):
        """Verifica la agregación unificada de resultados a través de todos los módulos."""
        unified = self.engine.unified_search(query="Elden Ring")
        self.assertGreater(unified["total_hits"], 0)
        self.assertGreaterEqual(unified["counts"]["games"], 1)
        self.assertGreaterEqual(unified["counts"]["cheats"], 1)
        self.assertGreaterEqual(unified["counts"]["communities"], 1)
        self.assertLess(unified["elapsed_ms"], 500.0, "La búsqueda debe completarse en menos de 500 ms")

    def test_08_favorites_and_history_lifecycle(self):
        """Verifica el ciclo de vida de favoritos e historial de búsqueda."""
        # Historial
        self.engine.clear_search_history()
        self.engine.add_search_history("Zelda TotK", section="games", count=5)
        history = self.engine.get_search_history(limit=5)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["query"], "Zelda TotK")

        # Favoritos
        fav_added = self.engine.add_favorite(
            item_type="game",
            item_id="zelda-totk",
            title="The Legend of Zelda: Tears of the Kingdom",
            subtitle="Nintendo Switch",
            url="/games?id=zelda-totk"
        )
        self.assertTrue(fav_added)
        favs = self.engine.get_favorites(item_type="game")
        self.assertGreaterEqual(len(favs), 1)
        self.assertEqual(favs[0]["item_id"], "zelda-totk")

        # Eliminar favorito
        removed = self.engine.remove_favorite("game_zelda-totk")
        self.assertTrue(removed)
        favs_after = self.engine.get_favorites(item_type="game")
        self.assertEqual(len(favs_after), 0)

    def test_09_snippet_highlighting_safety(self):
        """Verifica que el resaltado de fragmentos sea seguro contra inyección de HTML."""
        raw_text = "En <Hyrule> se encuentra la espada maestra y escudos sagrados."
        highlighted = highlight_safe_snippet(raw_text, ["espada"])
        self.assertIn('&lt;Hyrule&gt;', highlighted)
        self.assertIn('<mark class="hl">espada</mark>', highlighted)
        self.assertNotIn('<Hyrule>', highlighted)


if __name__ == "__main__":
    unittest.main()
