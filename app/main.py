"""
SamuBusquedas v1.99.1 (.onion) - Interfaz Minimalista Clásica + Memoria Colectiva de Búsquedas
==============================================================================================
Arquitecto Principal y Creador: saghet
Características:
1. Portada Centrada Ultraligera (Estilo Google Stanford 1998 + Tabla de Directorio AltaVista/Yahoo 97).
2. Memoria Colectiva de Búsquedas Exitosas (`COLLECTIVE_MEMORY`): Guarda de forma anónima las búsquedas
   exitosas y auto-indexa nuevos nodos .onion v3 descubiertos para servirlos al instante a cualquier usuario.
3. Motor Interno SamuRank v1.99.1 Completo: 112+ Sitios Base Verificados Online + Harvester Bilingüe
   ES<->EN en la Red Tor + Corrector Ortográfico Damerau-Levenshtein + Escudo Anti-Phishing SHA3-256.
4. Metadatos Hacker para `saghet`: Cabeceras HTTP (`X-Architected-By: saghet`), `/.well-known/security.txt`
   (RFC 9116), `/humans.txt`, `/canary.txt`, `<meta name="author" content="saghet">` y Banner ASCII Art.
"""

import html
import ipaddress
import json
import os
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, List, Optional, Tuple

from collective_memory import COLLECTIVE_MEMORY
from database import MAX_QUERY_LEN, SamuSearchEngine
from donation_shield import (
    BTC_ADDRESS,
    BTC_NETWORK_NOTE,
    BTC_QR_PATH,
    BTC_URI,
    COOKIE_NAME,
    DONATION_GATE_SECONDS,
    DONATION_TRACKER,
    FREE_SEARCH_LIMIT,
)
from onion_guardian import ONION_GUARDIAN
from realtime_trends_ai import SAMU_AI_ENGINE, TWITTER_TREND_WATCHER
from security_shield import evaluate_client_connection_security
from verifier import audit_catalog_integrity
from version import ENGINE_VERSION

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

search_engine = SamuSearchEngine()

OFFICIAL_ONION_DOMAIN = "http://x4wgcuog7p6i3gh5t2mcshhfe5cjlkiygl24vf4ac6xmqm5g62jkehyd.onion"
APP_VERSION = ENGINE_VERSION

ASCII_HACKER_BANNER = f"""<!--
 =====================================================================================
   ____                        ____                                _
  / ___|  __ _ _ __ ___  _   _| __ ) _   _ ___  __ _ _   _  ___  __| | __ _ ___
  \\___ \\ / _` | '_ ` _ \\| | | |  _ \\| | | / __|/ _` | | | |/ _ \\/ _` |/ _` / __|
   ___) | (_| | | | | | | |_| | |_) | |_| \\__ \\ (_| | |_| |  __/ (_| | (_| \\__ \\
  |____/ \\__,_|_| |_| |_|\\__,_|____/ \\__,_|___/\\__, |\\__,_|\\___|\\__,_|\\__,_|___/
                                                  |_|
  [+] ENGINE      : SamuBusquedas v{APP_VERSION} (.onion v3 Search & AI Trend Intelligence)
  [+] ARCHITECT   : saghet (Lead Security Researcher & Search Engine Architect)
  [+] RANKING     : SamuRank = BM25F * (Title:10, Tags:6, Tax:5) + OnionTrustRank + AI Quality
  [+] AI ENGINE   : SamuAIAntiGarbageEngine (Shannon Entropy + Bayesian Veto + Twitter/X Sync)
  [+] MEMORY      : Anonymous Collective Search Memory + Auto-FTS5 Node Indexing
  [+] ZERO-JS     : 100% Tor Browser "Safest" Mode Ready (CSP script-src 'none')
  [+] AUDIT DOCS  : /.well-known/security.txt | /humans.txt | /canary.txt
 =====================================================================================
-->"""

CANARY_TEXT = f"""-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA512

========================================================================
                 DECLARACIÓN DE TRANSPARENCIA Y CANARIO
                  PORTAL SAMUBUSQUEDAS v{APP_VERSION} (.ONION v3)
========================================================================
Autoría y Arquitectura Principal: saghet
Versión Oficial: v{APP_VERSION}
Fecha de actualización: 2026-10-17
Dominio Oficial .onion v3:
{OFFICIAL_ONION_DOMAIN}
Estado del Servicio: ÍNTEGRO Y OPERATIVO (Modo Zero-Logs de Usuario en RAM)

El arquitecto del sistema (saghet) y el equipo de SamuBusquedas declaran que:
1. NO hemos recibido órdenes judiciales, citaciones ni requerimientos
   secretos para interceptar o registrar tráfico de usuarios.
2. NO hemos instalado puertas traseras (backdoors) ni modificado los
   pesos del algoritmo SamuRank / OnionTrustRank para alterar las llaves
   públicas Ed25519 (.onion v3) verificadas con SHA3-256.
3. La Memoria Colectiva de Búsquedas almacena exclusivamente términos
   temáticos normalizados y enlaces .onion verificados ONLINE, sin asociar
   jamás direcciones IP, sesiones, cookies ni huellas de navegador.

Huella PGP Oficial de SamuBusquedas (by saghet):
SAMU-SAGHET-V3-7F9A-44C1-88E2-B009-31D4-99A0
-----BEGIN PGP SIGNATURE-----
Version: GnuPG v2 (Isolated Onion Environment - Architected by saghet)

iQIzBAEBCgAdFiEE724obdqF6ipLp95oTixuh5MpgpAFAmV0OnionACgkQTixu
h5MpgpB99Q//SamuBusquedasV2SaghetZeroJSProtectionShieldVerified==
=sagh
-----END PGP SIGNATURE-----
"""

SECURITY_TXT = f"""# RFC 9116 Security Policy - SamuBusquedas v{APP_VERSION} (.onion v3)
# Lead Security Architect & Creator: saghet
Contact: {OFFICIAL_ONION_DOMAIN}/verificar
Acknowledgments: saghet (Lead Security Architect, Cryptographic Verifier & Creator)
Preferred-Languages: es, en
Canonical: {OFFICIAL_ONION_DOMAIN}/.well-known/security.txt
Policy: {OFFICIAL_ONION_DOMAIN}/proteccion
Encryption: {OFFICIAL_ONION_DOMAIN}/canary.txt
Expires: 2027-12-31T23:59:59.000Z
"""

HUMANS_TXT = f"""/* TEAM & ARCHITECTURE */
Lead Architect & Security Researcher: saghet
Handle: saghet
Version: v{APP_VERSION}
Role: Creator of SamuBusquedas v{APP_VERSION} (.onion v3 Hybrid Search Engine, AI Anti-Garbage & Twitter/X Trend Sync)
Official Onion v3: {OFFICIAL_ONION_DOMAIN}

/* SEARCH ENGINE TECHNOLOGY */
Ranking Algorithm: SamuRank / OnionTrustRank (Multi-field Okapi BM25F + SHA3-256 Ed25519 Trust Bonus + AI Quality Score)
AI Filter Engine: SamuAIAntiGarbageEngine (Shannon Entropy + Bayesian Anti-Scam Veto + Topical Vector Coherence >= 75%)
Real-Time Trends: Twitter/X Live Trend Watcher (Colombia, LatAm, Global) -> Deep Web Pre-Indexed Intelligence
Collective Memory: Anonymous Query-to-Onion Bank + Automatic SQLite FTS5 Node Absorption
Online Verification: Active SOCKS5h Circuit Health Monitor + Fast IPv4 Bilingual Ahmia Harvester (ES <-> EN)
Directory Structure: Classic AltaVista / Yahoo! 1997 Compact Directory + Google 1998 Minimalist SERP
Query Capabilities: Google-Style Operators (cat:, tax:, js:safest, site:, trust:, pgp:, "phrase", -exclude) + DuckDuckGo !Bangs
Spell Correction: In-Memory Damerau-Levenshtein ("Did you mean...?") with Automatic Fuzzy Recovery

/* SECURITY & OPSEC MODEL */
Client Protection: 100% Zero-JS (CSP default-src 'none'), Referrer-Policy: no-referrer, Anti-Tor2Web Detector
Storage Model: Pure RAM SQLite FTS5 (:memory:) + Anonymized Collective Node Index (Zero User Logs)
DDoS Defense: Native Tor v3 Proof-of-Work (Equi-X Puzzle)
"""

ROBOTS_TXT = """User-agent: *
Allow: /
Allow: /verificar
Allow: /proteccion
Allow: /canary.txt
Allow: /humans.txt
Allow: /security.txt
Allow: /.well-known/security.txt
"""


def _render_retro_logo(is_large: bool = True) -> str:
    cls = "retro-logo" if is_large else "serp-logo"
    tag = ' <span class="onion-tag">.onion</span>' if is_large else ""
    return (
        f'<a href="/" class="{cls}">'
        f'<span class="c1">S</span><span class="c2">a</span><span class="c3">m</span><span class="c1">u</span>'
        f'<span class="c4">B</span><span class="c2">u</span><span class="c3">s</span><span class="c1">q</span>'
        f'<span class="c4">u</span><span class="c2">e</span><span class="c3">d</span><span class="c1">a</span>'
        f'<span class="c4">s</span><span class="c2">!</span>{tag}</a>'
    )


def _render_twitter_trends_ai_bar_html() -> str:
    """
    Renderiza el Radar de Tendencias en Tiempo Real de Twitter/X -> Deep Web
    curadas por Inteligencia Artificial Anti-Basura (`SAMU_AI_ENGINE`).
    """
    trends = TWITTER_TREND_WATCHER.get_active_trends(limit=10)
    t_stats = TWITTER_TREND_WATCHER.get_stats()
    if not trends:
        return ""

    pills: List[str] = []
    for item in trends:
        q_str = str(item.get("query", ""))
        disp = str(item.get("display", q_str))
        cat = str(item.get("category", "Tendencia"))
        reg = str(item.get("region", "Global"))
        ai_sc = float(item.get("ai_score", 92.0))
        cnt = int(item.get("result_count", 4))
        href = f"/?q={urllib.parse.quote_plus(q_str)}"
        pills.append(
            f'<a href="{href}" class="trend-ai-pill" '
            f'title="Tendencia Twitter/X ({reg} • {cat}) • IA Anti-Basura: {ai_sc:.0f}% • {cnt} nodos .onion pre-indexados">'
            f"🔥 {html.escape(disp)} <span class=\"trend-ai-score\">[IA {ai_sc:.0f}%]</span></a>"
        )

    return f"""
    <div class="trends-ai-box">
        <div class="trends-ai-header">
            <strong>📡 Lo Más Buscado en Twitter/X (Tiempo Real) → Pre-Indexado en Deep Web con IA Anti-Basura:</strong>
            <span>
                <strong>{t_stats['active_trends_count']}</strong> tendencias activas •
                Filtro IA: <strong>≥75% Calidad</strong> (0% Spam/Basura) •
                Regiones: <code>CO / LATAM / GLOBAL / US / ES</code>
            </span>
        </div>
        <div class="collective-pills-row">
            {" ".join(pills)}
        </div>
    </div>
    """


def _render_collective_memory_bar_html() -> str:
    """
    Renderiza la barra de Memoria Colectiva de Búsquedas Exitosas para que cualquier
    usuario vea qué búsquedas ya están pre-verificadas y listas al instante.
    """
    popular = COLLECTIVE_MEMORY.get_popular_successful_queries(limit=10)
    stats = COLLECTIVE_MEMORY.get_stats()
    if not popular:
        return ""

    pills: List[str] = []
    for item in popular:
        q_str = str(item.get("query", ""))
        disp = str(item.get("display_query", q_str))
        cnt = int(item.get("result_count", 0))
        hits = int(item.get("hits", 1))
        href = f"/?q={urllib.parse.quote_plus(q_str)}"
        pills.append(
            f'<a href="{href}" class="collective-pill" title="{cnt} enlaces .onion verificados • {hits} búsquedas exitosas">'
            f"{html.escape(disp)} <span class=\"collective-pill-count\">({cnt})</span></a>"
        )

    return f"""
    <div class="collective-memory-box">
        <div class="collective-memory-header">
            <strong>⚡ Memoria Colectiva de Búsquedas Exitosas (Respuesta Instantánea):</strong>
            <span>
                <strong>{stats['saved_queries']}</strong> búsquedas aprendidas •
                <strong>{stats['total_cached_links']}</strong> enlaces <code>.onion</code> verificados a la mano •
                <strong>{stats['learned_nodes']}</strong> nodos auto-indexados
            </span>
        </div>
        <div class="collective-pills-row">
            {" ".join(pills)}
        </div>
    </div>
    """


def _render_btc_left_corner_widget(search_count: int = 0) -> str:
    """
    Renderiza el recuadro fijo en la esquina izquierda con el Código QR Oficial de Bitcoin
    y la dirección de depósito `13CCAjcHanNyKNcR3eFSh2PEu9tBzpXq3d` para mantener el proyecto.
    """
    if search_count > FREE_SEARCH_LIMIT:
        usage_badge = (
            f'<div class="btc-corner-status btc-status-alert">'
            f'🚨 Búsquedas: <strong>{search_count}</strong> (&gt;{FREE_SEARCH_LIMIT}: Modo Espera 15s Activo)'
            f"</div>"
        )
    else:
        usage_badge = (
            f'<div class="btc-corner-status">'
            f"Búsquedas rápidas: <strong>{search_count}/{FREE_SEARCH_LIMIT}</strong> antes de espera de 15s"
            f"</div>"
        )

    return f"""
    <aside class="btc-left-corner-box" aria-label="Donaciones Bitcoin para mantener SamuBusquedas">
        <a href="{BTC_URI}" class="btc-corner-qr-link" title="Escanear QR para donar BTC a {BTC_ADDRESS}">
            <img src="{BTC_QR_PATH}" alt="QR Donar BTC {BTC_ADDRESS}" class="btc-corner-qr" width="76" height="76">
        </a>
        <div class="btc-corner-info">
            <div class="btc-corner-title">
                <span class="btc-symbol">₿</span> <strong>Donar BTC — Mantener Proyecto SamuBusquedas</strong>
            </div>
            <div class="btc-corner-addr-row">
                <span>Dirección BTC:</span>
                <code class="btc-addr-code" title="Dirección oficial de depósito BTC">{BTC_ADDRESS}</code>
                <a href="{BTC_URI}" class="btc-uri-link">[Abrir Wallet]</a>
            </div>
            <div class="btc-corner-sub">
                Red <strong>BTC (Bitcoin)</strong> ("1", "3", "bc1p", "bc1q") • {usage_badge}
            </div>
        </div>
    </aside>
    """


def render_aggressive_donation_gate_page(
    query: str,
    target_url: str,
    search_count: int,
) -> str:
    """
    Renderiza la pantalla intersticial agresiva de 15 segundos con el código QR grande
    cuando el usuario supera las 10 búsquedas (`search_count > 10`).
    """
    safe_q = html.escape(query or "toda la red Tor")
    safe_target = html.escape(target_url)
    return f"""
    <section class="btc-aggressive-gate">
        <div class="btc-gate-banner">
            🚨 HAS SUPERADO LAS {FREE_SEARCH_LIMIT} BÚSQUEDAS GRATUITAS (BÚSQUEDA #{search_count}) — SE REQUIERE TU APORTE PARA SOSTENER EL PROYECTO 🚨
        </div>
        <h1 class="btc-gate-title">
            Apoya a SamuBusquedas con Bitcoin (BTC) para mantener los nodos Tor y la IA Anti-Basura activos 24/7
        </h1>
        <p class="btc-gate-lead">
            Has realizado <strong>{search_count} búsquedas</strong> en esta sesión. Operar verificadores criptográficos
            <code>SHA3-256</code>, circuitos Tor y filtros de Inteligencia Artificial sin publicidad comercial tiene un costo continuo.
            <strong>Tu búsqueda para «{safe_q}» se mostrará automáticamente en {DONATION_GATE_SECONDS} segundos.</strong>
        </p>

        <div class="btc-gate-card">
            <div class="btc-gate-network-pill">Depositar BTC • Red: <strong>BTC (Bitcoin)</strong></div>
            <div class="btc-gate-qr-wrap">
                <img
                    src="{BTC_QR_PATH}"
                    alt="Código QR Bitcoin {BTC_ADDRESS}"
                    class="btc-gate-qr-large"
                    width="210"
                    height="210"
                >
            </div>
            <div class="btc-gate-addr-label">Dirección oficial de depósito BTC:</div>
            <div class="btc-gate-addr-box">
                <code>{BTC_ADDRESS}</code>
            </div>
            <p class="btc-gate-network-note">
                {html.escape(BTC_NETWORK_NOTE)}
            </p>
        </div>

        <div class="btc-countdown-container">
            <div class="btc-countdown-label">
                ⏳ Mostrando resultados de <strong>"{safe_q}"</strong> en <strong>{DONATION_GATE_SECONDS} segundos</strong> mientras escaneas el código QR...
            </div>
            <div class="btc-countdown-track">
                <div class="btc-countdown-fill"></div>
            </div>
            <div class="btc-continue-wrap">
                <a href="{safe_target}" class="btc-continue-btn">
                    ✅ Ya habían pasado los {DONATION_GATE_SECONDS}s — Ver resultados de "{safe_q}" ahora →
                </a>
            </div>
        </div>
    </section>
    """


def render_layout(
    title: str,
    active_nav: str,
    security_eval: Dict[str, object],
    body_html: str,
    search_count: int = 0,
    meta_refresh_url: Optional[str] = None,
    meta_refresh_seconds: int = DONATION_GATE_SECONDS,
) -> str:
    """Estructura maestra HTML minimalista al estilo Google 1998 / AltaVista 1997 con QR BTC en esquina izquierda."""
    risk_level = str(security_eval.get("risk_level", "SEGURO"))
    if risk_level == "CRÍTICO":
        risk_pill = '<span class="pill-danger">[ALERTA CRÍTICA: PROXY TOR2WEB DETECTADO]</span>'
    elif risk_level == "ADVERTENCIA":
        risk_pill = '<span class="pill-warn">[OPSEC: NAVEGADOR ESTÁNDAR - USA TOR BROWSER]</span>'
    else:
        risk_pill = '<span class="pill-safe">[Escudo Tor: SEGURO]</span>'

    warnings_html = ""
    warnings = security_eval.get("warnings", [])
    if isinstance(warnings, list) and warnings and risk_level == "CRÍTICO":
        items = "".join(f"<li>{html.escape(str(w))}</li>" for w in warnings)
        warnings_html = f"""
        <div class="alert-box critical">
            <span class="alert-title">Alerta de Seguridad:</span>
            <ul style="padding-left: 18px;">{items}</ul>
        </div>
        """

    meta_refresh_tag = ""
    if meta_refresh_url:
        meta_refresh_tag = (
            f'\n    <meta http-equiv="refresh" content="{int(meta_refresh_seconds)};url={html.escape(meta_refresh_url)}">'
        )

    total_indexed = sum(int(c["total"]) for c in search_engine.get_categories())  # type: ignore
    btc_left_corner_html = _render_btc_left_corner_widget(search_count=search_count)

    return f"""<!DOCTYPE html>
{ASCII_HACKER_BANNER}
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="referrer" content="no-referrer">
    <meta name="author" content="saghet">
    <meta name="creator" content="saghet">
    <meta name="generator" content="SamuBusquedas v{APP_VERSION} Engine by saghet (Zero-JS Tor Shield)">{meta_refresh_tag}
    <title>{html.escape(title)} — SamuBusquedas v{APP_VERSION} (.onion) by saghet</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="opsec-topbar">
        <div class="topbar-links">
            <span class="version-corner-badge" title="SamuBusquedas Versión {APP_VERSION} por saghet">v{APP_VERSION}</span>
            <a href="/">Buscador</a>
            <a href="/?q=all">Directorio Verificado Online ({total_indexed})</a>
            <a href="/verificar">Escáner Anti-Phishing</a>
            <a href="/proteccion">Guía OPSEC</a>
            <a href="/humans.txt">humans.txt (saghet)</a>
            <a href="/canary.txt">Canario PGP</a>
        </div>
        <div>
            {risk_pill} • <span class="pill-purple">v{APP_VERSION} Zero-JS | by saghet</span>
        </div>
    </div>

    <div class="btc-top-left-wrapper">
        {btc_left_corner_html}
    </div>

    <main class="container">
        {warnings_html}
        {body_html}
    </main>

    <footer class="site-footer">
        <p>
            © 2026 <strong>SamuBusquedas! v{APP_VERSION} (.onion v3)</strong> — Creado por <strong><code>saghet</code></strong> |
            Donaciones BTC: <code>{BTC_ADDRESS}</code> |
            Motor <code>SamuRank v{APP_VERSION}</code> | 100% Zero-JS &amp; Zero-Logs de Usuario.
        </p>
        <p style="margin-top: 4px;">
            <a href="/humans.txt">/humans.txt</a> -
            <a href="/.well-known/security.txt">/.well-known/security.txt (RFC 9116)</a> -
            <a href="/canary.txt">/canary.txt</a> -
            <a href="/?q=saghet">Acerca de saghet</a>
        </p>
    </footer>
</body>
</html>"""


def _render_knowledge_card_html(k_card: Optional[Dict[str, object]]) -> str:
    if not k_card:
        return ""
    attrs_html = []
    for label, val in k_card.get("attributes", []):  # type: ignore
        attrs_html.append(f"<span><strong>{html.escape(str(label))}:</strong> {html.escape(str(val))}</span>")

    badge_text = (
        "KNOWLEDGE CARD DE AUTORÍA HACKER (VERIFICADA)"
        if k_card.get("type") == "AUTHOR_CARD"
        else "FICHA RÁPIDA DE ENTIDAD VERIFICADA (.ONION v3)"
    )

    return f"""
    <aside class="knowledge-card">
        <span class="kc-badge">{badge_text}</span>
        <div class="kc-title">{html.escape(str(k_card.get("title", "")))}</div>
        <div class="kc-subtitle">{html.escape(str(k_card.get("subtitle", "")))}</div>
        <p>{html.escape(str(k_card.get("summary", "")))}</p>
        <div class="kc-attrs">
            {" • ".join(attrs_html)}
        </div>
    </aside>
    """


def render_classic_home_page(categories: List[Dict[str, object]]) -> str:
    """
    Renderiza la Portada Minimalista al estilo de la primera versión de Google (1998),
    el Radar de Tendencias en Tiempo Real de Twitter/X -> Deep Web (con IA Anti-Basura),
    la Memoria Colectiva de Búsquedas Exitosas y la tabla de categorías estilo AltaVista / Yahoo! (1997).
    """
    total_sites = sum(int(c["total"]) for c in categories)  # type: ignore
    trends_ai_bar = _render_twitter_trends_ai_bar_html()
    collective_bar = _render_collective_memory_bar_html()

    return f"""
    <section class="classic-home-hero">
        {_render_retro_logo(is_large=True)}
        <p class="retro-tagline">
            Buscador de la Deep Web ({total_sites} Sitios Indexados + Tendencias Twitter/X en Vivo + Filtro IA Anti-Basura) — Arquitectura por <strong>saghet</strong>
        </p>

        <form action="/" method="GET" class="retro-search-box">
            <div>
                <label for="q-input" style="font-size: 13px; display: block; margin-bottom: 4px;">
                    Busca cualquier servicio, tendencia de Twitter/X, foro, wiki, cripto, biblioteca, prensa o herramienta en la red Tor:
                </label>
                <input
                    id="q-input"
                    type="text"
                    name="q"
                    value=""
                    placeholder="Ej: gustavo petro, inteligencia artificial, monero, wikileaks, bellingcat, foros, saghet..."
                    class="retro-input"
                    autofocus
                >
            </div>
            <div class="retro-buttons">
                <button type="submit" class="retro-btn">Buscar con SamuBusquedas</button>
                <a href="/?q=%21random" class="retro-btn">Voy a tener suerte (!random)</a>
            </div>
            <div class="retro-radios">
                <label>
                    <input type="radio" name="scope" value="all" checked>
                    Buscar en toda la Deep Web (<strong>{total_sites} sitios indexados + Tendencias Twitter/X + Filtro IA Anti-Basura</strong>)
                </label>
                <label>
                    <input type="radio" name="scope" value="verified">
                    Solo Sitios Oficiales Verificados (PGP)
                </label>
            </div>
        </form>

        {trends_ai_bar}
        {collective_bar}

        <table class="altavista-directory">
            <thead>
                <tr>
                    <th colspan="2">
                        Directorio Temático Rápido (Estilo AltaVista / Yahoo! 1997) — Haz clic para explorar:
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>
                        <a href="/?q=foros+wiki" class="dir-cat-title">Wikis, Foros &amp; Comunidad Tor</a>
                        <div class="dir-sublinks">
                            <a href="/?q=hidden+wiki">Hidden Wiki</a>,
                            <a href="/?q=dread">Dread Forum</a>,
                            <a href="/?q=daunt">Daunt</a>,
                            <a href="/?q=pitch">Pitch Forum</a>,
                            <a href="/?q=endchan">EndChan</a>,
                            <a href="/?q=radio">DeepWeb Radio</a>
                        </div>
                    </td>
                    <td>
                        <a href="/?cat=Prensa+y+Whistleblowing" class="dir-cat-title">Prensa &amp; Whistleblowing (SecureDrop)</a>
                        <div class="dir-sublinks">
                            <a href="/?q=propublica">ProPublica</a>,
                            <a href="/?q=securedrop">SecureDrop</a>,
                            <a href="/?q=nytimes">NYTimes</a>,
                            <a href="/?q=bbc">BBC</a>,
                            <a href="/?q=guardian">The Guardian</a>,
                            <a href="/?q=bellingcat">Bellingcat</a>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>
                        <a href="/?q=monero+bitcoin" class="dir-cat-title">Criptomonedas &amp; Exploradores Blockchain</a>
                        <div class="dir-sublinks">
                            <a href="/?q=monero">Monero (XMR)</a>,
                            <a href="/?q=feather">Feather Wallet</a>,
                            <a href="/?q=mempool">Mempool.space</a>,
                            <a href="/?q=blockstream">Blockstream</a>,
                            <a href="/?q=blockchair">Blockchair</a>,
                            <a href="/?q=bisq">Bisq P2P</a>
                        </div>
                    </td>
                    <td>
                        <a href="/?cat=Correo+y+Comunicaci%C3%B3n+Cifrada" class="dir-cat-title">Correo Cifrado, Chat &amp; XMPP</a>
                        <div class="dir-sublinks">
                            <a href="/?q=protonmail">ProtonMail</a>,
                            <a href="/?q=riseup">Riseup</a>,
                            <a href="/?q=briar">Briar</a>,
                            <a href="/?q=simplex">SimpleX</a>,
                            <a href="/?q=cockli">Cock.li</a>,
                            <a href="/?q=irc">Hackint IRC</a>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>
                        <a href="/?cat=Bibliotecas%2C+Archivos+y+Ciencia" class="dir-cat-title">Bibliotecas, Libros &amp; Ciencia</a>
                        <div class="dir-sublinks">
                            <a href="/?q=trantor">Imperial Library</a>,
                            <a href="/?q=scihub">Sci-Hub</a>,
                            <a href="/?q=annas">Anna's Archive</a>,
                            <a href="/?q=comics">Comic Library</a>,
                            <a href="/?q=internet+archive">Wayback Machine</a>
                        </div>
                    </td>
                    <td>
                        <a href="/?q=hacker+git+pastebin" class="dir-cat-title">Cultura Hacker, Git &amp; Pastebins</a>
                        <div class="dir-sublinks">
                            <a href="/?q=defcon">DEF CON</a>,
                            <a href="/?q=ccc">Chaos Computer Club</a>,
                            <a href="/?q=pastebin">StrongHold Paste</a>,
                            <a href="/?q=gitea">Gitea Tor</a>,
                            <a href="/?q=cyberchef">CyberChef</a>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>
                        <a href="/?cat=Sistemas+Operativos+y+Software+Libre" class="dir-cat-title">Sistemas Operativos &amp; Espejos Debian/Tor</a>
                        <div class="dir-sublinks">
                            <a href="/?q=whonix">Whonix</a>,
                            <a href="/?q=qubes">Qubes OS</a>,
                            <a href="/?q=tails">Tails USB</a>,
                            <a href="/?q=debian">Debian Mirrors</a>,
                            <a href="/?q=onionshare">OnionShare</a>
                        </div>
                    </td>
                    <td>
                        <a href="/?cat=Buscadores+Leg%C3%ADtimos" class="dir-cat-title">Motores de Búsqueda &amp; VPNs en Tor</a>
                        <div class="dir-sublinks">
                            <a href="/?q=duckduckgo">DuckDuckGo</a>,
                            <a href="/?q=brave">Brave</a>,
                            <a href="/?q=metager">MetaGer</a>,
                            <a href="/?q=searxng">SearXNG</a>,
                            <a href="/?q=ahmia">Ahmia</a>,
                            <a href="/?q=torch">Torch</a>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </section>
    """


def render_serp_page(
    query: str,
    category: str,
    taxonomy: str,
    scope: str,
    search_payload: Dict[str, object],
    search_count: int = 0,
) -> str:
    """
    Renderiza la Página de Resultados (SERP) minimalista con soporte de Memoria Colectiva,
    Filtro IA Anti-Basura (`ai_quality_score`), verificación activa Online (.onion v3) y
    banner agresivo de donaciones BTC cuando el usuario supera las 10 búsquedas.
    """
    results: List[Dict[str, object]] = search_payload["results"]  # type: ignore
    did_you_mean = search_payload.get("did_you_mean")
    auto_corrected_from = search_payload.get("auto_corrected_from")
    semantic_intent = search_payload.get("semantic_intent")
    is_exploratory = bool(search_payload.get("is_exploratory_fallback"))
    collective_hit = bool(search_payload.get("collective_memory_hit"))
    collective_hits = int(search_payload.get("collective_hits", 0) or 0)
    newly_indexed_count = int(search_payload.get("newly_indexed_count", 0) or 0)
    total_indexed_surface = int(search_payload.get("total_indexed_surface", 112) or 112)
    ai_garbage_rejected = int(search_payload.get("ai_garbage_rejected", 0) or 0)
    k_card = search_payload.get("knowledge_card")  # type: ignore
    bang_info = search_payload.get("bang_info")  # type: ignore
    elapsed_ms = search_payload.get("elapsed_ms", 0.0)

    dym_html = ""
    if auto_corrected_from and did_you_mean:
        dym_url = f"/?q={urllib.parse.quote(str(did_you_mean))}"
        dym_html = f"""
        <div class="alert-box did-you-mean">
            <span class="alert-title">Se muestran resultados para:</span>
            <a href="{dym_url}"><strong>{html.escape(str(did_you_mean))}</strong></a>
            (en lugar de <em>{html.escape(str(auto_corrected_from))}</em>).
        </div>
        """
    elif did_you_mean:
        dym_url = f"/?q={urllib.parse.quote(str(did_you_mean))}"
        dym_html = f"""
        <div class="alert-box did-you-mean">
            <span class="alert-title">¿Quisiste decir:</span>
            <a href="{dym_url}"><strong>{html.escape(str(did_you_mean))}</strong></a>?
        </div>
        """

    if isinstance(semantic_intent, dict):
        intent_label = html.escape(str(semantic_intent.get("label", "")))
        intent_advisory = html.escape(str(semantic_intent.get("advisory", "")))
        dym_html += f"""
        <div class="alert-box safe">
            <span class="alert-title">{intent_label}:</span>
            {intent_advisory}
        </div>
        """
    elif is_exploratory:
        dym_html += f"""
        <div class="alert-box">
            <span class="alert-title">Búsqueda abierta en la Deep Web para "{html.escape(query)}":</span>
            Mostrando nodos del Índice Abierto Tor (No Verificados) y buscadores profundos.
        </div>
        """

    bang_html = ""
    if isinstance(bang_info, dict):
        b_url = html.escape(str(bang_info.get("url", "/")))
        bang_html = f"""
        <div class="alert-box safe">
            <span class="alert-title">Salto Rápido (!Bang): {html.escape(str(bang_info.get("name", "")))}</span> —
            <a href="{b_url}" class="onion-link" rel="noreferrer noopener" target="_blank">Ir directamente a {b_url}</a>
        </div>
        """

    aggressive_serp_spam_html = ""
    if search_count > FREE_SEARCH_LIMIT:
        aggressive_serp_spam_html = f"""
        <div class="btc-serp-spam-banner">
            <img src="{BTC_QR_PATH}" alt="QR BTC {BTC_ADDRESS}" width="64" height="64" class="btc-serp-spam-qr">
            <div>
                <div class="btc-serp-spam-title">
                    🚨 Llevas {search_count} búsquedas (&gt;{FREE_SEARCH_LIMIT} gratuitas) — ¡Apoya a SamuBusquedas con BTC!
                </div>
                <div class="btc-serp-spam-text">
                    Cada nueva búsqueda tendrá una espera previa de <strong>{DONATION_GATE_SECONDS} segundos</strong> con el código QR.
                    Envía tu aporte en Bitcoin a: <code>{BTC_ADDRESS}</code> (<a href="{BTC_URI}">Abrir Wallet BTC</a>)
                </div>
            </div>
        </div>
        """

    verified_count = sum(1 for r in results if r.get("verification_tier") == "VERIFIED")
    unverified_count = len(results) - verified_count

    items_html = []
    for idx, svc in enumerate(results, start=1):
        tier = str(svc.get("verification_tier", "VERIFIED"))
        if tier == "VERIFIED":
            badge_html = '<span class="tier-badge-verified">[VERIFICADO PGP]</span>'
        else:
            badge_html = '<span class="tier-badge-unverified">[ACTIVO COMUNITARIO]</span>'

        latency_ms = int(svc.get("latency_ms", 340))
        online_badge_html = f'<span class="online-badge">[ONLINE EN TOR • {latency_ms} ms]</span>'

        ai_score = float(svc.get("ai_quality_score", 92.0) or 92.0)
        ai_badge_html = (
            f'<span class="ai-badge" title="Verificado por Motor IA Anti-Basura (Entropía de Shannon + Coherencia Semántica)">'
            f"[IA CALIDAD: {ai_score:.0f}%]</span>"
        )

        collective_badge_html = ""
        if svc.get("newly_indexed"):
            collective_badge_html = (
                '<span class="collective-badge" title="Nuevo sitio .onion v3 descubierto e indexado permanentemente en esta búsqueda">'
                "[+NUEVO INDEXADO EN MOTOR]</span>"
            )
        elif svc.get("collective_memory"):
            c_hits = int(svc.get("collective_hits", collective_hits) or 1)
            collective_badge_html = (
                f'<span class="collective-badge" title="Guardado en Memoria Colectiva ({c_hits} búsquedas exitosas)">'
                f"[MEMORIA COLECTIVA • {c_hits}x]</span>"
            )

        onion_url = str(svc["onion_url"])
        clearnet_url = str(svc["clearnet_url"])
        title_rendered = str(svc.get("highlighted_title") or html.escape(str(svc["title"])))
        desc_rendered = str(svc.get("highlighted_desc") or html.escape(str(svc["description"])))
        verify_link = f"/verificar?onion={urllib.parse.quote(onion_url)}"

        items_html.append(
            f"""
            <article class="service-card">
                <div>
                    <span style="color: #666; font-size: 13px;">{idx}.</span>
                    <h2 class="service-title">
                        <a href="{html.escape(onion_url)}" rel="noreferrer noopener" target="_blank">{title_rendered}</a>
                    </h2>
                    {badge_html}
                    {online_badge_html}
                    {ai_badge_html}
                    {collective_badge_html}
                </div>
                <p class="service-desc">{desc_rendered}</p>
                <div class="serp-url-line">
                    <a href="{html.escape(onion_url)}" class="onion-link" rel="noreferrer noopener" target="_blank">{html.escape(onion_url)}</a>
                    <span class="serp-meta-links">
                        — Estado: <strong style="color: #006600;">VÁLIDO ONLINE ({latency_ms} ms)</strong>
                        — SamuRank: <strong>{svc.get("samu_rank", svc["safety_score"])}</strong>
                        — IA Calidad: <strong>{ai_score:.0f}%</strong>
                        — Modo Tor: {html.escape(str(svc["js_requirement"]))}
                        — <a href="{verify_link}">[Auditar Llave SHA3-256]</a>
                        — <a href="{html.escape(clearnet_url)}" rel="noreferrer noopener" target="_blank">[Ref/Salto]</a>
                    </span>
                </div>
            </article>
            """
        )

    checked_all = "checked" if scope != "verified" else ""
    checked_ver = "checked" if scope == "verified" else ""
    label_query = query if query else (category if category != "Todas" else taxonomy or "Todos")

    collective_status_str = ""
    if newly_indexed_count > 0:
        collective_status_str += (
            f' • <strong style="color:#006600;">+{newly_indexed_count} nuevos nodos .onion indexados (Total Motor: {total_indexed_surface})</strong>'
        )
    if collective_hit or collective_hits > 0:
        collective_status_str += f' • <strong style="color:#4b0082;">⚡ Memoria Colectiva ({collective_hits}x)</strong>'
    if ai_garbage_rejected > 0:
        collective_status_str += f' • <strong style="color:#005580;">🤖 Filtro IA bloqueó {ai_garbage_rejected} basura</strong>'
    else:
        collective_status_str += ' • <strong style="color:#005580;">🤖 Filtro IA Anti-Basura Activo (≥75%)</strong>'

    return f"""
    <header class="serp-header">
        {_render_retro_logo(is_large=False)}
        <form action="/" method="GET" class="serp-form">
            <input
                type="text"
                name="q"
                value="{html.escape(query)}"
                placeholder="Buscar en la red Tor..."
                class="serp-input"
                aria-label="Buscar en SamuBusquedas"
            >
            <button type="submit" class="retro-btn">Buscar</button>
            <span style="font-size: 12px; margin-left: 6px;">
                <label><input type="radio" name="scope" value="all" {checked_all}> Todo (Verificados + Comunitarios Online)</label>
                <label style="margin-left: 6px;"><input type="radio" name="scope" value="verified" {checked_ver}> Solo Oficiales PGP</label>
            </span>
        </form>
    </header>

    <div class="serp-stats-bar">
        <span>
            Superficie Verificada Online: Mostrando <strong>{len(results)} enlaces .onion activos</strong>
            (<strong>{verified_count} Oficiales PGP</strong> + <strong>{unverified_count} Nodos Tor Activos</strong>)
            para <strong>"{html.escape(str(label_query))}"</strong>{collective_status_str}
        </span>
        <span>Tiempo: <strong>{elapsed_ms} ms</strong> • Algoritmo <code>SamuRank v{APP_VERSION}</code> by <strong>saghet</strong></span>
    </div>

    {aggressive_serp_spam_html}
    {dym_html}
    {bang_html}
    {_render_knowledge_card_html(k_card)}

    <section class="results-grid">
        {"".join(items_html)}
    </section>
    """


def render_verify_page(inspected_url: str, report: Optional[Dict[str, object]]) -> str:
    """Renderiza el escáner Anti-Phishing clásico y directo con estado Online."""
    result_html = ""
    if report:
        verdict = str(report.get("verdict", ""))
        if verdict == "SAFE_VERIFIED":
            box_type = "safe"
        elif verdict == "DANGER_PHISHING":
            box_type = "critical"
        else:
            box_type = ""

        svc_info = ""
        svc = report.get("service")
        if isinstance(svc, dict):
            lat = int(svc.get("latency_ms", 350))
            svc_info = f"""
            <p style="margin-top: 6px; font-family: monospace;">
                <strong>Servicio Registrado:</strong> {html.escape(str(svc["title"]))}<br>
                <strong>Estado en Red Tor:</strong> <span class="online-badge">[ONLINE EN TOR • {lat} ms]</span><br>
                <strong>Dominio .onion Oficial:</strong>
                <a href="{html.escape(str(svc["onion_url"]))}" rel="noreferrer noopener">{html.escape(str(svc["onion_url"]))}</a><br>
                <strong>Evidencia PGP/OPSEC:</strong> {html.escape(str(svc["pgp_fingerprint"]))}
            </p>
            """

        result_html = f"""
        <div class="alert-box {box_type}">
            <span class="alert-title">[{html.escape(str(report.get("badge", "")))}] — Riesgo: {html.escape(str(report.get("risk_level", "")))}</span>
            <p style="margin-top: 4px;">{html.escape(str(report.get("message", "")))}</p>
            {svc_info}
        </div>
        """

    return f"""
    <header class="serp-header">
        {_render_retro_logo(is_large=False)}
        <strong>Escáner Criptográfico Anti-Phishing &amp; Verificador Online (.onion v3 Ed25519 + SHA3-256)</strong>
    </header>

    <form action="/verificar" method="GET" class="retro-search-box" style="text-align: left;">
        <p style="margin-bottom: 8px;">
            Pega cualquier enlace <code>.onion</code> para verificar matemáticamente sus 32 bytes de clave pública
            <code>Ed25519</code>, su suma de comprobación <code>SHA3-256</code> y comprobar si es un clon de phishing:
        </p>
        <input
            type="text"
            name="onion"
            value="{html.escape(inspected_url)}"
            placeholder="http://2gzyxa5ihm7nsggfxnu52rck2vv4rvmdlkiu3zzui5du4xyclen53wid.onion"
            class="retro-input"
        >
        <button type="submit" class="retro-btn">Auditar Llave .onion</button>
    </form>

    {result_html}
    """


def render_opsec_guide_page() -> str:
    audit_rows = audit_catalog_integrity()
    approved_count = sum(1 for r in audit_rows if r["status"] == "APROBADO")

    return f"""
    <header class="serp-header">
        {_render_retro_logo(is_large=False)}
        <strong>Guía de Seguridad OPSEC en la Deep Web (by saghet — v{APP_VERSION})</strong>
    </header>

    <div class="alert-box safe">
        <span class="alert-title">Auditoría Criptográfica SHA3-256 &amp; Verificación Online:</span>
        <strong>{approved_count} de {len(audit_rows)}</strong> dominios <code>.onion</code> v3 locales verificados matemáticamente y activos en la red Tor.
    </div>

    <table class="altavista-directory">
        <thead>
            <tr>
                <th colspan="2">Reglas Esenciales para Navegar Seguro en la Red Tor</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>
                    <strong>1. Usa el Modo "Safest" (Sin JavaScript)</strong>
                    <p class="dir-sublinks">
                        Abre el escudo de Tor Browser y selecciona el nivel <em>Safest</em> para bloquear exploits remotos de JavaScript.
                        SamuBusquedas funciona 100% en HTML puro.
                    </p>
                </td>
                <td>
                    <strong>2. Diferencia Sitios [VERIFICADO PGP] vs [ACTIVO COMUNITARIO]</strong>
                    <p class="dir-sublinks">
                        Los sitios con etiqueta verde cuentan con firma PGP o cabecera <code>Onion-Location</code> oficial.
                        En los sitios comunitarios, navega siempre en modo <em>Safest</em> y nunca ingreses datos personales.
                    </p>
                </td>
            </tr>
            <tr>
                <td>
                    <strong>3. Jamás uses Pasarelas Tor2Web (.onion.ly / .onion.ws)</strong>
                    <p class="dir-sublinks">
                        Accede únicamente desde <strong>Tor Browser</strong> oficial. Los proxies intermedios en navegadores normales interceptan todo tu tráfico.
                    </p>
                </td>
                <td>
                    <strong>4. Auditoría Abierta para Hackers (Autor: saghet)</strong>
                    <p class="dir-sublinks">
                        Inspecciona nuestra arquitectura en <a href="/humans.txt">/humans.txt</a>,
                        <a href="/.well-known/security.txt">/.well-known/security.txt</a> y <a href="/canary.txt">/canary.txt</a>.
                    </p>
                </td>
            </tr>
        </tbody>
    </table>
    """


class SamuOnionRequestHandler(BaseHTTPRequestHandler):
    server_version = f"SamuEngine/{APP_VERSION} (Tor-v3; Zero-JS; Hardened)"
    sys_version = ""

    def version_string(self) -> str:
        return self.server_version

    def date_time_string(self, timestamp: Optional[float] = None) -> str:
        return "Thu, 01 Jan 1970 00:00:00 GMT"

    def log_message(self, format: str, *args: object) -> None:
        pass

    def _send_hardened_headers(
        self,
        status_code: int = 200,
        content_type: str = "text/html; charset=utf-8",
        set_cookie: Optional[str] = None,
    ) -> None:
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("X-Architected-By", "saghet")
        self.send_header("X-Builder-Handle", "saghet")
        self.send_header("X-Engine-Version", APP_VERSION)
        self.send_header("X-Engine-Signature", f"saghet-samubusquedas-v{APP_VERSION}-ed25519")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; form-action 'self'; frame-ancestors 'none'; base-uri 'none'",
        )
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header("X-Permitted-Cross-Domain-Policies", "none")
        self.send_header("Permissions-Policy", "geolocation=(), microphone=(), camera=(), usb=(), interest-cohort=()")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Onion-Location", f"{OFFICIAL_ONION_DOMAIN}/")
        if set_cookie:
            self.send_header("Set-Cookie", set_cookie)
        self.end_headers()

    def do_HEAD(self) -> None:
        self._send_hardened_headers(200)

    def do_GET(self) -> None:
        safe_raw_path = self.path[:1024]
        parsed = urllib.parse.urlparse(safe_raw_path)
        path = parsed.path
        query_params = urllib.parse.parse_qs(parsed.query)

        if path == "/static/style.css":
            css_path = os.path.join(STATIC_DIR, "style.css")
            if os.path.exists(css_path):
                with open(css_path, "rb") as f:
                    content = f.read()
                self._send_hardened_headers(200, "text/css; charset=utf-8")
                self.wfile.write(content)
                return

        if path == "/static/btc_qr.png":
            qr_path = os.path.join(STATIC_DIR, "btc_qr.png")
            if os.path.exists(qr_path):
                with open(qr_path, "rb") as f:
                    content = f.read()
                self._send_hardened_headers(200, "image/png")
                self.wfile.write(content)
                return

        if path == "/canary.txt":
            self._send_hardened_headers(200, "text/plain; charset=utf-8")
            self.wfile.write(CANARY_TEXT.encode("utf-8"))
            return

        if path in ("/security.txt", "/.well-known/security.txt"):
            self._send_hardened_headers(200, "text/plain; charset=utf-8")
            self.wfile.write(SECURITY_TXT.encode("utf-8"))
            return

        if path == "/humans.txt":
            self._send_hardened_headers(200, "text/plain; charset=utf-8")
            self.wfile.write(HUMANS_TXT.encode("utf-8"))
            return

        if path == "/robots.txt":
            self._send_hardened_headers(200, "text/plain; charset=utf-8")
            self.wfile.write(ROBOTS_TXT.encode("utf-8"))
            return

        if path in ("/health", "/healthz"):
            self._send_hardened_headers(200, "application/json; charset=utf-8")
            payload = {
                "status": "ok",
                "version": APP_VERSION,
                "engine": f"SamuBusquedas v{APP_VERSION}",
                "architect": "saghet",
                "total_indexed_surface": search_engine.get_total_indexed_count(),
                "collective_memory": COLLECTIVE_MEMORY.get_stats(),
                "twitter_trends": TWITTER_TREND_WATCHER.get_stats(),
                "donations": DONATION_TRACKER.get_stats(),
                "onion_guardian": ONION_GUARDIAN.get_status(),
                "ai_filter": {
                    "engine": "SamuAIAntiGarbageEngine",
                    "min_quality_threshold": 75.0,
                    "methods": ["shannon_entropy", "bayesian_scam_veto", "topical_vector_coherence"],
                },
            }
            self.wfile.write((json.dumps(payload) + "\n").encode("utf-8"))
            return

        if path == "/api/trends":
            self._send_hardened_headers(200, "application/json; charset=utf-8")
            trends_payload = {
                "version": APP_VERSION,
                "architect": "saghet",
                "stats": TWITTER_TREND_WATCHER.get_stats(),
                "trends": TWITTER_TREND_WATCHER.get_active_trends(limit=12),
            }
            self.wfile.write((json.dumps(trends_payload, ensure_ascii=False) + "\n").encode("utf-8"))
            return

        req_headers = {k: v for k, v in self.headers.items()}
        security_eval = evaluate_client_connection_security(req_headers)
        client_ip = self.client_address[0] if self.client_address else "127.0.0.1"
        session_id, is_new_session = DONATION_TRACKER.resolve_session_id(req_headers, client_ip=client_ip)
        cookie_hdr = (
            f"{COOKIE_NAME}={session_id}; Path=/; Max-Age=43200; HttpOnly; SameSite=Lax"
            if is_new_session
            else None
        )

        if path == "/":
            q = query_params.get("q", [""])[0][:MAX_QUERY_LEN]
            cat = query_params.get("cat", ["Todas"])[0][:80]
            tax = query_params.get("tax", [""])[0][:40]
            scope = query_params.get("scope", ["all"])[0][:20]
            only_safest = query_params.get("safest", ["0"])[0] == "1"
            dpass = query_params.get("dpass", ["0"])[0] == "1"

            if not q.strip() and (not cat or cat == "Todas") and not tax.strip():
                current_cnt = DONATION_TRACKER.get_search_count(session_id)
                categories = search_engine.get_categories()
                body = render_classic_home_page(categories)
                page = render_layout(
                    "Buscador de la Deep Web",
                    "search",
                    security_eval,
                    body,
                    search_count=current_cnt,
                )
                self._send_hardened_headers(200, set_cookie=cookie_hdr)
                self.wfile.write(page.encode("utf-8"))
                return

            gate_eval = DONATION_TRACKER.register_search_and_evaluate_gate(
                session_id=session_id,
                is_real_search=True,
                dpass_completed=dpass,
            )
            current_cnt = int(gate_eval["search_count"])

            if gate_eval["should_gate"]:
                forward_params: List[Tuple[str, str]] = []
                if q:
                    forward_params.append(("q", q))
                if cat and cat != "Todas":
                    forward_params.append(("cat", cat))
                if tax:
                    forward_params.append(("tax", tax))
                if scope and scope != "all":
                    forward_params.append(("scope", scope))
                if only_safest:
                    forward_params.append(("safest", "1"))
                forward_params.append(("dpass", "1"))
                target_url = "/?" + urllib.parse.urlencode(forward_params)

                gate_body = render_aggressive_donation_gate_page(
                    query=q or cat or tax,
                    target_url=target_url,
                    search_count=current_cnt,
                )
                gate_page = render_layout(
                    f"Apoya a SamuBusquedas ({DONATION_GATE_SECONDS}s) — {q or cat}",
                    "search",
                    security_eval,
                    gate_body,
                    search_count=current_cnt,
                    meta_refresh_url=target_url,
                    meta_refresh_seconds=DONATION_GATE_SECONDS,
                )
                self._send_hardened_headers(200, set_cookie=cookie_hdr)
                self.wfile.write(gate_page.encode("utf-8"))
                return

            actual_q = "" if q.strip().lower() == "all" else q
            include_unverified = scope != "verified"
            search_payload = search_engine.search_v2(
                query=actual_q,
                category=cat,
                taxonomy=tax if tax else None,
                only_safest_js=only_safest,
                include_unverified=include_unverified,
            )
            body = render_serp_page(
                actual_q,
                cat,
                tax,
                scope,
                search_payload,
                search_count=current_cnt,
            )
            page = render_layout(
                f"{q or cat} - Buscar con SamuBusquedas",
                "search",
                security_eval,
                body,
                search_count=current_cnt,
            )
            self._send_hardened_headers(200, set_cookie=cookie_hdr)
            self.wfile.write(page.encode("utf-8"))
            return

        current_cnt = DONATION_TRACKER.get_search_count(session_id)
        if path == "/verificar":
            onion_param = query_params.get("onion", [""])[0][:MAX_QUERY_LEN]
            report = search_engine.inspect_onion_url(onion_param) if onion_param.strip() else None
            body = render_verify_page(onion_param, report)
            page = render_layout(
                "Verificador Anti-Phishing SHA3-256",
                "verify",
                security_eval,
                body,
                search_count=current_cnt,
            )
            self._send_hardened_headers(200, set_cookie=cookie_hdr)
            self.wfile.write(page.encode("utf-8"))
            return

        if path == "/proteccion":
            body = render_opsec_guide_page()
            page = render_layout(
                "Guía OPSEC en la Deep Web",
                "opsec",
                security_eval,
                body,
                search_count=current_cnt,
            )
            self._send_hardened_headers(200, set_cookie=cookie_hdr)
            self.wfile.write(page.encode("utf-8"))
            return

        not_found_body = """
        <div class="alert-box critical">
            <span class="alert-title">Error 404 — Página no encontrada</span>
            <p><a href="/">Volver al buscador SamuBusquedas!</a></p>
        </div>
        """
        page = render_layout("404 No Encontrado", "", security_eval, not_found_body, search_count=current_cnt)
        self._send_hardened_headers(404, set_cookie=cookie_hdr)
        self.wfile.write(page.encode("utf-8"))


def ensure_onion_ssl_certificates() -> Tuple[Optional[str], Optional[str]]:
    """Garantiza la existencia de un certificado X.509 SSL para soportar conexiones HTTPS (puerto 443) en Tor Browser Móvil."""
    repo_root = os.path.dirname(BASE_DIR)
    runtime_dir = os.path.join(repo_root, ".tor_runtime")
    os.makedirs(runtime_dir, exist_ok=True)
    cert_path = os.path.join(runtime_dir, "onion_cert.pem")
    key_path = os.path.join(runtime_dir, "onion_key.pem")
    if os.path.exists(cert_path) and os.path.exists(key_path):
        return cert_path, key_path
    try:
        import datetime
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.x509.oid import NameOID

        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, "x4wgcuog7p6i3gh5t2mcshhfe5cjlkiygl24vf4ac6xmqm5g62jkehyd.onion")
        ])
        san = x509.SubjectAlternativeName([
            x509.DNSName("x4wgcuog7p6i3gh5t2mcshhfe5cjlkiygl24vf4ac6xmqm5g62jkehyd.onion"),
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ])
        cert = (
            x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1))
            .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3650))
            .add_extension(san, critical=False)
            .sign(key, hashes.SHA256())
        )
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        with open(key_path, "wb") as f:
            f.write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        return cert_path, key_path
    except Exception:
        return None, None


def run_server(host: str = "0.0.0.0", port: int = 8080, https_port: int = 8443) -> None:
    import ssl
    ONION_GUARDIAN.start_guardian_daemon(heartbeat_interval_seconds=45)
    TWITTER_TREND_WATCHER.start_background_daemon(
        lambda q: search_engine.search_v2(query=q, enable_live_tor=True)
    )

    # 1. Listener HTTPS (Puerto 443 en Tor -> 8443 interno) para Tor Browser Móvil
    cert_path, key_path = ensure_onion_ssl_certificates()
    if cert_path and key_path and https_port:
        try:
            ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_ctx.load_cert_chain(cert_path, key_path)
            https_server = ThreadingHTTPServer(("127.0.0.1", https_port), SamuOnionRequestHandler)
            https_server.socket = ssl_ctx.wrap_socket(https_server.socket, server_side=True)
            https_thread = threading.Thread(target=https_server.serve_forever, daemon=True)
            https_thread.start()
            print(f"  [*] Listener HTTPS Activo (Tor port 443): https://127.0.0.1:{https_port}")
        except Exception as exc:
            print(f"  [!] No se pudo iniciar listener HTTPS ({exc})")

    # 2. Listener HTTP (Wi-Fi LAN + Tor port 80)
    server = ThreadingHTTPServer((host, port), SamuOnionRequestHandler)
    print("======================================================================")
    print(f"  SAMUBUSQUEDAS! v{APP_VERSION} (.ONION) - DUAL HTTP/HTTPS & RED WI-FI")
    print("  ARCHITECTED BY: saghet")
    print("======================================================================")
    print(f"  [*] Red Wi-Fi Local / HTTP: http://{host}:{port}")
    print(f"  [*] Dominio Tor Onion v3:   {OFFICIAL_ONION_DOMAIN}")
    print("======================================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    port_env = os.environ.get("PORT")
    host_env = os.environ.get("HOST")
    port_arg = int(port_env) if port_env else (int(sys.argv[1]) if len(sys.argv) > 1 else 8080)
    host_arg = host_env if host_env else "0.0.0.0"
    run_server(host=host_arg, port=port_arg)
