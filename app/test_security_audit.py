"""
Suite de Certificación y Auditoría de Seguridad / Calidad IR v2.0 - SamuBusquedas (.onion)
==========================================================================================
Autor de la Suite: Lead Security & Search Quality Auditor + Lead Cybersecurity Engineer
Arquitecto del Proyecto: saghet

Certifica los 3 Bloques de la Matriz de Auditoría:
- Bloque A (IR-01 a IR-07): Ranking BM25F + OnionTrustRank, Operadores (`cat:`, `js:safest`, `-excluir`,
  `"frase exacta"`, `!Bangs`), Corrector Ortográfico Levenshtein y Snippets Resaltados (`<mark class="hl">`).
- Bloque B (SEC-01 a SEC-05): Fuzzing agresivo de FTS5, SQL Injection, XSS en Snippets y Parámetros,
  Query Bomb (10,000 chars), Anti-SSRF SOCKS5h y Cabeceras Cross-Origin / Anti-Clock-Skew.
- Bloque C (SAG-01 a SAG-04): Verificación de Metadatos y Reconocimiento Hacker para `saghet` en
  `/humans.txt`, `/.well-known/security.txt` (RFC 9116), `<meta name="author" content="saghet">`,
  Banner ASCII Art, Cabeceras HTTP (`X-Architected-By: saghet`) y Knowledge Card sin fugas de OPSEC.
"""

import json
import threading
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer

from database import SamuSearchEngine, is_valid_v3_onion
from main import SamuOnionRequestHandler
from security_shield import evaluate_client_connection_security
from verifier import audit_catalog_integrity, probe_onion_via_socks5h


class TestSamuBusquedasV2CertificationSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from pathlib import Path
        cls._cm_path = Path(__file__).resolve().parent / "collective_memory.json"
        cls._cm_backup = cls._cm_path.read_text(encoding="utf-8") if cls._cm_path.exists() else None
        cls.engine = SamuSearchEngine()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), SamuOnionRequestHandler)
        cls.port = cls.server.server_port
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        if getattr(cls, "_cm_backup", None) is not None:
            cls._cm_path.write_text(cls._cm_backup, encoding="utf-8")

    # =========================================================================
    # BLOQUE A: PRUEBAS DE CALIDAD DE BÚSQUEDA Y RECUPERACIÓN DE INFORMACIÓN (IR)
    # =========================================================================

    def test_IR01_bm25f_and_samurank_top1_precision(self) -> None:
        """[IR-01] Verifica que el ranking híbrido SamuRank (BM25F + SHA3-256 Trust) posicione #1 el servicio exacto."""
        res_debian = self.engine.search_v2(query="Debian")["results"]
        self.assertGreaterEqual(len(res_debian), 1)
        self.assertIn("Debian", str(res_debian[0]["title"]))

        res_defcon = self.engine.search_v2(query="DEF CON")["results"]
        self.assertGreaterEqual(len(res_defcon), 1)
        self.assertIn("DEF CON", str(res_defcon[0]["title"]))

    def test_IR02_category_and_yahoo_taxonomy_operators(self) -> None:
        """[IR-02] Verifica soporte de operadores cat: y tax: al estilo Google / Yahoo! Directory."""
        res_cat = self.engine.search_v2(query="cat:prensa")["results"]
        self.assertGreaterEqual(len(res_cat), 4)
        for item in res_cat:
            self.assertIn("Prensa", str(item["category"]))

        res_tax = self.engine.search_v2(query="tax:lib/books", enable_live_tor=False)["results"]
        self.assertGreaterEqual(len(res_tax), 4)
        self.assertTrue(any("Trantor" in str(r["title"]) for r in res_tax))

    def test_IR03_js_safest_operator_filtering(self) -> None:
        """[IR-03] Verifica que el operador `correo js:safest` devuelva Riseup/Systemli pero excluya Proton Mail (Standard JS)."""
        res = self.engine.search_v2(query="correo js:safest", enable_live_tor=False)["results"]
        titles = [str(r["title"]) for r in res]
        self.assertTrue(any("Riseup" in t for t in titles))
        self.assertFalse(any("Proton Mail" in t for t in titles))

    def test_IR04_boolean_exclusion_operator(self) -> None:
        """[IR-04] Verifica que el operador de exclusión `-duckduckgo` elimine ese resultado sin afectar los demás buscadores."""
        res = self.engine.search_v2(query="buscador -duckduckgo", enable_live_tor=False)["results"]
        titles = [str(r["title"]) for r in res]
        self.assertTrue(any("Brave" in t or "Ahmia" in t for t in titles))
        self.assertFalse(any("DuckDuckGo" in t for t in titles))

    def test_IR05_exact_phrase_and_accent_insensitive_matching(self) -> None:
        """[IR-05] Verifica la coincidencia de frase exacta con y sin tildes ('investigación' == 'investigacion')."""
        res_with_accent = self.engine.search_v2(query='"periodismo de investigación"', enable_live_tor=False)["results"]
        res_no_accent = self.engine.search_v2(query='"periodismo de investigacion"', enable_live_tor=False)["results"]
        self.assertGreaterEqual(len(res_with_accent), 1)
        self.assertEqual(res_with_accent[0]["id"], res_no_accent[0]["id"])
        self.assertIn("ProPublica", str(res_no_accent[0]["title"]))

    def test_IR06_spell_correction_and_auto_recovery(self) -> None:
        """[IR-06] Verifica que el corrector ortográfico Damerau-Levenshtein sugiera y recupere resultados automáticamente."""
        payload_1 = self.engine.search_v2(query="protnmail", enable_live_tor=False)
        self.assertEqual(payload_1["did_you_mean"], "protonmail")
        self.assertGreaterEqual(len(payload_1["results"]), 1)
        self.assertEqual(payload_1["auto_corrected_from"], "protnmail")

        payload_2 = self.engine.search_v2(query="whonx", enable_live_tor=False)
        self.assertEqual(payload_2["did_you_mean"], "whonix")
        self.assertGreaterEqual(len(payload_2["results"]), 1)

        payload_3 = self.engine.search_v2(query="debain", enable_live_tor=False)
        self.assertEqual(payload_3["did_you_mean"], "debian")
        self.assertGreaterEqual(len(payload_3["results"]), 1)

    def test_IR07_highlighted_snippets_bangs_and_amplified_unverified_surface(self) -> None:
        """[IR-07] Verifica resaltado (<mark class="hl">), !Bangs y que cualquier consulta (foros, cripto, libre) devuelva resultados."""
        payload = self.engine.search_v2(query="whistleblowers", enable_live_tor=False)
        results = payload["results"]
        self.assertGreaterEqual(len(results), 1)
        self.assertIn('<mark class="hl">', str(results[0]["highlighted_desc"]))

        # Consultas variadas sobre sitios no verificados y comunitarios (foros, wiki, monero, pastebin)
        for q_term in ["foros", "hidden wiki", "monero", "bitcoin", "scihub", "pastebin", "saghet", "cualquiercosaenladeepweb"]:
            p_res = self.engine.search_v2(query=q_term, enable_live_tor=True)["results"]
            self.assertGreaterEqual(len(p_res), 1, f"La consulta '{q_term}' devolvió 0 resultados")

        bang_payload = self.engine.search_v2(query="!ddg privacidad", enable_live_tor=False)
        self.assertIsNotNone(bang_payload["bang_info"])
        self.assertIn("duckduckgo", str(bang_payload["bang_info"]["url"]))

    def test_IR08_no_nonsense_spellcheck_and_semantic_deepweb_routing(self) -> None:
        """
        [IR-08] Verifica que buscar 'armas', 'mercados', 'drogas', 'exploits' u 'ovnis' JAMÁS se auto-corrija a
        palabras sin sentido como 'mas', sino que active el Clasificador Semántico de Intención Deep Web + Live Tor.
        """
        payload_armas = self.engine.search_v2(query="armas", enable_live_tor=True)
        self.assertIsNone(payload_armas["did_you_mean"], "ERROR: 'armas' no debe sugerir 'mas' ni otra palabra")
        self.assertIsNone(payload_armas["auto_corrected_from"], "ERROR: 'armas' no debe auto-corregirse")
        self.assertIsNotNone(payload_armas["semantic_intent"])
        self.assertEqual(payload_armas["semantic_intent"]["id"], "conflict_osint_military")

        titles = [str(r["title"]) for r in payload_armas["results"]]
        self.assertTrue(any("Bellingcat" in t or "CIA" in t or "SecureDrop" in t for t in titles))
        # Ningún snippet debe resaltar 'mas' dentro de 'idiomas' o 'Masivo'
        for r in payload_armas["results"]:
            hl_desc = str(r.get("highlighted_desc", ""))
            self.assertNotIn('idio<mark class="hl">mas</mark>', hl_desc)
            self.assertNotIn('<mark class="hl">Mas</mark>ivo', hl_desc)

        for intent_q in ["mercados", "drogas", "exploits", "ovnis", "anonimato"]:
            p = self.engine.search_v2(query=intent_q, enable_live_tor=False)
            self.assertIsNone(p["did_you_mean"], f"'{intent_q}' fue corregido erróneamente a {p['did_you_mean']}")
            self.assertIsNotNone(p["semantic_intent"], f"'{intent_q}' debe activar intención semántica Deep Web")
            self.assertGreaterEqual(len(p["results"]), 4)

    def test_IR09_word_boundary_snippet_highlighting(self) -> None:
        """[IR-09] Verifica que highlight_safe_snippet respete límites de palabra (\b) y nunca parta palabras a la mitad."""
        from database import highlight_safe_snippet

        sample = "Cobertura en más de 40 idiomas con índice Masivo sobre armas y armamento."
        # Si el token es 'armas', solo debe resaltar 'armas', jamás 'idiomas' ni 'Masivo'
        hl_armas = highlight_safe_snippet(sample, ["armas"])
        self.assertIn('<mark class="hl">armas</mark>', hl_armas)
        self.assertNotIn('idio<mark class="hl">', hl_armas)
        self.assertNotIn('<mark class="hl">Mas', hl_armas)

    def test_IR10_zero_synthetic_onions_and_online_verification_on_all_searches(self) -> None:
        """[IR-10] Verifica cero direcciones sintéticas ('...aaa...') y que cada resultado esté verificado como ONLINE."""
        import re

        all_svcs = self.engine.search_v2(query="", enable_live_tor=False)["results"]
        self.assertGreaterEqual(len(all_svcs), 112)
        for svc in all_svcs:
            u = str(svc["onion_url"])
            self.assertTrue(is_valid_v3_onion(u), f"URL inválida: {u}")
            self.assertIsNone(
                re.search(r"https?://[a-z]{4,6}aa[a-z2-7]{48}\.onion", u),
                f"Detectada URL sintética prohibida: {u}",
            )
            self.assertTrue(svc.get("online_verified"), f"Servicio no marcado online: {svc['id']}")
            self.assertGreater(int(svc.get("latency_ms", 0)), 0)

        # Verificar también en consultas con live Tor habilitado
        for q_test in ["monero", "armas", "foros", "terminus_raro_xyz"]:
            res = self.engine.search_v2(query=q_test, enable_live_tor=True)["results"]
            self.assertGreaterEqual(len(res), 1)
            for item in res:
                u = str(item["onion_url"])
                self.assertTrue(is_valid_v3_onion(u), f"Resultado en vivo con URL inválida: {u}")
                self.assertIsNone(
                    re.search(r"https?://[a-z]{4,6}aa[a-z2-7]{48}\.onion", u),
                    f"Detectada URL sintética en vivo: {u}",
                )
                self.assertTrue(item.get("online_verified"))

    def test_IR11_version_1_99_4_top_left_and_online_badges_in_serp(self) -> None:
        """[IR-11] Verifica la versión v1.99.4 en la esquina superior izquierda y los badges [ONLINE EN TOR], [IA CALIDAD] y [MEMORIA COLECTIVA]."""
        from version import ENGINE_VERSION

        self.assertEqual(ENGINE_VERSION, "1.99.4")
        url = f"http://127.0.0.1:{self.port}/?q=monero"
        with urllib.request.urlopen(url) as resp:
            self.assertEqual(resp.headers.get("X-Engine-Version"), ENGINE_VERSION)
            html_doc = resp.read().decode("utf-8")
            self.assertIn('class="version-corner-badge"', html_doc)
            self.assertIn(f">v{ENGINE_VERSION}</span>", html_doc)
            self.assertIn("ONLINE EN TOR", html_doc)
            self.assertIn("VÁLIDO ONLINE", html_doc)
            self.assertIn("IA CALIDAD:", html_doc)

    def test_IR12_collective_search_memory_persistence_and_auto_indexing(self) -> None:
        """[IR-12] Verifica que búsquedas exitosas se guarden en Memoria Colectiva y sirvan al instante a otros usuarios."""
        from collective_memory import COLLECTIVE_MEMORY

        # Usuario 1 busca 'bibliotecas ciencia'
        res_user1 = self.engine.search_v2(query="bibliotecas ciencia", enable_live_tor=False)
        self.assertGreaterEqual(len(res_user1["results"]), 3)

        # Usuario 2 busca 'Bibliótecas Ciencia' (con tilde y mayúsculas) -> Hit instantáneo en Memoria Colectiva
        res_user2 = self.engine.search_v2(query="Bibliótecas Ciencia", enable_live_tor=False)
        self.assertTrue(res_user2.get("collective_memory_hit"))
        self.assertGreaterEqual(int(res_user2.get("collective_hits", 0)), 2)
        self.assertTrue(any(r.get("collective_memory") for r in res_user2["results"]))

        # Verificar que una consulta con datos sensibles (email) sea rechazada por higiene OPSEC
        sec_check = COLLECTIVE_MEMORY.record_successful_search("usuario@secreto.com", res_user1["results"])
        self.assertEqual(sec_check["saved_results"], 0)

    def test_IR13_bilingual_tor_query_expansion(self) -> None:
        """[IR-13] Verifica que el expansor bilingüe ES <-> EN traduzca consultas en español al vocabulario Tor en inglés."""
        from live_tor_search import expand_bilingual_tor_queries

        exp_bib = expand_bilingual_tor_queries("bibliotecas")
        self.assertEqual(len(exp_bib), 2)
        self.assertIn("library", exp_bib[1])

        exp_cripto = expand_bilingual_tor_queries("billetera cripto")
        self.assertEqual(len(exp_cripto), 2)
        self.assertIn("wallet", exp_cripto[1])

    def test_IR14_continuous_snowball_surface_growth_on_each_search(self) -> None:
        """[IR-14] Certifica que cada búsqueda nueva (incluso de términos repetidos) amplíe el índice FTS5 con nuevos nodos .onion."""
        surface_0 = self.engine.get_total_indexed_count()

        # Búsqueda 1: 'debian' -> descubre e indexa nuevos nodos .onion v3
        res_1 = self.engine.search_v2(query="debian", enable_live_tor=True)
        surface_1 = self.engine.get_total_indexed_count()
        self.assertGreater(surface_1, surface_0, "La primera búsqueda debía incrementar el total de nodos indexados")
        self.assertGreaterEqual(int(res_1.get("newly_indexed_count", 0)), 1)

        # Búsqueda 2: 'securedrop' -> vuelve a incrementar el índice con más nodos .onion v3
        res_2 = self.engine.search_v2(query="securedrop", enable_live_tor=True)
        surface_2 = self.engine.get_total_indexed_count()
        self.assertGreater(surface_2, surface_1, "La segunda búsqueda debía incrementar aún más el índice")
        self.assertGreaterEqual(int(res_2.get("newly_indexed_count", 0)), 1)

        # Búsqueda 3 (mismo término 'debian' por un segundo usuario) -> salta los ya conocidos e indexa la siguiente oleada
        res_3 = self.engine.search_v2(query="debian", enable_live_tor=True)
        surface_3 = self.engine.get_total_indexed_count()
        self.assertGreater(surface_3, surface_2, "Una búsqueda repetida debe seguir ampliando la superficie con nodos inéditos")
        self.assertGreaterEqual(int(res_3.get("newly_indexed_count", 0)), 1)

    def test_IR15_compound_query_precision_and_anti_scam_shield(self) -> None:
        """[IR-15] Certifica que búsquedas compuestas ('gustavo petro', 'expresidente gustavo petro') devuelvan 100% resultados relevantes sin servidores inconexos ni spam/carding."""
        forbidden_irrelevant_or_scam = (
            "grafana2.torproject.org",
            "ircbouncer.torproject.org",
            "live credit card",
            "darkvaultx",
            "drugrush",
            "cocaine",
            "fentanyl",
            "debconf4",
            "website hack service",
        )
        for compound_q in ("gustavo petro", "expresidente gustavo petro"):
            res = self.engine.search_v2(query=compound_q, enable_live_tor=True)["results"]
            self.assertGreaterEqual(len(res), 6)
            for item in res:
                combined = f"{item['title']} {item['description']}".lower()
                for bad in forbidden_irrelevant_or_scam:
                    self.assertNotIn(bad, combined, f"Resultado contaminado o inconexo '{bad}' en consulta '{compound_q}'")
                self.assertIn("gustavo", combined, f"El resultado '{item['title']}' no menciona 'gustavo'")
                self.assertIn("petro", combined, f"El resultado '{item['title']}' no menciona 'petro'")
                self.assertTrue(is_valid_v3_onion(str(item["onion_url"])))
                self.assertTrue(item.get("online_verified"))

    def test_IR16_realtime_twitter_trends_and_ai_anti_garbage_filter(self) -> None:
        """[IR-16] Certifica el Radar en Tiempo Real de Twitter/X -> Deep Web y el Motor IA Anti-Basura (SamuAIAntiGarbageEngine)."""
        from realtime_trends_ai import SAMU_AI_ENGINE, TWITTER_TREND_WATCHER

        # 1. Evaluar clasificador IA de tendencias de Twitter/X
        valid_trend = SAMU_AI_ENGINE.evaluate_trend_quality("#GustavoPetro", "Colombia")
        self.assertTrue(valid_trend["is_valid"])
        self.assertEqual(valid_trend["query"], "gustavo petro")
        self.assertGreaterEqual(float(valid_trend["ai_score"]), 85.0)

        garbage_trend_1 = SAMU_AI_ENGINE.evaluate_trend_quality("#SorteoGratisBuenJueves", "Global")
        self.assertFalse(garbage_trend_1["is_valid"])
        garbage_trend_2 = SAMU_AI_ENGINE.evaluate_trend_quality("Shakira", "Colombia")
        self.assertFalse(garbage_trend_2["is_valid"])

        # 2. Evaluar filtro IA Anti-Basura sobre resultados de Deep Web
        scam_item = {
            "title": "DarkVaultX Live Credit Card Dumps & Cloned Cards",
            "description": "Buy 10x Bitcoin Multiplier and Western Union Hack",
            "onion_url": "http://2gzyxa5ihm7nsggfxnu52rck2vv4rvmdlkiu3zzui5du4xyclen53wid.onion",
            "verification_tier": "UNVERIFIED",
        }
        scam_eval = SAMU_AI_ENGINE.evaluate_search_result_ai("gustavo petro", scam_item)
        self.assertTrue(scam_eval["is_garbage"])
        self.assertLess(float(scam_eval["ai_quality_score"]), 25.0)

        legit_item = {
            "title": "ProPublica Whistleblower — Investigación sobre Gustavo Petro",
            "description": "Archivo periodístico cifrado en Tor sobre Gustavo Petro y América Latina.",
            "onion_url": "http://p53lf57qovyuvwsc6xnrppyply3vtqm7l6pcobkmyqsiofyeznfu5uqd.onion",
            "verification_tier": "VERIFIED",
            "safety_score": 98,
        }
        legit_eval = SAMU_AI_ENGINE.evaluate_search_result_ai("gustavo petro", legit_item)
        self.assertFalse(legit_eval["is_garbage"])
        self.assertGreaterEqual(float(legit_eval["ai_quality_score"]), 85.0)

        # 3. Verificar que el Watcher de Twitter/X tenga tendencias activas y que /api/trends y la portada funcionen
        active_trends = TWITTER_TREND_WATCHER.get_active_trends(limit=8)
        self.assertGreaterEqual(len(active_trends), 5)

        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/api/trends") as resp:
            self.assertEqual(resp.status, 200)
            trends_json = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(trends_json["version"], "1.99.4")
            self.assertGreaterEqual(len(trends_json["trends"]), 5)

        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/") as resp:
            home_html = resp.read().decode("utf-8")
            self.assertIn("Lo Más Buscado en Twitter/X (Tiempo Real)", home_html)
            self.assertIn("Pre-Indexado en Deep Web con IA Anti-Basura", home_html)

    # =========================================================================
    # BLOQUE B: PRUEBAS DE RESISTENCIA A ATAQUES, FUZZING Y CIBERSEGURIDAD
    # =========================================================================

    def test_SEC01_fts5_syntax_fuzzing_and_sql_injection(self) -> None:
        """[SEC-01 & SEC-02] Verifica que payloads maliciosos FTS5 y SQL Injection no provoquen sqlite3.OperationalError."""
        malicious_queries = [
            '^"()*+:-OR AND NOT NEAR/1 "unclosed',
            "'''\"\"\"***((())):::^^^",
            "NEAR(tor, 5) OR *",
            "tor'; DROP TABLE services; --",
            "cat:Todas' UNION SELECT 1,2,3,4,5,6,7,8,9,10,11,12,13--",
        ]
        for mq in malicious_queries:
            res = self.engine.search_v2(query=mq, enable_live_tor=False)
            self.assertIn("results", res)

        # Confirmar que los >= 112 servicios siguen intactos en RAM
        all_svcs = self.engine.search_v2(query="", enable_live_tor=False)["results"]
        self.assertGreaterEqual(len(all_svcs), 112)

    def test_SEC02_sha3_256_cryptographic_checksum_and_anti_phishing(self) -> None:
        """Verifica que las 112+ direcciones tengan checksum SHA3-256 válido y que se detecten clones y checksums falsos."""
        report = audit_catalog_integrity()
        self.assertGreaterEqual(len(report), 112)
        for item in report:
            self.assertEqual(item["status"], "APROBADO", f"Fallo SHA3-256 en {item['title']}")

        # 1. Dominio oficial de Tor Project (Checksum SHA3-256 real)
        official = "http://2gzyxa5ihm7nsggfxnu52rck2vv4rvmdlkiu3zzui5du4xyclen53wid.onion"
        self.assertEqual(self.engine.inspect_onion_url(official)["verdict"], "SAFE_VERIFIED")

        # 2. Clon de Phishing por prefijo Vanity ('2gzyx...')
        phishing_vanity = "http://2gzyxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaad.onion"
        self.assertEqual(self.engine.inspect_onion_url(phishing_vanity)["verdict"], "DANGER_PHISHING")

        # 3. Clon de Phishing por suplantación de marca incrustada ('protonmail...')
        phishing_brand = "http://protonmailaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaad.onion"
        self.assertEqual(self.engine.inspect_onion_url(phishing_brand)["verdict"], "DANGER_PHISHING")

        # 4. Dirección de 56 caracteres con checksum SHA3-256 corrupto
        corrupted_checksum = "http://zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzd.onion"
        self.assertEqual(self.engine.inspect_onion_url(corrupted_checksum)["verdict"], "INVALID_OR_V2")

    def test_SEC03_reflected_xss_and_query_bomb_defense(self) -> None:
        """[SEC-03 & SEC-04] Audita inmunidad contra XSS reflejado y bombas de consulta de 10,000 caracteres."""
        xss_q = urllib.parse.quote('<script>alert("xss")</script><img src=x onerror=alert(1)>')
        url = f"http://127.0.0.1:{self.port}/?q={xss_q}"
        with urllib.request.urlopen(url) as resp:
            body = resp.read().decode("utf-8")
            self.assertEqual(resp.status, 200)
            self.assertNotIn("<script>", body.lower())
            self.assertNotIn("<img src=x", body.lower())
            self.assertIn("&lt;script&gt;", body)

        # Query bomb de 10,000 caracteres
        t0 = time.perf_counter()
        bomb_res = self.engine.search_v2(query="A" * 10000, enable_live_tor=False)
        elapsed = (time.perf_counter() - t0) * 1000
        self.assertLess(elapsed, 80.0)
        self.assertLessEqual(len(str(bomb_res["parsed_query"]["raw"])), 256)

    def test_SEC04_socks5h_anti_ssrf_and_hardened_headers(self) -> None:
        """[SEC-05] Verifica que el conector SOCKS5h bloquee SSRF hacia IPs locales/Clearnet y audita cabeceras HTTP."""
        ssrf_1 = probe_onion_via_socks5h("http://127.0.0.1:8080/admin")
        self.assertFalse(ssrf_1["ok"])
        self.assertIn("Anti-SSRF", str(ssrf_1["reason"]))

        ssrf_2 = probe_onion_via_socks5h("http://169.254.169.254/latest/meta-data/")
        self.assertFalse(ssrf_2["ok"])

        url = f"http://127.0.0.1:{self.port}/"
        with urllib.request.urlopen(url) as resp:
            self.assertEqual(resp.headers.get("Referrer-Policy"), "no-referrer")
            self.assertEqual(resp.headers.get("Cross-Origin-Opener-Policy"), "same-origin")
            self.assertEqual(resp.headers.get("Cross-Origin-Resource-Policy"), "same-origin")
            self.assertEqual(resp.headers.get("Date"), "Thu, 01 Jan 1970 00:00:00 GMT")
            self.assertNotIn("Python", resp.headers.get("Server", ""))

    # =========================================================================
    # BLOQUE C: VERIFICACIÓN DE METADATOS Y RECONOCIMIENTO HACKER PARA `saghet`
    # =========================================================================

    def test_SAG01_to_SAG04_hacker_metadata_and_opsec_safety(self) -> None:
        """[SAG-01 a SAG-04] Certifica todos los metadatos de autoría para `saghet` sin fugas de rutas locales."""
        # 1. Verificar cabeceras HTTP, <meta> tags, Banner ASCII y Knowledge Card de `saghet`
        url_saghet = f"http://127.0.0.1:{self.port}/?q=saghet"
        with urllib.request.urlopen(url_saghet) as resp:
            self.assertEqual(resp.headers.get("X-Architected-By"), "saghet")
            self.assertEqual(resp.headers.get("X-Builder-Handle"), "saghet")
            html_doc = resp.read().decode("utf-8")
            self.assertIn('<meta name="author" content="saghet">', html_doc)
            self.assertIn("ARCHITECT   : saghet", html_doc)
            self.assertIn("KNOWLEDGE CARD DE AUTORÍA HACKER", html_doc)
            # Garantía OPSEC: Cero fugas de rutas de Windows/sistema local
            self.assertNotIn("C:\\Users", html_doc)
            self.assertNotIn("c:/Users", html_doc)

        # 2. Verificar /humans.txt
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/humans.txt") as resp:
            humans = resp.read().decode("utf-8")
            self.assertEqual(resp.status, 200)
            self.assertIn("Lead Architect & Security Researcher: saghet", humans)
            self.assertNotIn("C:\\Users", humans)

        # 3. Verificar /.well-known/security.txt (Estándar RFC 9116)
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/.well-known/security.txt") as resp:
            sec_txt = resp.read().decode("utf-8")
            self.assertEqual(resp.status, 200)
            self.assertIn("Acknowledgments: saghet", sec_txt)
            self.assertIn("Canonical:", sec_txt)
            self.assertIn("Expires:", sec_txt)


if __name__ == "__main__":
    unittest.main(verbosity=2)
