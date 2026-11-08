"""
Suite de Pruebas Unitarias - Fase 2: IA Semántica y NLP Gamer
=============================================================
Certifica el analizador de lenguaje natural, la extracción de entidades,
la desambiguación de acrónimos, el enrutamiento por intención y la detección de amenazas.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from gamer_ai import GAMER_AI, GamerSemanticAI
from gamer_db import GamerSearchEngineDB


class TestGamerPhase2AI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.db_path = os.path.join(cls.temp_dir.name, "test_gamer_phase2.db")
        cls.engine = GamerSearchEngineDB(db_path=cls.db_path)
        cls.ai = GAMER_AI

    @classmethod
    def tearDownClass(cls):
        cls.engine.close()
        cls.temp_dir.cleanup()

    def test_01_example1_natural_language_zelda_totk(self):
        """Verifica Ejemplo 1: 'Quiero encontrar todos los trucos de Zelda Tears of the Kingdom para Nintendo Switch'."""
        query = "Quiero encontrar todos los trucos de Zelda Tears of the Kingdom para Nintendo Switch"
        intent = self.ai.analyze_query(query)

        self.assertEqual(intent.detected_game, "The Legend of Zelda: Tears of the Kingdom")
        self.assertEqual(intent.detected_platform, "Nintendo Switch")
        self.assertEqual(intent.intent_type, "cheats")
        self.assertGreaterEqual(intent.confidence, 0.85)
        self.assertTrue(any("GameFAQs" in s for s in intent.recommended_sources))
        self.assertFalse(intent.is_suspicious)

    def test_02_example2_natural_language_elden_ring_communities(self):
        """Verifica Ejemplo 2: 'Quiero encontrar comunidades de jugadores de Elden Ring que compartan builds y secretos'."""
        query = "Quiero encontrar comunidades de jugadores de Elden Ring que compartan builds y secretos"
        intent = self.ai.analyze_query(query)

        self.assertEqual(intent.detected_game, "Elden Ring")
        self.assertEqual(intent.intent_type, "communities")
        self.assertGreaterEqual(intent.confidence, 0.8)
        self.assertTrue(any("Reddit" in s or "Discord" in s for s in intent.recommended_sources))

    def test_03_acronym_and_slang_disambiguation(self):
        """Verifica la desambiguación de acrónimos típicos del mundo gamer (totk, botw, gow, fh5, sm64)."""
        # "totk duplicacion"
        intent_totk = self.ai.analyze_query("totk duplicacion")
        self.assertEqual(intent_totk.detected_game, "The Legend of Zelda: Tears of the Kingdom")
        self.assertEqual(intent_totk.intent_type, "cheats")

        # "gow ragnarok platino ps5"
        intent_gow = self.ai.analyze_query("gow ragnarok platino ps5")
        self.assertEqual(intent_gow.detected_game, "God of War Ragnarök")
        self.assertEqual(intent_gow.detected_platform, "PlayStation 5")
        self.assertEqual(intent_gow.intent_type, "cheats")

        # "fh5 carreras xbox series"
        intent_fh5 = self.ai.analyze_query("fh5 carreras xbox series")
        self.assertEqual(intent_fh5.detected_game, "Forza Horizon 5")
        self.assertEqual(intent_fh5.detected_platform, "Xbox Series X/S")

        # "sm64 blj glitch"
        intent_sm64 = self.ai.analyze_query("sm64 blj glitch")
        self.assertEqual(intent_sm64.detected_game, "Super Mario 64")
        self.assertEqual(intent_sm64.intent_type, "cheats")

    def test_04_preservation_and_emulator_intent(self):
        """Verifica la detección de intención de preservación y emuladores."""
        intent_emu = self.ai.analyze_query("como configurar emulador dolphin para gamecube")
        self.assertEqual(intent_emu.detected_platform, "Nintendo GameCube")
        self.assertEqual(intent_emu.intent_type, "preservation")
        self.assertTrue(any("GitHub" in s or "Archive" in s for s in intent_emu.recommended_sources))

    def test_05_anti_malware_and_piracy_detection(self):
        """Verifica la detección de patrones de malware, keygens y descargas piratas engañosas."""
        # Intento de descarga ilegal / falsa
        intent_piracy = self.ai.analyze_query("descargar gratis rom nsp switch zelda")
        self.assertTrue(intent_piracy.is_suspicious)
        self.assertIsNotNone(intent_piracy.suspicious_reason)

        # Keygen / crack
        intent_crack = self.ai.analyze_query("keygen.exe crack bypass drm")
        self.assertTrue(intent_crack.is_suspicious)
        self.assertIn("malware", intent_crack.suspicious_reason.lower())

        # Consulta legítima limpia
        intent_clean = self.ai.analyze_query("emulador pcsx2 playstation 2 codigo abierto")
        self.assertFalse(intent_clean.is_suspicious)

    def test_06_smart_search_execution_and_priority_routing(self):
        """Verifica que execute_smart_search enrute a la sección prioritaria y entregue resultados organizados."""
        # Consulta de comunidades: debe dar prioridad a communities
        res_comm = self.ai.execute_smart_search(
            raw_query="comunidades de jugadores de Elden Ring",
            engine_db=self.engine
        )
        self.assertEqual(res_comm["priority_section"], "communities")
        self.assertGreater(len(res_comm["communities"]), 0)
        self.assertEqual(res_comm["communities"][0]["id"], "comm-r-eldenring")

        # Consulta de trucos: debe dar prioridad a cheats
        res_cheats = self.ai.execute_smart_search(
            raw_query="trucos y secretos de zelda tears of the kingdom",
            engine_db=self.engine
        )
        self.assertEqual(res_cheats["priority_section"], "cheats")
        self.assertGreater(len(res_cheats["cheats"]), 0)


if __name__ == "__main__":
    unittest.main()
