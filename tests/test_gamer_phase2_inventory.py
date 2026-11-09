"""
Suite de Pruebas Unitarias - Fase 2: Inventario Histórico de Consolas y Generaciones
===================================================================================
Verifica el inventario formal de plataformas para Nintendo, PlayStation y Xbox,
la separación estricta entre sobremesa y portátiles, y el motor de deduplicación
de retrocompatibilidad.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from console_inventory import (
    CONSOLE_INVENTORY,
    ConsoleRecord,
    Manufacturer,
    PlatformLine,
)


class TestConsoleInventoryPhase2(unittest.TestCase):

    def setUp(self):
        self.inv = CONSOLE_INVENTORY

    def test_01_nintendo_home_current_and_previous_4(self):
        """Verifica la línea de sobremesa/híbrida de Nintendo (Switch 2, Switch, Wii U, Wii, GameCube)."""
        home = self.inv.get_home_consoles_current_and_previous(Manufacturer.NINTENDO.value)
        home_ids = [c.id for c in home]
        self.assertIn("nintendo_switch_2", home_ids)
        self.assertIn("nintendo_switch", home_ids)
        self.assertIn("nintendo_wii_u", home_ids)
        self.assertIn("nintendo_wii", home_ids)
        self.assertIn("nintendo_gamecube", home_ids)
        # Asegurar que las portátiles no se mezclan con las consolas de sobremesa
        self.assertNotIn("game_boy_advance", home_ids)
        self.assertNotIn("nintendo_ds", home_ids)

    def test_02_nintendo_retro_and_handheld_catalogue(self):
        """Verifica el catálogo retro independiente de Nintendo (N64, SNES, NES, GB, GBC, GBA, DS, 3DS)."""
        retro = self.inv.get_retro_and_handheld_catalogue(Manufacturer.NINTENDO.value)
        retro_ids = [c.id for c in retro]
        expected = [
            "nintendo_64", "super_nintendo", "nes",
            "game_boy", "game_boy_color", "game_boy_advance",
            "nintendo_ds", "nintendo_3ds"
        ]
        for exp in expected:
            self.assertIn(exp, retro_ids, f"Falta {exp} en el catálogo retro/portátil de Nintendo")

    def test_03_playstation_home_and_handhelds(self):
        """Verifica PlayStation 5 a PlayStation 1 en sobremesa y PSP / PS Vita en catálogo independiente."""
        ps_home = self.inv.get_home_consoles_current_and_previous(Manufacturer.PLAYSTATION.value)
        ps_home_ids = [c.id for c in ps_home]
        self.assertEqual(len(ps_home_ids), 5)
        self.assertEqual(ps_home_ids, ["playstation_5", "playstation_4", "playstation_3", "playstation_2", "playstation_1"])

        ps_handhelds = self.inv.get_retro_and_handheld_catalogue(Manufacturer.PLAYSTATION.value)
        ps_handheld_ids = [c.id for c in ps_handhelds]
        self.assertIn("playstation_portable", ps_handheld_ids)
        self.assertIn("playstation_vita", ps_handheld_ids)

    def test_04_xbox_generations(self):
        """Verifica Xbox Series X/S, Xbox One, Xbox 360 y Xbox original."""
        xbox_consoles = self.inv.get_home_consoles_current_and_previous(Manufacturer.XBOX.value)
        xbox_ids = [c.id for c in xbox_consoles]
        self.assertEqual(xbox_ids, ["xbox_series_xs", "xbox_one", "xbox_360", "xbox_original"])

    def test_05_backward_compatibility_deduplication(self):
        """
        Regla de oro: No contabilizar una versión retrocompatible como un juego nuevo.
        Verifica que Red Dead Redemption de Xbox 360 ejecutado en Series X no se contabilice como juego nativo de Series X.
        """
        res = self.inv.resolve_backward_compatibility(
            game_title="Red Dead Redemption",
            original_platform_id="xbox_360",
            played_on_platform_id="xbox_series_xs"
        )
        self.assertTrue(res["is_backward_compatible"])
        self.assertFalse(res["is_native"])
        self.assertEqual(res["canonical_platform"], "Xbox 360")
        self.assertEqual(res["host_platform"], "Xbox Series X/S")

    def test_06_dynamic_console_registration(self):
        """Verifica que el inventario se actualice dinámicamente si se añade una nueva plataforma."""
        custom_console = ConsoleRecord(
            id="steam_deck_oled",
            name="Steam Deck OLED",
            short_name="Steam Deck",
            manufacturer="Valve",
            line=PlatformLine.HANDHELD_CONSOLE.value,
            generation_number=9,
            generation_label="PC Handheld Generación 9",
            release_year=2023,
            lifespan="2023 - Presente",
            media_format="Almacenamiento NVMe / MicroSD",
            target_top_games=30
        )
        self.inv.register_console(custom_console)
        retrieved = self.inv.get_console("steam_deck_oled")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Steam Deck OLED")


if __name__ == "__main__":
    unittest.main()
