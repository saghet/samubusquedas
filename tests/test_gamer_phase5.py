"""
Suite de Pruebas de Integración y UI - Fase 5: Rediseño UI/UX Gamer y Rutas HTTP
=================================================================================
Verifica el servidor HTTP en vivo, las 9 secciones independientes, las tarjetas visuales,
los filtros dinámicos, la hoja de estilos en tema oscuro y los endpoints API JSON.
"""

import json
import os
import sys
import threading
import time
import unittest
import urllib.request
from http.server import ThreadingHTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from main import SamuOnionRequestHandler


class TestGamerPhase5UIAndHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Levantar servidor en un puerto aleatorio efímero (puerto 0)
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), SamuOnionRequestHandler)
        cls.port = cls.server.server_port
        cls.base_url = f"http://127.0.0.1:{cls.port}"
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.15)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def _get(self, path: str):
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url, headers={"User-Agent": "TestGamerBrowser/1.0"})
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            return resp.status, resp.read().decode("utf-8"), dict(resp.headers)

    def test_01_static_css_and_dark_theme(self):
        """Verifica que /static/style.css se sirva en UTF-8 y contenga las variables del tema oscuro gamer."""
        status, css, headers = self._get("/static/style.css")
        self.assertEqual(status, 200)
        self.assertIn("--bg-dark", css)
        self.assertIn("--cyan-accent", css)
        self.assertIn("--purple-accent", css)
        self.assertIn("text/css", headers.get("Content-Type", ""))

    def test_02_home_view_and_navigation(self):
        """Verifica la portada con el buscador principal y las 9 secciones en la barra de navegación."""
        status, html_content, _ = self._get("/gamer")
        self.assertEqual(status, 200)
        self.assertIn("GAMER SEARCH ENGINE", html_content)
        self.assertIn("/juegos", html_content)
        self.assertIn("/trucos", html_content)
        self.assertIn("/preservacion", html_content)
        self.assertIn("/emuladores", html_content)
        self.assertIn("/comunidades", html_content)
        self.assertIn("/favoritos", html_content)

    def test_03_smart_search_unified_view(self):
        """Verifica la búsqueda inteligente unificada con tarjeta de análisis de IA."""
        status, html_content, _ = self._get("/gamer?q=Zelda+Tears+of+the+Kingdom")
        self.assertEqual(status, 200)
        self.assertIn("Inteligencia Semántica Gamer", html_content)
        self.assertIn("Tears of the Kingdom", html_content)
        self.assertIn("tab-juegos", html_content)
        self.assertIn("tab-trucos", html_content)
        self.assertIn("tab-comunidades", html_content)

    def test_04_games_section_with_filters(self):
        """Verifica la sección /juegos con filtros de plataforma y género."""
        status, html_content, _ = self._get("/juegos?platform=Nintendo+Switch&genre=Action-Adventure")
        self.assertEqual(status, 200)
        self.assertIn("Videojuegos", html_content)
        self.assertIn("Nintendo Switch", html_content)
        self.assertIn("Tears of the Kingdom", html_content)

    def test_05_cheats_section(self):
        """Verifica la sección /trucos con filtrado por categoría."""
        status, html_content, _ = self._get("/trucos?category=glitches")
        self.assertEqual(status, 200)
        self.assertIn("Buscador de Trucos", html_content)
        self.assertIn("Duplicación", html_content)

    def test_06_preservation_and_emulators_sections(self):
        """Verifica /preservacion y /emuladores mostrando emuladores oficiales y homebrew."""
        status_pres, html_pres, _ = self._get("/preservacion")
        self.assertEqual(status_pres, 200)
        self.assertIn("Preservación Digital", html_pres)

        status_emu, html_emu, _ = self._get("/emuladores")
        self.assertEqual(status_emu, 200)
        self.assertIn("Emuladores Oficiales", html_emu)
        self.assertIn("Dolphin", html_emu)
        self.assertIn("PCSX2", html_emu)

    def test_07_communities_section_priority(self):
        """Verifica la sección prioritaria /comunidades mostrando subreddits y Discord verificados."""
        status, html_content, _ = self._get("/comunidades")
        self.assertEqual(status, 200)
        self.assertIn("Buscador de Comunidades Gamer", html_content)
        self.assertIn("r/NintendoSwitch", html_content)
        self.assertIn("r/PS5", html_content)
        self.assertIn("r/XboxSeriesX", html_content)
        self.assertIn("Discord", html_content)

    def test_08_game_detail_view(self):
        """Verifica la ficha técnica /juego?id=zelda-totk con tabla de especificaciones."""
        status, html_content, _ = self._get("/juego?id=zelda-totk")
        self.assertEqual(status, 200)
        self.assertIn("The Legend of Zelda: Tears of the Kingdom", html_content)
        self.assertIn("Ficha Técnica", html_content)
        self.assertIn("Requisitos Técnicos", html_content)
        self.assertIn("18.2 GB", html_content)

    def test_09_favorites_and_history_section(self):
        """Verifica la sección /favoritos mostrando elementos guardados e historial."""
        status, html_content, _ = self._get("/favoritos")
        self.assertEqual(status, 200)
        self.assertIn("Favoritos e Historial", html_content)

    def test_10_api_endpoints_json(self):
        """Verifica los endpoints API JSON /api/search, /api/filters y /api/stats."""
        # /api/search
        status_s, body_s, _ = self._get("/api/search?q=Elden+Ring")
        self.assertEqual(status_s, 200)
        data_s = json.loads(body_s)
        self.assertIn("intent", data_s)
        self.assertIn("games", data_s)
        self.assertGreater(data_s["total_hits"], 0)

        # /api/filters
        status_f, body_f, _ = self._get("/api/filters")
        self.assertEqual(status_f, 200)
        data_f = json.loads(body_f)
        self.assertIn("platforms", data_f)
        self.assertIn("genres", data_f)

        # /api/stats
        status_st, body_st, _ = self._get("/api/stats")
        self.assertEqual(status_st, 200)
        data_st = json.loads(body_st)
        self.assertGreater(data_st["total_games"], 0)


if __name__ == "__main__":
    unittest.main()
