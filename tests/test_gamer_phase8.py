"""
Suite de Pruebas Unitarias - Fase 8: Panel de Transparencia SEARCH INTELLIGENCE en Tiempo Real
=============================================================================================
Verifica la generación, estructura de datos y renderizado del cockpit de telemetría:
- Motores y fuentes consultadas (éxito vs fallos)
- Errores de red transparentes
- Consultas generadas e idiomas
- Dominios descubiertos y catalogados
- Filtro de calidad (evaluados, aceptados, descartados con motivos)
- Tiempo de ejecución en ms
- Profundidad alcanzada y cobertura por plataforma
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from gamer_ai import GAMER_AI
from gamer_views import render_search_intelligence_panel, render_smart_search_results_view


class TestGamerPhase8SearchIntelligence(unittest.TestCase):

    def setUp(self):
        self.mock_intel = {
            "queried_providers": ["DuckDuckGo Web", "Wikipedia (ES/EN)", "Steam Community", "Reddit RSS", "Speedrun.com"],
            "successful_providers": ["Wikipedia (ES/EN)", "Steam Community", "Reddit RSS", "Speedrun.com"],
            "failed_providers": ["DuckDuckGo Web"],
            "errors": {"DuckDuckGo Web": "HTTP 403 Rate Limit Exceeded"},
            "elapsed_seconds": 1.45,
            "total_domains_discovered": 14,
            "generated_queries": [
                "GTA 5 hidden secrets",
                "GTA V cheat codes",
                "グランド・セフト・オートV 攻略"
            ],
            "live_suggestions": ["GTA V trucos ps5", "GTA V secretos helicoptero"],
            "new_domains_discovered": ["rockstargames.com", "gtaforums.com"],
            "total_catalog_domains": 18,
            "wave_2_executed": True,
            "wave_2_query": "GTA V guides walkthrough",
            "deep_links_discovered": 6,
            "total_evaluated": 12,
            "total_accepted": 10,
            "total_discarded_low_quality": 2,
            "discarded_items": [
                {
                    "title": "Hack GTA Free Money Generator No Survey",
                    "reason": "Puntaje de calidad insuficiente (18.0 < 35.0)",
                    "score": 18.0
                },
                {
                    "title": "SE RUMOREA MAPA 50X EN GTA 6 - IMPERDIBLE",
                    "reason": "Puntaje de calidad insuficiente (27.5 < 35.0)",
                    "score": 27.5
                }
            ],
            "languages_used": ["Español (ES)", "Inglés (EN)", "Japonés (JA)"],
            "platforms_covered": ["PC", "PS5", "PS4", "Xbox Series X/S"],
            "search_depth": "Profundidad 2 (Oleada 1 Federada + Oleada 2 Recursiva)"
        }

    def test_01_render_panel_basic_kpis(self):
        """Verifica que el panel renderice todos los KPIs esenciales."""
        html = render_search_intelligence_panel(self.mock_intel, elapsed_ms=1450.0)
        self.assertIn("Search Intelligence", html)
        self.assertIn("1450.0 ms", html)
        self.assertIn("Motores Consultados", html)
        self.assertIn("5", html)
        self.assertIn("(4 OK)", html)
        self.assertIn("Profundidad 2", html)
        self.assertIn("10", html)
        self.assertIn("2 descartados", html)

    def test_02_render_panel_network_errors_transparently(self):
        """Verifica que los errores de red se muestren sin ocultar la causa ni el proveedor."""
        html = render_search_intelligence_panel(self.mock_intel, elapsed_ms=1450.0)
        self.assertIn("DuckDuckGo Web", html)
        self.assertIn("HTTP 403 Rate Limit Exceeded", html)
        self.assertIn("Reporte de Conectividad de Red", html)

    def test_03_render_panel_discarded_items_reasons(self):
        """Verifica que los resultados descartados por baja calidad muestren título, score y razón."""
        html = render_search_intelligence_panel(self.mock_intel, elapsed_ms=1450.0)
        self.assertIn("Hack GTA Free Money Generator", html)
        self.assertIn("18.0", html)
        self.assertIn("SE RUMOREA MAPA 50X", html)
        self.assertIn("27.5", html)

    def test_04_render_panel_queries_and_languages(self):
        """Verifica que las consultas generadas y los idiomas procesados (ES, EN, JA) se rendericen."""
        html = render_search_intelligence_panel(self.mock_intel, elapsed_ms=1450.0)
        self.assertIn("GTA 5 hidden secrets", html)
        self.assertIn("グランド・セフト・オートV", html)
        self.assertIn("Español (ES)", html)
        self.assertIn("Inglés (EN)", html)
        self.assertIn("Japonés (JA)", html)

    def test_05_smart_results_view_includes_intelligence_panel(self):
        """Verifica que la vista principal de resultados incluya el panel Search Intelligence."""
        smart_res = {
            "query": "GTA V",
            "intent": {"confidence": 0.95, "natural_language_summary": "Búsqueda canónica de GTA V"},
            "elapsed_ms": 120.0,
            "total_hits": 5,
            "counts": {"games": 2, "cheats": 2, "preservation": 0, "communities": 1},
            "games": [],
            "cheats": [],
            "preservation": [],
            "communities": [],
            "search_intelligence": self.mock_intel
        }
        view_html = render_smart_search_results_view("GTA V", smart_res)
        self.assertIn("Search Intelligence — Telemetría y Transparencia en Vivo", view_html)
        self.assertIn("Profundidad 2", view_html)


if __name__ == "__main__":
    unittest.main()
