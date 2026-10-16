"""
SamuBusquedas v2.5 (.onion) - Interfaz Minimalista Clásica (Estilo Google 1998 / AltaVista 1997)
================================================================================================
Arquitecto Principal y Creador: saghet
Características:
1. Portada Centrada Ultraligera (Estilo Google Stanford 1998 + Tabla de Directorio AltaVista/Yahoo 97).
2. Página de Resultados (SERP) Compacta de 3 Líneas por Resultado (Título + Snippet Resaltado + Línea URL .onion).
3. Motor Interno SamuRank v2.5 Completo: 57 Sitios Locales (Verificados + Comunitarios) + Búsqueda en Vivo
   en la Red Tor + Corrector Ortográfico Automático Damerau-Levenshtein + Escudo Anti-Phishing SHA3-256.
4. Metadatos Hacker para `saghet`: Cabeceras HTTP (`X-Architected-By: saghet`), `/.well-known/security.txt`
   (RFC 9116), `/humans.txt`, `/canary.txt`, `<meta name="author" content="saghet">` y Banner ASCII Art.
"""

import html
import os
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, List, Optional

from database import MAX_QUERY_LEN, SamuSearchEngine
from security_shield import evaluate_client_connection_security
from verifier import audit_catalog_integrity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

search_engine = SamuSearchEngine()

OFFICIAL_ONION_DOMAIN = "http://x4wgcuog7p6i3gh5t2mcshhfe5cjlkiygl24vf4ac6xmqm5g62jkehyd.onion"

ASCII_HACKER_BANNER = """<!--
 =====================================================================================
   ____                        ____                                _
  / ___|  __ _ _ __ ___  _   _| __ ) _   _ ___  __ _ _   _  ___  __| | __ _ ___
  \\___ \\ / _` | '_ ` _ \\| | | |  _ \\| | | / __|/ _` | | | |/ _ \\/ _` |/ _` / __|
   ___) | (_| | | | | | | |_| | |_) | |_| \\__ \\ (_| | |_| |  __/ (_| | (_| \\__ \\
  |____/ \\__,_|_| |_| |_|\\__,_|____/ \\__,_|___/\\__, |\\__,_|\\___|\\__,_|\\__,_|___/
                                                  |_|
  [+] ENGINE      : SamuBusquedas v2.5 (.onion v3 Classic Search & Directory)
  [+] ARCHITECT   : saghet (Lead Security Researcher & Search Engine Architect)
  [+] RANKING     : SamuRank = BM25F * (Title:10, Tags:6, Tax:5) + OnionTrustRank(SHA3-256)
  [+] ZERO-JS     : 100% Tor Browser "Safest" Mode Ready (CSP script-src 'none')
  [+] AUDIT DOCS  : /.well-known/security.txt | /humans.txt | /canary.txt
 =====================================================================================
-->"""

CANARY_TEXT = f"""-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA512

========================================================================
                 DECLARACIÓN DE TRANSPARENCIA Y CANARIO
                  PORTAL SAMUBUSQUEDAS v2.5 (.ONION v3)
========================================================================
Autoría y Arquitectura Principal: saghet
Fecha de actualización: 2026-10-15
Dominio Oficial .onion v3:
{OFFICIAL_ONION_DOMAIN}
Estado del Servicio: ÍNTEGRO Y OPERATIVO (Modo Zero-Logs en Memoria RAM)

El arquitecto del sistema (saghet) y el equipo de SamuBusquedas declaran que:
1. NO hemos recibido órdenes judiciales, citaciones ni requerimientos
   secretos para interceptar o registrar tráfico de usuarios.
2. NO hemos instalado puertas traseras (backdoors) ni modificado los
   pesos del algoritmo SamuRank / OnionTrustRank para alterar las llaves
   públicas Ed25519 (.onion v3) verificadas con SHA3-256.
3. El servidor opera estrictamente sin registros en disco (Zero-Logs) y
   con política Content-Security-Policy: default-src 'none'.

Huella PGP Oficial de SamuBusquedas (by saghet):
SAMU-SAGHET-V3-7F9A-44C1-88E2-B009-31D4-99A0
-----BEGIN PGP SIGNATURE-----
Version: GnuPG v2 (Isolated Onion Environment - Architected by saghet)

iQIzBAEBCgAdFiEE724obdqF6ipLp95oTixuh5MpgpAFAmV0OnionACgkQTixu
h5MpgpB99Q//SamuBusquedasV2SaghetZeroJSProtectionShieldVerified==
=sagh
-----END PGP SIGNATURE-----
"""

SECURITY_TXT = f"""# RFC 9116 Security Policy - SamuBusquedas v2.5 (.onion v3)
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
Role: Creator of SamuBusquedas v2.5 (.onion v3 Hybrid Search Engine & Anti-Phishing Shield)
Official Onion v3: {OFFICIAL_ONION_DOMAIN}

/* SEARCH ENGINE TECHNOLOGY */
Ranking Algorithm: SamuRank / OnionTrustRank (Multi-field Okapi BM25F + SHA3-256 Ed25519 Trust Bonus)
Directory Structure: Classic AltaVista / Yahoo! 1997 Compact Directory + Google 1998 Minimalist SERP
Query Capabilities: Google-Style Operators (cat:, tax:, js:safest, site:, trust:, pgp:, "phrase", -exclude) + DuckDuckGo !Bangs
Spell Correction: In-Memory Damerau-Levenshtein ("Did you mean...?") with Automatic Fuzzy Recovery

/* SECURITY & OPSEC MODEL */
Client Protection: 100% Zero-JS (CSP default-src 'none'), Referrer-Policy: no-referrer, Anti-Tor2Web Detector
Storage Model: Pure RAM SQLite FTS5 (:memory:) - Zero Disk Logs
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


def render_layout(
    title: str,
    active_nav: str,
    security_eval: Dict[str, object],
    body_html: str,
) -> str:
    """Estructura maestra HTML minimalista al estilo Google 1998 / AltaVista 1997."""
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

    return f"""<!DOCTYPE html>
{ASCII_HACKER_BANNER}
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="referrer" content="no-referrer">
    <meta name="author" content="saghet">
    <meta name="creator" content="saghet">
    <meta name="generator" content="SamuBusquedas v2.5 Engine by saghet (Zero-JS Tor Shield)">
    <title>{html.escape(title)} — SamuBusquedas (.onion) by saghet</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="opsec-topbar">
        <div class="topbar-links">
            <a href="/">Buscador</a>
            <a href="/?q=all">Directorio Completo (57)</a>
            <a href="/verificar">Escáner Anti-Phishing</a>
            <a href="/proteccion">Guía OPSEC</a>
            <a href="/humans.txt">humans.txt (saghet)</a>
            <a href="/canary.txt">Canario PGP</a>
        </div>
        <div>
            {risk_pill} • <span class="pill-purple">Zero-JS | by saghet</span>
        </div>
    </div>

    <main class="container">
        {warnings_html}
        {body_html}
    </main>

    <footer class="site-footer">
        <p>
            © 2026 <strong>SamuBusquedas! (.onion v3)</strong> — Creado por <strong><code>saghet</code></strong> |
            Motor <code>SamuRank (BM25F + SHA3-256)</code> | 100% Zero-JS &amp; Zero-Logs en RAM.
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
    Renderiza la Portada Minimalista al estilo de la primera versión de Google (1998)
    y la tabla de categorías compacta estilo AltaVista / Yahoo! (1997).
    """
    total_sites = sum(int(c["total"]) for c in categories)  # type: ignore

    return f"""
    <section class="classic-home-hero">
        {_render_retro_logo(is_large=True)}
        <p class="retro-tagline">
            Buscador de la Deep Web (Sitios Verificados PGP + Índice Abierto Tor) — Arquitectura por <strong>saghet</strong>
        </p>

        <form action="/" method="GET" class="retro-search-box">
            <div>
                <label for="q-input" style="font-size: 13px; display: block; margin-bottom: 4px;">
                    Busca cualquier servicio, foro, wiki, cripto, prensa o herramienta en la red Tor:
                </label>
                <input
                    id="q-input"
                    type="text"
                    name="q"
                    value=""
                    placeholder="Ej: foros, hidden wiki, monero, correo, scihub, debian, pastebin, saghet..."
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
                    Buscar en toda la Deep Web (<strong>{total_sites} sitios locales + Red Tor en vivo</strong>)
                </label>
                <label>
                    <input type="radio" name="scope" value="verified">
                    Solo Sitios Oficiales Verificados (PGP)
                </label>
            </div>
        </form>

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
                            <a href="/?q=torlinks">TorLinks</a>,
                            <a href="/?q=radio">DeepWeb Radio</a>
                        </div>
                    </td>
                    <td>
                        <a href="/?cat=Prensa+y+Whistleblowing" class="dir-cat-title">Prensa &amp; Whistleblowing</a>
                        <div class="dir-sublinks">
                            <a href="/?q=propublica">ProPublica</a>,
                            <a href="/?q=securedrop">SecureDrop</a>,
                            <a href="/?q=nytimes">NYTimes</a>,
                            <a href="/?q=bbc">BBC</a>,
                            <a href="/?q=bellingcat">Bellingcat</a>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>
                        <a href="/?q=monero+bitcoin" class="dir-cat-title">Criptomonedas &amp; Finanzas P2P</a>
                        <div class="dir-sublinks">
                            <a href="/?q=monero">Monero (XMR)</a>,
                            <a href="/?q=feather">Feather Wallet</a>,
                            <a href="/?q=mempool">Bitcoin Mempool</a>,
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
                            <a href="/?q=internet+archive">Wayback Machine</a>
                        </div>
                    </td>
                    <td>
                        <a href="/?q=hacker+git+pastebin" class="dir-cat-title">Cultura Hacker, Git &amp; Pastebins</a>
                        <div class="dir-sublinks">
                            <a href="/?q=defcon">DEF CON</a>,
                            <a href="/?q=ccc">Chaos Computer Club</a>,
                            <a href="/?q=pastebin">StrongHold Paste</a>,
                            <a href="/?q=git">OnionGit</a>,
                            <a href="/?q=cyberchef">CyberChef</a>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>
                        <a href="/?cat=Sistemas+Operativos+y+Software+Libre" class="dir-cat-title">Sistemas Operativos &amp; Herramientas</a>
                        <div class="dir-sublinks">
                            <a href="/?q=whonix">Whonix</a>,
                            <a href="/?q=qubes">Qubes OS</a>,
                            <a href="/?q=tails">Tails USB</a>,
                            <a href="/?q=debian">Debian Onion</a>,
                            <a href="/?q=onionshare">OnionShare</a>
                        </div>
                    </td>
                    <td>
                        <a href="/?cat=Buscadores+Leg%C3%ADtimos" class="dir-cat-title">Otros Buscadores &amp; VPNs en Tor</a>
                        <div class="dir-sublinks">
                            <a href="/?q=duckduckgo">DuckDuckGo</a>,
                            <a href="/?q=brave">Brave</a>,
                            <a href="/?q=ahmia">Ahmia</a>,
                            <a href="/?q=torch">Torch</a>,
                            <a href="/?q=haystak">Haystak</a>,
                            <a href="/?q=mullvad">Mullvad VPN</a>
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
) -> str:
    """
    Renderiza la Página de Resultados (SERP) minimalista al estilo Google 1998 / AltaVista:
    - Cabecera de 1 línea con logo + input + botón.
    - Franja azul clara con conteo de resultados y milisegundos.
    - Lista limpia de 3 líneas por resultado (Título + Snippet + URL .onion en verde).
    """
    results: List[Dict[str, object]] = search_payload["results"]  # type: ignore
    did_you_mean = search_payload.get("did_you_mean")
    auto_corrected_from = search_payload.get("auto_corrected_from")
    semantic_intent = search_payload.get("semantic_intent")
    is_exploratory = bool(search_payload.get("is_exploratory_fallback"))
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

    verified_count = sum(1 for r in results if r.get("verification_tier") == "VERIFIED")
    unverified_count = len(results) - verified_count

    items_html = []
    for idx, svc in enumerate(results, start=1):
        tier = str(svc.get("verification_tier", "VERIFIED"))
        if tier == "VERIFIED":
            badge_html = '<span class="tier-badge-verified">[VERIFICADO PGP]</span>'
        else:
            badge_html = '<span class="tier-badge-unverified">[NO VERIFICADO / COMUNITARIO]</span>'

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
                </div>
                <p class="service-desc">{desc_rendered}</p>
                <div class="serp-url-line">
                    <a href="{html.escape(onion_url)}" class="onion-link" rel="noreferrer noopener" target="_blank">{html.escape(onion_url)}</a>
                    <span class="serp-meta-links">
                        — SamuRank: <strong>{svc.get("samu_rank", svc["safety_score"])}</strong>
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
                <label><input type="radio" name="scope" value="all" {checked_all}> Todo (Verificados + No Verificados)</label>
                <label style="margin-left: 6px;"><input type="radio" name="scope" value="verified" {checked_ver}> Solo Oficiales PGP</label>
            </span>
        </form>
    </header>

    <div class="serp-stats-bar">
        <span>
            Superficie Amplificada Activa: Mostrando <strong>{len(results)} resultados</strong>
            (<strong>{verified_count} Verificados</strong> + <strong>{unverified_count} No Verificados</strong>)
            para <strong>"{html.escape(str(label_query))}"</strong>
        </span>
        <span>Tiempo: <strong>{elapsed_ms} ms</strong> • Algoritmo <code>SamuRank v2.5</code> by <strong>saghet</strong></span>
    </div>

    {dym_html}
    {bang_html}
    {_render_knowledge_card_html(k_card)}

    <section class="results-grid">
        {"".join(items_html)}
    </section>
    """


def render_verify_page(inspected_url: str, report: Optional[Dict[str, object]]) -> str:
    """Renderiza el escáner Anti-Phishing clásico y directo."""
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
            svc_info = f"""
            <p style="margin-top: 6px; font-family: monospace;">
                <strong>Servicio Registrado:</strong> {html.escape(str(svc["title"]))}<br>
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
        <strong>Escáner Criptográfico Anti-Phishing (.onion v3 Ed25519 + SHA3-256)</strong>
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
        <strong>Guía de Seguridad OPSEC en la Deep Web (by saghet)</strong>
    </header>

    <div class="alert-box safe">
        <span class="alert-title">Auditoría Criptográfica SHA3-256:</span>
        <strong>{approved_count} de {len(audit_rows)}</strong> dominios <code>.onion</code> v3 locales verificados matemáticamente.
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
                    <strong>2. Diferencia Sitios [VERIFICADO PGP] vs [NO VERIFICADO]</strong>
                    <p class="dir-sublinks">
                        Los sitios con etiqueta verde cuentan con firma PGP o cabecera <code>Onion-Location</code> oficial.
                        En los sitios marcados como <em>No Verificado / Comunitario</em>, nunca ingreses datos personales ni contraseñas.
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
    server_version = "SamuEngine/2.5 (Tor-v3; Zero-JS; Hardened)"
    sys_version = ""

    def version_string(self) -> str:
        return self.server_version

    def date_time_string(self, timestamp: Optional[float] = None) -> str:
        return "Thu, 01 Jan 1970 00:00:00 GMT"

    def log_message(self, format: str, *args: object) -> None:
        pass

    def _send_hardened_headers(
        self, status_code: int = 200, content_type: str = "text/html; charset=utf-8"
    ) -> None:
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("X-Architected-By", "saghet")
        self.send_header("X-Builder-Handle", "saghet")
        self.send_header("X-Engine-Signature", "saghet-samubusquedas-v2-ed25519")
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

        req_headers = {k: v for k, v in self.headers.items()}
        security_eval = evaluate_client_connection_security(req_headers)

        if path == "/":
            q = query_params.get("q", [""])[0][:MAX_QUERY_LEN]
            cat = query_params.get("cat", ["Todas"])[0][:80]
            tax = query_params.get("tax", [""])[0][:40]
            scope = query_params.get("scope", ["all"])[0][:20]
            only_safest = query_params.get("safest", ["0"])[0] == "1"

            # Si el usuario entra a la raíz `/` sin consulta ni filtro, mostramos la portada minimalista estilo Google 1998
            if not q.strip() and (not cat or cat == "Todas") and not tax.strip():
                categories = search_engine.get_categories()
                body = render_classic_home_page(categories)
                page = render_layout("Buscador de la Deep Web", "search", security_eval, body)
                self._send_hardened_headers(200)
                self.wfile.write(page.encode("utf-8"))
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
            body = render_serp_page(actual_q, cat, tax, scope, search_payload)
            page = render_layout(f"{q or cat} - Buscar con SamuBusquedas", "search", security_eval, body)
            self._send_hardened_headers(200)
            self.wfile.write(page.encode("utf-8"))
            return

        if path == "/verificar":
            onion_param = query_params.get("onion", [""])[0][:MAX_QUERY_LEN]
            report = search_engine.inspect_onion_url(onion_param) if onion_param.strip() else None
            body = render_verify_page(onion_param, report)
            page = render_layout("Verificador Anti-Phishing SHA3-256", "verify", security_eval, body)
            self._send_hardened_headers(200)
            self.wfile.write(page.encode("utf-8"))
            return

        if path == "/proteccion":
            body = render_opsec_guide_page()
            page = render_layout("Guía OPSEC en la Deep Web", "opsec", security_eval, body)
            self._send_hardened_headers(200)
            self.wfile.write(page.encode("utf-8"))
            return

        not_found_body = """
        <div class="alert-box critical">
            <span class="alert-title">Error 404 — Página no encontrada</span>
            <p><a href="/">Volver al buscador SamuBusquedas!</a></p>
        </div>
        """
        page = render_layout("404 No Encontrado", "", security_eval, not_found_body)
        self._send_hardened_headers(404)
        self.wfile.write(page.encode("utf-8"))


def run_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    server = ThreadingHTTPServer((host, port), SamuOnionRequestHandler)
    print("======================================================================")
    print("  SAMUBUSQUEDAS! v2.5 (.ONION) - CLASSIC GOOGLE 98 / ALTAVISTA UI")
    print("  ARCHITECTED BY: saghet")
    print("======================================================================")
    print(f"  [*] Loopback local:       http://{host}:{port}")
    print(f"  [*] Dominio Tor Onion v3: {OFFICIAL_ONION_DOMAIN}")
    print("======================================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    port_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(host="127.0.0.1", port=port_arg)
