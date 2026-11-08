"""
Gamer Search Engine - Vistas y Renderizado de Componentes UI
============================================================
Maquetación modular en HTML5 / CSS3 Dark Theme para las 9 secciones:
1. Videojuegos
2. Trucos y Secretos
3. ROMs y Preservación
4. Emuladores
5. Mods
6. Comunidades (Prioritaria)
7. Guías y Tutoriales
8. Investigación Avanzada (OSINT)
9. Favoritos e Historial
Además de la portada destacada, fichas técnicas y comparador de versiones.
"""

import html
import urllib.parse
from typing import Any, Dict, List, Optional
from gamer_service import (
    CHEAT_CATEGORY_LABELS,
    PRESERVATION_TYPE_LABELS,
    COMMUNITY_TYPE_LABELS,
)


def _platform_badge(platform_name: str) -> str:
    p = platform_name.lower()
    if "nintendo" in p or "switch" in p:
        cls = "badge-nintendo"
    elif "playstation" in p or "ps" in p:
        cls = "badge-playstation"
    elif "xbox" in p:
        cls = "badge-xbox"
    elif any(r in p for r in ("retro", "nes", "snes", "n64", "sega", "atari")):
        cls = "badge-retro"
    else:
        cls = "badge-multi"
    return f'<span class="badge-platform {cls}">{html.escape(platform_name)}</span>'


def render_header(active_nav: str = "home") -> str:
    nav_items = [
        ("home", "/", "🔍 Buscador", False),
        ("juegos", "/juegos", "🎮 Videojuegos", False),
        ("trucos", "/trucos", "⚡ Trucos & Secretos", False),
        ("preservacion", "/preservacion", "🏛️ ROMs & Preservación", False),
        ("emuladores", "/emuladores", "🕹️ Emuladores", False),
        ("mods", "/mods", "🛠️ Mods & Parches", False),
        ("comunidades", "/comunidades", "👥 Comunidades", True),
        ("guias", "/guias", "📖 Guías & 100%", False),
        ("investigacion", "/investigacion", "🛰️ OSINT Web", False),
        ("favoritos", "/favoritos", "⭐ Favoritos & Historial", False),
    ]

    links_html = []
    for nav_id, url, label, is_special in nav_items:
        active_cls = " active" if active_nav == nav_id else ""
        special_cls = " special" if is_special else ""
        links_html.append(f'<a href="{url}" class="nav-link{active_cls}{special_cls}">{label}</a>')

    return f"""
    <header class="site-header">
        <div class="topbar-container">
            <div class="brand-wrapper">
                <a href="/" class="brand-logo">
                    <span class="logo-icon">🎮</span> GAMER SEARCH ENGINE
                </a>
                <span class="version-tag">v2.0 PRO</span>
            </div>
            <nav class="main-nav">
                {"".join(links_html)}
            </nav>
        </div>
    </header>
    """


def render_footer() -> str:
    return """
    <footer class="site-footer">
        <p>
            © 2026 <strong>Gamer Search Engine</strong> — Motor Inteligente de Videojuegos, Trucos y Comunidades.
        </p>
        <p style="margin-top: 6px; font-size: 12px;">
            Ecosistemas Prioritarios: <strong>Nintendo Switch</strong> • <strong>PlayStation 5</strong> • <strong>Xbox Series X/S</strong> • <strong>Retro & Preservación</strong>.
            Cero enlaces maliciosos • Verificación Criptográfica y Filtro Anti-Malware Activo.
        </p>
    </footer>
    """


def render_layout(title: str, active_nav: str, content_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#0a0c13">
    <title>{html.escape(title)} — Gamer Search Engine</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    {render_header(active_nav)}
    <main class="page-container">
        {content_html}
    </main>
    {render_footer()}
</body>
</html>"""


def render_search_hero(
    query: str = "",
    action_url: str = "/",
    active_platform: str = "Todas",
    subtitle: str = "Localiza videojuegos, trucos, guías, ROMs legales, emuladores y comunidades gamer."
) -> str:
    pills = [
        ("Todas", "🌐 Todas"),
        ("Nintendo Switch", "🔴 Nintendo Switch"),
        ("PlayStation 5", "🔵 PlayStation 5"),
        ("Xbox Series X", "🟢 Xbox Series X/S"),
        ("Retro", "🟡 Retro & Clásicos")
    ]
    pills_html = []
    for p_id, p_label in pills:
        active_cls = " active" if active_platform == p_id else ""
        p_extra = ""
        if "Nintendo" in p_id:
            p_extra = " pill-nintendo"
        elif "PlayStation" in p_id:
            p_extra = " pill-playstation"
        elif "Xbox" in p_id:
            p_extra = " pill-xbox"
        elif "Retro" in p_id:
            p_extra = " pill-retro"

        pill_url = f"{action_url}?q={urllib.parse.quote(query)}&platform={urllib.parse.quote(p_id)}"
        pills_html.append(f'<a href="{pill_url}" class="platform-pill{p_extra}{active_cls}">{p_label}</a>')

    safe_q = html.escape(query)

    return f"""
    <section class="search-hero-box">
        <div class="hero-header">
            <h1 class="hero-title">Buscador Inteligente de Videojuegos &amp; Comunidades</h1>
            <p class="hero-subtitle">{html.escape(subtitle)}</p>
        </div>
        <form action="{action_url}" method="GET" class="search-form">
            <input type="hidden" name="platform" value="{html.escape(active_platform)}">
            <div class="search-input-wrapper">
                <span class="search-icon-decor">⚡</span>
                <input
                    type="text"
                    name="q"
                    value="{safe_q}"
                    placeholder="Ej: 'trucos Zelda Tears of the Kingdom', 'comunidades Elden Ring', 'emulador PS2', 'Metroid'..."
                    class="main-search-input"
                    autofocus
                >
                <button type="submit" class="search-submit-btn">
                    <span>Buscar</span> ➔
                </button>
            </div>
            <div class="platform-pills-row">
                {"".join(pills_html)}
            </div>
        </form>
    </section>
    """


# --- RENDERIZADO DE TARJETAS ---

def render_game_card(g: Dict[str, Any]) -> str:
    platforms_html = "".join(_platform_badge(p) for p in g.get("platforms", []))
    genres_html = " ".join(f'<span class="game-tag">{html.escape(gen)}</span>' for gen in g.get("genres", []))
    highlighted_summary = g.get("highlighted_summary") or html.escape(g.get("summary", ""))

    return f"""
    <div class="game-card">
        <div>
            <div class="game-card-header">
                <h3 class="game-title">{html.escape(g.get("title", ""))}</h3>
                <span class="game-rating-badge">★ {g.get("rating", 0.0):.0f}/100</span>
            </div>
            <div class="game-meta-row">
                <span>{g.get("release_year", "")}</span> •
                <span>{html.escape(g.get("developer", ""))}</span> •
                <span>{platforms_html}</span>
            </div>
            <p class="game-summary">{highlighted_summary}</p>
            <div class="game-tags-row">{genres_html}</div>
        </div>
        <div class="game-card-footer">
            <span style="color: var(--text-dim);">{html.escape(g.get("price_status", ""))}</span>
            <a href="/juego?id={g.get('id')}" class="btn-details">Ficha Técnica &amp; Trucos ➔</a>
        </div>
    </div>
    """


def render_cheat_card(c: Dict[str, Any]) -> str:
    cat_label = CHEAT_CATEGORY_LABELS.get(c.get("category", ""), c.get("category", "").title())
    content = c.get("highlighted_content") or html.escape(c.get("content", ""))

    return f"""
    <div class="cheat-card">
        <div class="cheat-card-header">
            <h3 class="cheat-title">{html.escape(c.get("title", ""))}</h3>
            <span class="cheat-category-badge">{html.escape(cat_label)}</span>
        </div>
        <div class="cheat-game-context">
            <strong>{html.escape(c.get("game_title", ""))}</strong> • {_platform_badge(c.get("platform", ""))}
        </div>
        <div class="cheat-content-box">{content}</div>
        <div class="cheat-footer-meta">
            <span>Fuente original: <strong>{html.escape(c.get("original_source", ""))}</strong></span>
            <span>Verificado: <code>{c.get("verified_date", "")}</code></span>
            <a href="{html.escape(c.get('source_url', '#'))}" target="_blank" rel="noopener" class="btn-details">Ver fuente oficial ↗</a>
        </div>
    </div>
    """


def render_community_card(comm: Dict[str, Any]) -> str:
    type_label = COMMUNITY_TYPE_LABELS.get(comm.get("platform_type", ""), comm.get("platform_type", "").title())
    games_text = ", ".join(comm.get("related_games", []))

    return f"""
    <div class="community-card">
        <div>
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <h3 class="community-name">{html.escape(comm.get("name", ""))}</h3>
                {_platform_badge(comm.get("platform", ""))}
            </div>
            <span class="community-members-badge">{html.escape(comm.get("members_display", ""))}</span>
            <div class="community-meta-list">
                <div><strong>Tipo:</strong> {html.escape(type_label)}</div>
                <div><strong>Temática:</strong> {html.escape(comm.get("theme", ""))}</div>
                <div><strong>Juegos:</strong> {html.escape(games_text)}</div>
                <div><strong>Actividad:</strong> {html.escape(comm.get("recent_activity", ""))}</div>
                <div><strong>Idioma:</strong> {html.escape(comm.get("language", ""))}</div>
            </div>
        </div>
        <div style="border-top: 1px solid rgba(255,255,255,0.05); padding-top: 12px; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 11.5px; color: var(--text-dim);">{html.escape(comm.get("entry_requirements", ""))}</span>
            <a href="{html.escape(comm.get('official_url', '#'))}" target="_blank" rel="noopener" class="btn-details" style="background-color: rgba(0,240,255,0.15); color: var(--cyan-accent);">Unirse / Explorar ↗</a>
        </div>
    </div>
    """


def render_preservation_card(p: Dict[str, Any]) -> str:
    type_label = PRESERVATION_TYPE_LABELS.get(p.get("item_type", ""), p.get("item_type", "").title())

    return f"""
    <div class="preservation-card">
        <div class="preservation-header">
            <h3 class="preservation-title">{html.escape(p.get("title", ""))}</h3>
            <span class="legal-badge-verified">✓ {html.escape(p.get("legal_status", ""))}</span>
        </div>
        <div style="font-size: 13px; color: var(--cyan-accent); margin-bottom: 8px;">
            {_platform_badge(p.get("platform", ""))} • <span style="color: var(--text-dim);">{html.escape(type_label)}</span>
        </div>
        <p style="font-size: 13.5px; color: var(--text-muted); margin-bottom: 12px;">
            {html.escape(p.get("description", ""))}
        </p>
        <div style="background-color: var(--bg-input); padding: 10px 14px; border-radius: 6px; font-size: 12px; margin-bottom: 12px;">
            <strong>Notas Técnicas:</strong> {html.escape(p.get("technical_notes", ""))}
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; flex-wrap: wrap; gap: 8px;">
            <span>Licencia: <code>{html.escape(p.get("license", ""))}</code></span>
            <span>Autor: <strong>{html.escape(p.get("developer_author", ""))}</strong></span>
            <a href="{html.escape(p.get('safe_download_url', p.get('source_url', '#')))}" target="_blank" rel="noopener" class="btn-details">Repositorio Oficial / Descarga Segura ↗</a>
        </div>
    </div>
    """


# --- VISTAS COMPLETAS ---

def render_home_view(stats: Dict[str, Any], featured_games: List[Dict[str, Any]], featured_cheats: List[Dict[str, Any]], top_communities: List[Dict[str, Any]]) -> str:
    hero = render_search_hero(
        query="",
        subtitle=f"Indexados: {stats.get('total_games', 0)} videojuegos • {stats.get('total_cheats', 0)} trucos y trofeos • {stats.get('total_preservation', 0)} emuladores legales • {stats.get('total_communities', 0)} comunidades verificadas."
    )

    games_html = "".join(render_game_card(g) for g in featured_games[:6])
    cheats_html = "".join(render_cheat_card(c) for c in featured_cheats[:4])
    comm_html = "".join(render_community_card(comm) for comm in top_communities[:4])

    return f"""
    {hero}
    
    <section style="margin-bottom: 36px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <h2 style="font-size: 20px; font-weight: 700;">🎮 Videojuegos Destacados (Nintendo, PS5, Xbox Series X/S)</h2>
            <a href="/juegos">Ver catálogo completo ({stats.get('total_games', 0)}) ➔</a>
        </div>
        <div class="cards-grid">
            {games_html}
        </div>
    </section>

    <section style="margin-bottom: 36px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <h2 style="font-size: 20px; font-weight: 700;">⚡ Trucos Recientes, Glitches &amp; Trofeos</h2>
            <a href="/trucos">Ver todos los trucos ➔</a>
        </div>
        <div class="cards-list">
            {cheats_html}
        </div>
    </section>

    <section>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <h2 style="font-size: 20px; font-weight: 700;">👥 Comunidades Gamer Verificadas (Reddit &amp; Discord)</h2>
            <a href="/comunidades">Explorar comunidades ➔</a>
        </div>
        <div class="cards-grid">
            {comm_html}
        </div>
    </section>
    """


def render_smart_search_results_view(query: str, smart_res: Dict[str, Any], platform_filter: str = "Todas") -> str:
    hero = render_search_hero(query=query, active_platform=platform_filter)
    intent = smart_res.get("intent", {})

    # Tarjeta de Inteligencia Artificial
    ai_card_html = ""
    if intent:
        conf = int(intent.get("confidence", 0.8) * 100)
        sources = intent.get("recommended_sources", [])
        sources_html = " ".join(f'<span class="source-tag">{html.escape(s)}</span>' for s in sources)
        ai_card_html = f"""
        <div class="ai-intel-card">
            <div class="ai-card-header">
                <span class="ai-card-title">🤖 Inteligencia Semántica Gamer: Análisis de Consulta</span>
                <span class="ai-confidence-pill">Confianza IA: {conf}%</span>
            </div>
            <p class="ai-summary-text">{intent.get("natural_language_summary", "")}</p>
            <div class="ai-sources-row">
                <span>Fuentes recomendadas por IA:</span>
                {sources_html}
            </div>
        </div>
        """

    # Alerta de ciberseguridad si la consulta es sospechosa
    sec_alert_html = ""
    if intent.get("is_suspicious"):
        sec_alert_html = f"""
        <div class="security-alert-box">
            <span class="sec-alert-icon">🛡️</span>
            <div>
                <div class="sec-alert-title">Advertencia de Seguridad y Protección Gamer</div>
                <p>{html.escape(intent.get("suspicious_reason", ""))}</p>
            </div>
        </div>
        """

    counts = smart_res.get("counts", {})
    total_hits = smart_res.get("total_hits", 0)
    elapsed = smart_res.get("elapsed_ms", 0.0)

    # Tabs
    tabs_html = f"""
    <div class="results-tabs-bar">
        <a href="#tab-juegos" class="results-tab active">🎮 Videojuegos <span class="tab-count">{counts.get('games', 0)}</span></a>
        <a href="#tab-trucos" class="results-tab">⚡ Trucos &amp; Secretos <span class="tab-count">{counts.get('cheats', 0)}</span></a>
        <a href="#tab-preservacion" class="results-tab">🏛️ Preservación &amp; Emulación <span class="tab-count">{counts.get('preservation', 0)}</span></a>
        <a href="#tab-comunidades" class="results-tab">👥 Comunidades <span class="tab-count">{counts.get('communities', 0)}</span></a>
    </div>
    """

    games_html = "".join(render_game_card(g) for g in smart_res.get("games", []))
    cheats_html = "".join(render_cheat_card(c) for c in smart_res.get("cheats", []))
    pres_html = "".join(render_preservation_card(p) for p in smart_res.get("preservation", []))
    comm_html = "".join(render_community_card(comm) for comm in smart_res.get("communities", []))

    return f"""
    {hero}
    {sec_alert_html}
    {ai_card_html}
    
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
        <h2 style="font-size: 18px; color: var(--text-dim);">
            Resultados para <strong style="color: #ffffff;">"{html.escape(query)}"</strong> ({total_hits} coincidencias en {elapsed:.1f} ms)
        </h2>
    </div>

    {tabs_html}

    <section id="tab-juegos" style="margin-bottom: 30px;">
        <h3 style="font-size: 16px; margin-bottom: 14px; color: var(--cyan-accent);">🎮 Videojuegos Relacionados</h3>
        <div class="cards-grid">
            {games_html if games_html else '<p style="color: var(--text-dim);">No se encontraron videojuegos específicos para este término.</p>'}
        </div>
    </section>

    <section id="tab-trucos" style="margin-bottom: 30px;">
        <h3 style="font-size: 16px; margin-bottom: 14px; color: var(--purple-accent);">⚡ Trucos, Glitches y Secretos</h3>
        <div class="cards-list">
            {cheats_html if cheats_html else '<p style="color: var(--text-dim);">No se encontraron trucos específicos.</p>'}
        </div>
    </section>

    <section id="tab-preservacion" style="margin-bottom: 30px;">
        <h3 style="font-size: 16px; margin-bottom: 14px; color: var(--green-accent);">🏛️ Preservación, Emulación y Homebrew Legal</h3>
        <div class="cards-list">
            {pres_html if pres_html else '<p style="color: var(--text-dim);">No se encontraron emuladores o proyectos de preservación.</p>'}
        </div>
    </section>

    <section id="tab-comunidades" style="margin-bottom: 30px;">
        <h3 style="font-size: 16px; margin-bottom: 14px; color: var(--cyan-accent);">👥 Comunidades Gamer y Foros</h3>
        <div class="cards-grid">
            {comm_html if comm_html else '<p style="color: var(--text-dim);">No se encontraron comunidades específicas.</p>'}
        </div>
    </section>
    """


def render_game_detail_view(detail_payload: Dict[str, Any]) -> str:
    game = detail_payload["game"]
    cheats = detail_payload.get("cheats", [])
    communities = detail_payload.get("communities", [])

    platforms_html = "".join(_platform_badge(p) for p in game.get("platforms", []))
    genres_html = " • ".join(game.get("genres", []))
    editions_html = ", ".join(game.get("editions", []))
    dlcs_html = ", ".join(game.get("dlcs", [])) if game.get("dlcs") else "Ninguno reportado"
    patches_html = ", ".join(game.get("updates_patches", []))

    cheats_html = "".join(render_cheat_card(c) for c in cheats)
    comm_html = "".join(render_community_card(comm) for comm in communities)

    return f"""
    <div class="detail-hero">
        <a href="/juegos" style="font-size: 13px; margin-bottom: 12px; display: inline-block;">⬅ Volver a Videojuegos</a>
        <div class="detail-title-row">
            <div>
                <h1 class="detail-main-title">{html.escape(game.get("title", ""))}</h1>
                <div style="margin-top: 8px;">{platforms_html} • <span style="color: var(--text-dim);">{game.get("release_year", "")}</span></div>
            </div>
            <span class="game-rating-badge" style="font-size: 16px; padding: 6px 14px;">★ {game.get("rating", 0.0):.0f} / 100 ({html.escape(game.get("rating_source", ""))})</span>
        </div>
        <p style="font-size: 15px; color: var(--text-muted); line-height: 1.6; margin-bottom: 20px;">
            {html.escape(game.get("summary", ""))}
        </p>

        <h3 style="font-size: 16px; color: var(--cyan-accent); margin-top: 24px;">📊 Ficha Técnica &amp; Comparativa de Versiones</h3>
        <table class="specs-table">
            <tbody>
                <tr><th>Desarrollador / Publisher</th><td>{html.escape(game.get("developer", ""))} / {html.escape(game.get("publisher", ""))}</td></tr>
                <tr><th>Género(s)</th><td>{html.escape(genres_html)}</td></tr>
                <tr><th>Ediciones Disponibles</th><td>{html.escape(editions_html)}</td></tr>
                <tr><th>DLCs y Expansiones</th><td>{html.escape(dlcs_html)}</td></tr>
                <tr><th>Parches y Actualizaciones</th><td>{html.escape(patches_html)}</td></tr>
                <tr><th>Compatibilidad de Hardware</th><td>{html.escape(game.get("compatibility", ""))}</td></tr>
                <tr><th>Requisitos Técnicos</th><td><code>{html.escape(game.get("technical_requirements", ""))}</code></td></tr>
                <tr><th>Precio y Disponibilidad</th><td>{html.escape(game.get("price_status", ""))}</td></tr>
                <tr><th>Región</th><td>{html.escape(game.get("region", "Global"))}</td></tr>
            </tbody>
        </table>
    </div>

    <section style="margin-bottom: 30px;">
        <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 16px;">⚡ Trucos y Guías para este Juego ({len(cheats)})</h2>
        <div class="cards-list">
            {cheats_html if cheats_html else '<p style="color: var(--text-dim);">No hay trucos registrados todavía para este título.</p>'}
        </div>
    </section>

    <section>
        <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 16px;">👥 Comunidades y Foros de Jugadores ({len(communities)})</h2>
        <div class="cards-grid">
            {comm_html if comm_html else '<p style="color: var(--text-dim);">No hay comunidades específicas vinculadas.</p>'}
        </div>
    </section>
    """


def render_favorites_history_view(favorites: List[Dict[str, Any]], history: List[Dict[str, Any]]) -> str:
    fav_items = []
    for f in favorites:
        fav_items.append(f"""
        <div style="background-color: var(--bg-card); padding: 16px; border-radius: 8px; border: 1px solid var(--border-subtle); display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong style="color: #ffffff; font-size: 16px;">{html.escape(f.get("title", ""))}</strong>
                <div style="font-size: 13px; color: var(--text-dim);">{html.escape(f.get("subtitle", ""))}</div>
            </div>
            <a href="{html.escape(f.get('url', '#'))}" class="btn-details">Abrir ➔</a>
        </div>
        """)

    hist_items = []
    for h in history:
        hist_items.append(f"""
        <li style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between;">
            <a href="/?q={urllib.parse.quote(h.get('query', ''))}">🔍 {html.escape(h.get('query', ''))}</a>
            <span style="font-size: 12px; color: var(--text-dim);">{h.get('results_count', 0)} resultados</span>
        </li>
        """)

    return f"""
    <div style="margin-bottom: 30px;">
        <h1 style="font-size: 28px; font-weight: 800; margin-bottom: 8px;">⭐ Favoritos e Historial de Búsquedas</h1>
        <p style="color: var(--text-muted);">Gestiona tus juegos seguidos, trucos guardados y consultas recientes en almacenamiento local seguro.</p>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
        <section>
            <h2 style="font-size: 18px; font-weight: 700; margin-bottom: 14px; color: var(--gold-accent);">⭐ Elementos Guardados ({len(favorites)})</h2>
            <div style="display: flex; flex-direction: column; gap: 12px;">
                {"".join(fav_items) if fav_items else '<p style="color: var(--text-dim);">Aún no has guardado favoritos. Haz clic en guardar en cualquier videojuego o truco.</p>'}
            </div>
        </section>

        <section>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <h2 style="font-size: 18px; font-weight: 700; color: var(--cyan-accent);">🕒 Consultas Recientes ({len(history)})</h2>
            </div>
            <ul style="list-style: none;">
                {"".join(hist_items) if hist_items else '<li style="color: var(--text-dim);">No hay búsquedas en el historial.</li>'}
            </ul>
        </section>
    </div>
    """


# --- VISTAS DE MÓDULOS CON FILTROS DINÁMICOS ---

def render_games_module_view(query: str, payload: Dict[str, Any], filter_opts: Dict[str, Any], cur_filters: Dict[str, str]) -> str:
    hero = render_search_hero(query=query, action_url="/juegos", active_platform=cur_filters.get("platform", "Todas"), subtitle="Catálogo completo de videojuegos con filtros avanzados.")

    # Dropdowns de filtros
    plat_opts = "".join(f'<option value="{p}" {"selected" if cur_filters.get("platform") == p else ""}>{p}</option>' for p in filter_opts["platforms"])
    genre_opts = "".join(f'<option value="{g}" {"selected" if cur_filters.get("genre") == g else ""}>{g}</option>' for g in filter_opts["genres"])
    year_opts = "".join(f'<option value="{y}" {"selected" if cur_filters.get("year") == y else ""}>{y}</option>' for y in filter_opts["years"])

    filter_bar = f"""
    <form action="/juegos" method="GET" class="filter-controls-card">
        <input type="hidden" name="q" value="{html.escape(query)}">
        <div class="filter-group">
            <span class="filter-label">Plataforma:</span>
            <select name="platform" class="filter-select" onchange="this.form.submit()">{plat_opts}</select>
        </div>
        <div class="filter-group">
            <span class="filter-label">Género:</span>
            <select name="genre" class="filter-select" onchange="this.form.submit()">{genre_opts}</select>
        </div>
        <div class="filter-group">
            <span class="filter-label">Año:</span>
            <select name="year" class="filter-select" onchange="this.form.submit()">{year_opts}</select>
        </div>
        <div class="filter-group">
            <span class="filter-label">Ordenar por:</span>
            <select name="sort" class="filter-select" onchange="this.form.submit()">
                <option value="relevance" {"selected" if cur_filters.get("sort_by") == "relevance" else ""}>Relevancia</option>
                <option value="rating_desc" {"selected" if cur_filters.get("sort_by") == "rating_desc" else ""}>Mejor Valorados (Rating)</option>
                <option value="year_desc" {"selected" if cur_filters.get("sort_by") == "year_desc" else ""}>Más Recientes</option>
                <option value="title_asc" {"selected" if cur_filters.get("sort_by") == "title_asc" else ""}>Nombre (A-Z)</option>
            </select>
        </div>
        <button type="submit" class="btn-details" style="padding: 6px 14px;">Filtrar</button>
    </form>
    """

    games_html = "".join(render_game_card(g) for g in payload.get("results", []))
    cnt = payload.get("count", 0)

    return f"""
    {hero}
    {filter_bar}
    <div style="margin-bottom: 16px; color: var(--text-dim);">Mostrando <strong>{cnt}</strong> videojuegos encontrados:</div>
    <div class="cards-grid">
        {games_html if games_html else '<p style="color: var(--text-dim);">No se encontraron videojuegos con los filtros seleccionados.</p>'}
    </div>
    """


def render_cheats_module_view(query: str, payload: Dict[str, Any], filter_opts: Dict[str, Any], cur_filters: Dict[str, str]) -> str:
    hero = render_search_hero(query=query, action_url="/trucos", active_platform=cur_filters.get("platform", "Todas"), subtitle="Trucos, códigos, easter eggs, glitches conocidos y trofeos de PS5 / logros de Xbox.")

    cat_options = ['<option value="Todas">Todas las categorías</option>']
    for c in filter_opts["cheat_categories"]:
        sel = "selected" if cur_filters.get("category") == c["id"] else ""
        cat_options.append(f'<option value="{c["id"]}" {sel}>{c["label"]}</option>')

    filter_bar = f"""
    <form action="/trucos" method="GET" class="filter-controls-card">
        <input type="hidden" name="q" value="{html.escape(query)}">
        <div class="filter-group">
            <span class="filter-label">Categoría:</span>
            <select name="category" class="filter-select" onchange="this.form.submit()">{"".join(cat_options)}</select>
        </div>
        <button type="submit" class="btn-details">Aplicar Filtro</button>
    </form>
    """

    cheats_html = "".join(render_cheat_card(c) for c in payload.get("results", []))

    return f"""
    {hero}
    {filter_bar}
    <div style="margin-bottom: 16px; color: var(--text-dim);">Mostrando <strong>{payload.get('count', 0)}</strong> trucos y guías verificadas:</div>
    <div class="cards-list">
        {cheats_html if cheats_html else '<p style="color: var(--text-dim);">No se encontraron trucos con los filtros seleccionados.</p>'}
    </div>
    """


def render_preservation_module_view(query: str, payload: Dict[str, Any], filter_opts: Dict[str, Any], cur_filters: Dict[str, str]) -> str:
    hero = render_search_hero(query=query, action_url="/preservacion", active_platform=cur_filters.get("platform", "Todas"), subtitle="Preservación digital, emuladores oficiales, homebrew de dominio público y parches limpios.")

    type_options = ['<option value="Todos">Todos los tipos</option>']
    for p in filter_opts["preservation_types"]:
        sel = "selected" if cur_filters.get("item_type") == p["id"] else ""
        type_options.append(f'<option value="{p["id"]}" {sel}>{p["label"]}</option>')

    filter_bar = f"""
    <form action="/preservacion" method="GET" class="filter-controls-card">
        <input type="hidden" name="q" value="{html.escape(query)}">
        <div class="filter-group">
            <span class="filter-label">Tipo de Recurso:</span>
            <select name="type" class="filter-select" onchange="this.form.submit()">{"".join(type_options)}</select>
        </div>
        <button type="submit" class="btn-details">Filtrar</button>
    </form>
    """

    pres_html = "".join(render_preservation_card(p) for p in payload.get("results", []))

    return f"""
    {hero}
    {filter_bar}
    <div style="margin-bottom: 16px; color: var(--text-dim);">Mostrando <strong>{payload.get('count', 0)}</strong> recursos de preservación legalmente verificados:</div>
    <div class="cards-list">
        {pres_html if pres_html else '<p style="color: var(--text-dim);">No se encontraron recursos con los filtros seleccionados.</p>'}
    </div>
    """


def render_communities_module_view(query: str, payload: Dict[str, Any], filter_opts: Dict[str, Any], cur_filters: Dict[str, str]) -> str:
    hero = render_search_hero(query=query, action_url="/comunidades", active_platform=cur_filters.get("platform", "Todas"), subtitle="Encuentra comunidades gamer activas en Reddit, Discord oficial, Foros y Speedrun.com.")

    type_options = ['<option value="Todos">Todos los tipos</option>']
    for ct in filter_opts["community_types"]:
        sel = "selected" if cur_filters.get("platform_type") == ct["id"] else ""
        type_options.append(f'<option value="{ct["id"]}" {sel}>{ct["label"]}</option>')

    filter_bar = f"""
    <form action="/comunidades" method="GET" class="filter-controls-card">
        <input type="hidden" name="q" value="{html.escape(query)}">
        <div class="filter-group">
            <span class="filter-label">Tipo de Comunidad:</span>
            <select name="type" class="filter-select" onchange="this.form.submit()">{"".join(type_options)}</select>
        </div>
        <button type="submit" class="btn-details">Filtrar</button>
    </form>
    """

    comm_html = "".join(render_community_card(comm) for comm in payload.get("results", []))

    return f"""
    {hero}
    {filter_bar}
    <div style="margin-bottom: 16px; color: var(--text-dim);">Mostrando <strong>{payload.get('count', 0)}</strong> comunidades gamer verificadas:</div>
    <div class="cards-grid">
        {comm_html if comm_html else '<p style="color: var(--text-dim);">No se encontraron comunidades con los filtros seleccionados.</p>'}
    </div>
    """


def render_osint_investigation_view(query: str, osint_payload: Dict[str, Any]) -> str:
    hero = render_search_hero(query=query, action_url="/investigacion", subtitle="Investigación avanzada en fuentes abiertas: Speedrun.com, Internet Archive y GitHub.")

    results = osint_payload.get("results", [])
    cnt = osint_payload.get("total", 0)

    items_html = []
    for r in results:
        sec = r.get("security", {})
        reputation = sec.get("reputation_score", 100.0)
        tier = sec.get("safety_tier", "CONFIABLE_VERIFICADO")
        badge_cls = "legal-badge-verified" if tier == "CONFIABLE_VERIFICADO" else "game-tag"

        items_html.append(f"""
        <div class="preservation-card" style="border-left-color: var(--cyan-accent);">
            <div class="preservation-header">
                <h3 class="preservation-title">{html.escape(r.get("title", ""))}</h3>
                <span class="{badge_cls}">Seguridad: {reputation:.0f}/100</span>
            </div>
            <div style="font-size: 13px; color: var(--cyan-accent); margin-bottom: 6px;">
                Fuente: <strong>{html.escape(r.get("source", ""))}</strong> • {html.escape(r.get("category", ""))}
            </div>
            <p style="font-size: 13.5px; color: var(--text-muted); margin-bottom: 12px;">
                {html.escape(r.get("description", ""))}
            </p>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 12px; color: var(--text-dim);">{html.escape(sec.get("domain", ""))}</span>
                <a href="{html.escape(r.get('url', '#'))}" target="_blank" rel="noopener" class="btn-details">Explorar Fuente Externa ↗</a>
            </div>
        </div>
        """)

    return f"""
    {hero}
    <div style="margin-bottom: 16px; color: var(--text-dim);">
        Resultados de Investigación OSINT en fuentes abiertas ({cnt} encontrados en vivo):
    </div>
    <div class="cards-list">
        {"".join(items_html) if items_html else '<p style="color: var(--text-dim);">Ingresa un término para investigar en vivo en Speedrun.com, Internet Archive y GitHub.</p>'}
    </div>
    """

