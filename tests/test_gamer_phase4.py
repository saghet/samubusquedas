"""
Suite de Pruebas Unitarias - Fase 4: OSINT, Conectores y Escudo de Ciberseguridad
================================================================================
Verifica el análisis de reputación de fuentes, detección de malware y falsas descargas,
arquitectura modular de conectores de fuentes abiertas y agregación concurrente.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from gamer_security import GAMER_SECURITY, GamerSecurityShield
from gamer_connectors import (
    BaseGamerProvider,
    OSINTAggregator,
    SpeedrunComProvider,
    InternetArchiveProvider,
    GitHubGamerProvider,
)


class MockGamerProvider(BaseGamerProvider):
    """Proveedor mock para verificar extensibilidad y agregación sin depender de red externa."""
    name = "mock_provider"
    source_label = "Fuente Mock Verificada"

    def search(self, query: str, limit: int = 5):
        return [{
            "id": "mock_1",
            "title": f"Resultado Mock para {query}",
            "category": "Prueba OSINT",
            "description": "Metadatos extraídos de fuente de prueba.",
            "source": self.source_label,
            "url": "https://archive.org/details/test_game",
            "security": GAMER_SECURITY.evaluate_url("https://archive.org/details/test_game").to_dict()
        }]


class TestGamerPhase4OSINTAndSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sec = GAMER_SECURITY
        cls.aggregator = OSINTAggregator(timeout_per_provider=1.0)

    def test_01_trusted_official_domains(self):
        """Verifica que dominios oficiales (Nintendo, PlayStation, Xbox, GitHub, Archive, Speedrun) tengan reputación >= 90."""
        trusted_urls = [
            "https://www.nintendo.com/games/",
            "https://www.playstation.com/es-es/ps5/",
            "https://www.xbox.com/es-ES/consoles/xbox-series-x",
            "https://github.com/libretro/RetroArch",
            "https://archive.org/details/internetarcade",
            "https://www.speedrun.com/sm64",
            "https://gamefaqs.gamespot.com/switch/",
            "https://pcsx2.net/downloads/"
        ]
        for url in trusted_urls:
            report = self.sec.evaluate_url(url)
            self.assertGreaterEqual(report.reputation_score, 90.0, f"Fallo de reputación en: {url}")
            self.assertEqual(report.safety_tier, "CONFIABLE_VERIFICADO")
            self.assertFalse(report.is_known_malicious)
            self.assertIn("https_cifrado_valido", report.flags)

    def test_02_suspicious_and_scam_domains(self):
        """Verifica la detección de dominios maliciosos, generadores de estafa y trampas piratas."""
        bad_urls = [
            "https://switchromsfree.com/download.php",
            "https://freerobuxgenerator.com/get-free",
            "https://downloadfreeisopc.com/installer.exe"
        ]
        for bad_url in bad_urls:
            report = self.sec.evaluate_url(bad_url)
            self.assertTrue(report.is_known_malicious, f"No detectado como malicioso: {bad_url}")
            self.assertEqual(report.safety_tier, "PELIGROSO_BLOQUEADO")
            self.assertLessEqual(report.reputation_score, 30.0)
            self.assertIn("dominio_malicioso_identificado", report.flags)

    def test_03_dangerous_executable_extensions_warning(self):
        """Verifica que enlaces con ejecutables (.exe, .scr, .bat) activen advertencias técnicas preventivas."""
        exe_url = "https://descargas-gamer-ejemplo.net/juego_setup.exe"
        report = self.sec.evaluate_url(exe_url)
        self.assertTrue(report.has_fake_download_traps)
        self.assertIn("archivo_ejecutable_peligroso_.exe", report.flags)
        self.assertIn("ADVERTENCIA DE SEGURIDAD", report.warning_message)
        self.assertLessEqual(report.reputation_score, 40.0)

    def test_04_safe_preservation_patch_formats(self):
        """Verifica el reconocimiento de formatos legítimos de parches (IPS, BPS, UPS, Z64)."""
        safe_patch_url = "https://mother3.fobby.net/mother3_v1.3_translation.ups"
        report = self.sec.evaluate_url(safe_patch_url)
        self.assertFalse(report.has_fake_download_traps)
        self.assertIn("formato_preservacion_seguro_.ups", report.flags)

    def test_05_modular_provider_registration(self):
        """Verifica la arquitectura modular permitiendo incorporar nuevos proveedores sin tocar el núcleo."""
        custom_aggregator = OSINTAggregator(timeout_per_provider=0.5)
        mock_prov = MockGamerProvider()
        custom_aggregator.register_provider(mock_prov)

        self.assertIn(mock_prov, custom_aggregator.providers)
        res = custom_aggregator.search_all("Super Mario", limit_per_provider=2)
        self.assertGreater(res["total"], 0)
        self.assertTrue(any("Resultado Mock" in r["title"] for r in res["results"]))

    def test_06_insecure_http_penalty(self):
        """Verifica penalización de reputación y flag de advertencia en sitios sin HTTPS."""
        http_url = "http://foro-gamer-retro-antiguo.org/temas"
        report = self.sec.evaluate_url(http_url)
        self.assertIn("http_inseguro_sin_cifrar", report.flags)
        self.assertLess(report.reputation_score, 80.0)


if __name__ == "__main__":
    unittest.main()
