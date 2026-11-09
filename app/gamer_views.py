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
        ("library", "/library", "📚 Gaming Library", True),
        ("home", "/", "🔍 Buscador", False),
        ("juegos", "/juegos", "🎮 Videojuegos", False),
        ("trucos", "/trucos", "⚡ Trucos & Secretos", False),
        ("preservacion", "/preservacion", "🏛️ ROMs & Preservación", False),
        ("emuladores", "/emuladores", "🕹️ Emuladores", False),
        ("mods", "/mods", "🛠️ Mods & Parches", False),
        ("comunidades", "/comunidades", "👥 Comunidades", False),
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


def render_search_intelligence_panel(intel: Dict[str, Any], elapsed_ms: float) -> str:
    """Renderiza el Panel de Transparencia y Telemetría en Vivo (Fase 8)."""
    if not intel:
        return ""

    queried = intel.get("queried_providers", [])
    successful = intel.get("successful_providers", [])
    failed = intel.get("failed_providers", [])
    errors = intel.get("errors", {})
    gen_queries = intel.get("generated_queries", [])
    languages = intel.get("languages_used", ["Español (ES)", "Inglés (EN)"])
    depth = intel.get("search_depth", "Profundidad 1 (Oleada Federada Concurrente)")
    platforms = intel.get("platforms_covered", ["Multiplataforma"])
    total_eval = intel.get("total_evaluated", 0)
    total_acc = intel.get("total_accepted", 0)
    total_disc = intel.get("total_discarded_low_quality", 0)
    discarded_items = intel.get("discarded_items", [])
    new_domains = intel.get("new_domains_discovered", [])
    catalog_domains = intel.get("total_catalog_domains", 0)

    # Pills de idiomas
    lang_pills = " ".join(f'<span style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid #0284c7; border-radius: 4px; padding: 2px 8px; font-size: 11.5px; font-weight: bold;">{html.escape(l)}</span>' for l in languages)

    # Pills de plataformas
    plat_pills = " ".join(f'<span style="background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid #7c3aed; border-radius: 4px; padding: 2px 8px; font-size: 11.5px; font-weight: bold;">{html.escape(p)}</span>' for p in platforms)

    # Proveedores
    prov_items = []
    for p in queried:
        is_ok = p in successful
        err_msg = errors.get(p, "")
        badge = '<span style="background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; border-radius: 4px; padding: 2px 6px; font-size: 11px;">CONECTADO</span>' if is_ok else f'<span style="background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; border-radius: 4px; padding: 2px 6px; font-size: 11px;">FALLO ({html.escape(err_msg or "Timeout")})</span>'
        prov_items.append(f'<li style="display: flex; justify-content: space-between; align-items: center; padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 12.5px;"><span>{html.escape(p)}</span>{badge}</li>')

    # Consultas generadas
    q_pills = "".join(f'<div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #334155; border-radius: 4px; padding: 4px 8px; font-size: 12px; color: #cbd5e1; font-family: monospace;">🔍 {html.escape(q)}</div>' for q in gen_queries)

    # Elementos descartados
    if discarded_items:
        disc_rows = []
        for it in discarded_items:
            disc_rows.append(f"""
            <div style="background: rgba(239, 68, 68, 0.08); border-left: 3px solid #ef4444; padding: 6px 10px; margin-bottom: 6px; border-radius: 4px; font-size: 12px;">
                <div style="font-weight: bold; color: #fca5a5;">{html.escape(it.get('title', 'Sin título'))}</div>
                <div style="color: #94a3b8; font-size: 11px;">Score: {it.get('score', 0.0)}/100 • Motivo: <span style="color: #f87171;">{html.escape(it.get('reason', ''))}</span></div>
            </div>
            """)
        disc_html = "".join(disc_rows)
    else:
        disc_html = '<div style="color: #94a3b8; font-size: 12px;">No hubo resultados descartados por baja calidad en esta consulta.</div>'

    # Errores de red
    if errors:
        err_list = "".join(f"<li><strong>{html.escape(k)}:</strong> {html.escape(v)}</li>" for k, v in errors.items())
        err_notice = f"""
        <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; border-radius: 6px; padding: 8px 12px; margin-top: 10px; font-size: 12px; color: #fca5a5;">
            <strong>⚠️ Reporte de Conectividad de Red:</strong>
            <ul style="margin: 4px 0 0 16px;">{err_list}</ul>
        </div>
        """
    else:
        err_notice = '<div style="color: #34d399; font-size: 12px; margin-top: 6px;">✔ Todas las conexiones externas respondieron sin errores de red.</div>'

    return f"""
    <div style="background: linear-gradient(180deg, #0d1322 0%, #0a0d16 100%); border: 1px solid #1e293b; border-radius: 10px; padding: 18px; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.4);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; border-bottom: 1px solid #1e293b; padding-bottom: 10px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 18px;">📡</span>
                <h3 style="font-size: 15px; font-weight: 800; color: #38bdf8; letter-spacing: 0.5px; margin: 0; text-transform: uppercase;">
                    Search Intelligence — Telemetría y Transparencia en Vivo
                </h3>
            </div>
            <span style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid #0284c7; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;">
                ⚡ {elapsed_ms:.1f} ms
            </span>
        </div>

        <!-- Métricas KPI Principales -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; margin-bottom: 14px;">
            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid #1e293b; border-radius: 6px; padding: 8px 12px;">
                <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">Motores Consultados</div>
                <div style="font-size: 17px; font-weight: bold; color: #ffffff;">{len(queried)} <span style="font-size: 12px; color: #10b981;">({len(successful)} OK)</span></div>
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid #1e293b; border-radius: 6px; padding: 8px 12px;">
                <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">Profundidad</div>
                <div style="font-size: 12.5px; font-weight: bold; color: #cbd5e1; margin-top: 3px;">{html.escape(depth)}</div>
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid #1e293b; border-radius: 6px; padding: 8px 12px;">
                <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">Dominios Catalogados</div>
                <div style="font-size: 17px; font-weight: bold; color: #38bdf8;">{catalog_domains + len(new_domains)} <span style="font-size: 12px; color: #94a3b8;">(+{len(new_domains)} nuevos)</span></div>
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid #1e293b; border-radius: 6px; padding: 8px 12px;">
                <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">Filtro Calidad (&gt;= 35)</div>
                <div style="font-size: 17px; font-weight: bold; color: #10b981;">{total_acc} <span style="font-size: 12px; color: #f87171;">/ {total_disc} descartados</span></div>
            </div>
        </div>

        <!-- Secciones Colapsables de Transparencia -->
        <div style="display: flex; flex-direction: column; gap: 8px;">
            <details style="background: rgba(15, 23, 42, 0.5); border: 1px solid #1e293b; border-radius: 6px; padding: 8px 12px;">
                <summary style="cursor: pointer; font-size: 12.5px; font-weight: bold; color: #93c5fd; outline: none;">
                    📋 Expansión Automática de Consultas e Idiomas ({len(gen_queries)} variantes generadas)
                </summary>
                <div style="margin-top: 10px;">
                    <div style="margin-bottom: 8px; font-size: 12px; color: #94a3b8;">
                        Idiomas procesados: {lang_pills}
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 6px;">
                        {q_pills}
                    </div>
                </div>
            </details>

            <details style="background: rgba(15, 23, 42, 0.5); border: 1px solid #1e293b; border-radius: 6px; padding: 8px 12px;">
                <summary style="cursor: pointer; font-size: 12.5px; font-weight: bold; color: #93c5fd; outline: none;">
                    🔌 Fuentes Consultadas y Estado de Red ({len(successful)} activas, {len(failed)} con fallo)
                </summary>
                <div style="margin-top: 10px;">
                    <ul style="list-style: none; margin: 0; padding: 0;">
                        {"".join(prov_items)}
                    </ul>
                    {err_notice}
                </div>
            </details>

            <details style="background: rgba(15, 23, 42, 0.5); border: 1px solid #1e293b; border-radius: 6px; padding: 8px 12px;">
                <summary style="cursor: pointer; font-size: 12.5px; font-weight: bold; color: #93c5fd; outline: none;">
                    🚫 Auditoría Anti-Basura: Resultados Descartados ({total_disc} items)
                </summary>
                <div style="margin-top: 10px;">
                    {disc_html}
                </div>
            </details>

            <details style="background: rgba(15, 23, 42, 0.5); border: 1px solid #1e293b; border-radius: 6px; padding: 8px 12px;">
                <summary style="cursor: pointer; font-size: 12.5px; font-weight: bold; color: #93c5fd; outline: none;">
                    🎮 Cobertura por Plataforma y Arquitecturas
                </summary>
                <div style="margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px;">
                    {plat_pills}
                </div>
            </details>
        </div>
    </div>
    """


def render_smart_search_results_view(query: str, smart_res: Dict[str, Any], platform_filter: str = "Todas") -> str:
    hero = render_search_hero(query=query, active_platform=platform_filter)
    intent = smart_res.get("intent", {})
    elapsed = smart_res.get("elapsed_ms", 0.0)
    intel_html = render_search_intelligence_panel(smart_res.get("search_intelligence", {}), elapsed)

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
    {intel_html}
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
    comp = detail_payload.get("complementary", {})
    multilingual = detail_payload.get("multilingual", {})
    cheats_local = detail_payload.get("cheats", [])
    comm_local = detail_payload.get("communities", [])

    def _esc(val: Any) -> str:
        return html.escape(str(val if val is not None else ""))

    title = game.get("title", "")
    platforms = game.get("platforms", []) or []
    platforms_html = "".join(_platform_badge(p) for p in platforms)
    genres_html = " • ".join(str(g) for g in (game.get("genres") or []))
    score_5d = game.get("score_5d", {}) or {}
    rating = game.get("rating", 0.0) or 0.0
    sales = game.get("sales_documented", "Ventas no reportadas") or "Ventas no reportadas"
    summary = game.get("summary", "") or ""
    rationale = score_5d.get("rationale", "") or ""

    # Fuentes consultadas
    sources = comp.get("consulted_sources", []) or game.get("consulted_sources", []) or []

    # Trucos y secretos
    cheats_items = comp.get("cheats_and_secrets", []) or []
    # Guías
    guides_items = comp.get("guides_and_walkthroughs", []) or []
    # Comunidades
    comm_items = comp.get("communities", []) or []
    # Mods
    mods_items = comp.get("mods_and_development", []) or []
    # Emulación
    pres_info = comp.get("preservation_and_emulation", {}) or {}
    # Noticias
    news_items = comp.get("news_and_updates", []) or []

    # Construcción de HTML para cada pestaña
    cheats_html = "".join([f"""
    <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); padding: 16px; border-radius: 8px; margin-bottom: 12px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12px; font-weight:700; color:var(--cyan-accent); text-transform:uppercase;">{_esc(c.get('category',''))}</span>
            <span style="font-size:11px; background:rgba(0,255,136,0.1); color:#00ff88; padding:3px 8px; border-radius:12px;">{_esc(c.get('epistemic_status','Confirmado'))}</span>
        </div>
        <h4 style="margin: 8px 0 6px 0; color:#ffffff; font-size:15px;">{_esc(c.get('title',''))}</h4>
        <p style="font-size:13px; color:var(--text-muted); line-height:1.5;">{_esc(c.get('description',''))}</p>
        <div style="margin-top:10px;"><a href="{_esc(c.get('source_url','#'))}" target="_blank" rel="noopener noreferrer" style="font-size:12px; color:var(--accent-glow);">Ver investigación completa en fuente ➔</a></div>
    </div>
    """ for c in cheats_items])

    guides_html = "".join([f"""
    <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); padding: 16px; border-radius: 8px; margin-bottom: 12px;">
        <span style="font-size:12px; font-weight:700; color:#ffb703; text-transform:uppercase;">{_esc(g.get('type',''))}</span>
        <h4 style="margin: 8px 0 6px 0; color:#ffffff; font-size:15px;">{_esc(g.get('title',''))}</h4>
        <p style="font-size:13px; color:var(--text-muted); line-height:1.5;">{_esc(g.get('description',''))}</p>
        <div style="margin-top:10px;"><a href="{_esc(g.get('url','#'))}" target="_blank" rel="noopener noreferrer" style="font-size:12px; color:var(--accent-glow);">Abrir guía oficial / comunitaria ➔</a></div>
    </div>
    """ for g in guides_items])

    comm_html = "".join([f"""
    <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); padding: 16px; border-radius: 8px; margin-bottom: 12px;">
        <span style="font-size:12px; font-weight:700; color:#80ffea; text-transform:uppercase;">{_esc(cm.get('platform',''))} • {_esc(cm.get('type',''))}</span>
        <h4 style="margin: 8px 0 6px 0; color:#ffffff; font-size:15px;">{_esc(cm.get('name',''))}</h4>
        <p style="font-size:13px; color:var(--text-muted); line-height:1.5;">{_esc(cm.get('description',''))}</p>
        <div style="margin-top:10px;"><a href="{_esc(cm.get('url','#'))}" target="_blank" rel="noopener noreferrer" style="font-size:12px; color:var(--accent-glow);">Unirse a la comunidad ➔</a></div>
    </div>
    """ for cm in comm_items])

    mods_html = "".join([f"""
    <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); padding: 16px; border-radius: 8px; margin-bottom: 12px;">
        <span style="font-size:12px; font-weight:700; color:#d4af37; text-transform:uppercase;">{_esc(m.get('source',''))}</span>
        <h4 style="margin: 8px 0 6px 0; color:#ffffff; font-size:15px;">{_esc(m.get('title',''))}</h4>
        <p style="font-size:13px; color:var(--text-muted); line-height:1.5;">{_esc(m.get('description',''))}</p>
        <div style="margin-top:10px;"><a href="{_esc(m.get('url','#'))}" target="_blank" rel="noopener noreferrer" style="font-size:12px; color:var(--accent-glow);">Explorar repositorio / descargas ➔</a></div>
    </div>
    """ for m in mods_items])

    sources_html = "".join([f"""
    <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); padding: 14px 18px; border-radius: 8px; margin-bottom: 10px; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <div style="font-weight:700; color:#ffffff; font-size:14px;">{_esc(s.get('name',''))}</div>
            <div style="font-size:12px; color:var(--text-dim); margin-top:2px;">{_esc(s.get('type','Fuente Independiente Contrastada'))} • Verificada</div>
        </div>
        <a href="{_esc(s.get('url','#'))}" target="_blank" rel="noopener noreferrer" class="btn-details" style="font-size:12px; padding:6px 12px;">Visitar Fuente ➔</a>
    </div>
    """ for s in sources])

    news_html = "".join([f"""
    <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); padding: 16px; border-radius: 8px; margin-bottom: 12px;">
        <span style="font-size:12px; font-weight:700; color:var(--cyan-accent);">{_esc(n.get('source',''))}</span>
        <h4 style="margin: 6px 0; color:#ffffff; font-size:15px;">{_esc(n.get('title',''))}</h4>
        <p style="font-size:13px; color:var(--text-muted); line-height:1.5;">{_esc(n.get('description',''))}</p>
        <div style="margin-top:8px;"><a href="{_esc(n.get('url','#'))}" target="_blank" rel="noopener noreferrer" style="font-size:12px; color:var(--accent-glow);">Leer artículo / registro ➔</a></div>
    </div>
    """ for n in news_items])

    # Multilingual queries preview
    languages = multilingual.get("languages", {}) or {}
    multilingual_html = f"""
    <div style="margin-top: 25px; padding: 18px; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px;">
        <h4 style="font-size: 14px; color: var(--cyan-accent); margin-bottom: 10px;">🌐 Búsqueda Multilingüe Expandida (Fase 8 / Sección 9)</h4>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; font-size: 12px;">
            <div>
                <strong style="color: #ff9e00;">Español (ES):</strong>
                <ul style="padding-left: 16px; margin-top: 4px; color: var(--text-dim);">
                    {"".join(f"<li>{_esc(q)}</li>" for q in languages.get('es', [])[:3])}
                </ul>
            </div>
            <div>
                <strong style="color: #64dfdf;">Inglés (EN):</strong>
                <ul style="padding-left: 16px; margin-top: 4px; color: var(--text-dim);">
                    {"".join(f"<li>{_esc(q)}</li>" for q in languages.get('en', [])[:3])}
                </ul>
            </div>
            <div>
                <strong style="color: #f72585;">Japonés (JA):</strong>
                <ul style="padding-left: 16px; margin-top: 4px; color: var(--text-dim);">
                    {"".join(f"<li>{_esc(q)}</li>" for q in languages.get('ja', [])[:3])}
                </ul>
            </div>
            <div>
                <strong style="color: #48cae4;">Portugués (PT):</strong>
                <ul style="padding-left: 16px; margin-top: 4px; color: var(--text-dim);">
                    {"".join(f"<li>{_esc(q)}</li>" for q in languages.get('pt', [])[:3])}
                </ul>
            </div>
        </div>
    </div>
    """

    return f"""
    <style>
        .tab-bar {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 20px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 10px;
        }}
        .tab-btn {{
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.1);
            color: var(--text-muted);
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.2s;
        }}
        .tab-btn:hover {{
            background: rgba(255,255,255,0.1);
            color: #ffffff;
        }}
        .tab-btn.active {{
            background: var(--cyan-accent);
            color: #0b0f19;
            border-color: var(--cyan-accent);
            box-shadow: 0 0 12px rgba(0,255,200,0.3);
        }}
        .tab-pane {{
            display: none;
            animation: fadeIn 0.3s ease-in-out;
        }}
        .tab-pane.active {{
            display: block;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(4px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .metric-pill {{
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            padding: 10px 14px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-pill strong {{
            display: block;
            font-size: 16px;
            color: #ffffff;
            margin-top: 4px;
        }}
    </style>

    <div class="detail-hero">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
            <a href="/library" style="font-size: 13px; color:var(--cyan-accent);">⬅ Volver a Gaming Library</a>
            <span style="font-size: 12px; color:var(--text-dim);">Ficha Individual de 24 Atributos • Verificado</span>
        </div>
        <div class="detail-title-row">
            <div>
                <h1 class="detail-main-title">{_esc(title)}</h1>
                <div style="margin-top: 8px;">{platforms_html} • <span style="color: var(--text-dim);">{game.get("release_year", "")}</span> • <span style="color:var(--text-dim);">{_esc(game.get("generation", ""))}</span></div>
            </div>
            <div style="text-align:right;">
                <span class="game-rating-badge" style="font-size: 16px; padding: 6px 14px;">★ {rating:.1f} / 100</span>
                <div style="font-size:11px; color:var(--text-dim); margin-top:4px;">Puntuación Multivariante 5D</div>
            </div>
        </div>
        <p style="font-size: 15px; color: var(--text-muted); line-height: 1.6; margin: 16px 0;">
            {_esc(summary)}
        </p>
        {f'<div style="background:rgba(0,255,200,0.05); border-left:3px solid var(--cyan-accent); padding:10px 14px; font-size:13px; color:#d0f0fd; border-radius:0 6px 6px 0; margin-bottom:16px;"><strong>Justificación de Ranking:</strong> {_esc(rationale)}</div>' if rationale else ''}
    </div>

    <!-- NAVEGACIÓN POR 8 PESTAÑAS (SECCIÓN 11) -->
    <div class="tab-bar">
        <button class="tab-btn active" onclick="switchGamerTab(event, 'tab-info')">1. 📊 Información General</button>
        <button class="tab-btn" onclick="switchGamerTab(event, 'tab-cheats')">2. ⚡ Trucos y Secretos</button>
        <button class="tab-btn" onclick="switchGamerTab(event, 'tab-guides')">3. 📖 Guías y 100%</button>
        <button class="tab-btn" onclick="switchGamerTab(event, 'tab-community')">4. 👥 Comunidades</button>
        <button class="tab-btn" onclick="switchGamerTab(event, 'tab-mods')">5. 🛠️ Mods &amp; Dev</button>
        <button class="tab-btn" onclick="switchGamerTab(event, 'tab-preservation')">6. 🏛️ Emulación Legal</button>
        <button class="tab-btn" onclick="switchGamerTab(event, 'tab-news')">7. 📢 Noticias</button>
        <button class="tab-btn" onclick="switchGamerTab(event, 'tab-sources')">8. 🔍 Fuentes ({len(sources)})</button>
    </div>

    <!-- PESTAÑA 1: INFORMACIÓN GENERAL -->
    <div id="tab-info" class="tab-pane active">
        <h3 style="font-size: 16px; color: var(--cyan-accent); margin-bottom: 14px;">⚖️ Desglose Multivariante de Puntuación 5D (Fase 3)</h3>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; margin-bottom: 24px;">
            <div class="metric-pill"><span style="font-size:11px; color:var(--text-dim);">Crítica (25%)</span><strong>{score_5d.get('critic_score', 0):.1f}</strong></div>
            <div class="metric-pill"><span style="font-size:11px; color:var(--text-dim);">Usuarios (25%)</span><strong>{score_5d.get('user_score', 0):.1f}</strong></div>
            <div class="metric-pill"><span style="font-size:11px; color:var(--text-dim);">Importancia (20%)</span><strong>{score_5d.get('historical_importance', 0):.1f}</strong></div>
            <div class="metric-pill"><span style="font-size:11px; color:var(--text-dim);">Ventas / Pop (15%)</span><strong>{score_5d.get('sales_popularity', 0):.1f}</strong></div>
            <div class="metric-pill"><span style="font-size:11px; color:var(--text-dim);">Comunidad (15%)</span><strong>{score_5d.get('community_activity', 0):.1f}</strong></div>
        </div>

        <h3 style="font-size: 16px; color: var(--cyan-accent); margin-bottom: 14px;">📋 Ficha Técnica Exhaustiva (24 Atributos Obligatorios)</h3>
        <table class="specs-table">
            <tbody>
                <tr><th>Nombre Oficial</th><td><strong>{_esc(title)}</strong></td></tr>
                <tr><th>Alias y Nombres Alternativos</th><td>{_esc(", ".join(game.get("aliases") or []))}</td></tr>
                <tr><th>Plataforma Canónica &amp; Generación</th><td>{_esc(", ".join(platforms))} ({_esc(game.get("generation", ""))})</td></tr>
                <tr><th>Fecha de Lanzamiento</th><td>{_esc(game.get("release_date", "No registrada"))}</td></tr>
                <tr><th>Desarrollador / Distribuidor</th><td>{_esc(game.get("developer", ""))} / {_esc(game.get("publisher", ""))}</td></tr>
                <tr><th>Género(s)</th><td>{_esc(genres_html)}</td></tr>
                <tr><th>Idiomas y Regiones</th><td>{_esc(", ".join(game.get("languages") or ["Español", "Inglés"]))} • {_esc(game.get("region", "Global"))}</td></tr>
                <tr><th>Ventas Oficiales Documentadas</th><td>{_esc(sales)}</td></tr>
                <tr><th>Posición en Ranking Oficial</th><td>#{game.get("rank_position", 1)} en su plataforma</td></tr>
                <tr><th>Características Técnicas</th><td>{_esc(", ".join(game.get("features") or ["Resolución nativa"]))}</td></tr>
                <tr><th>Requisitos Técnicos</th><td><code>{_esc(game.get("technical_requirements") or "18.2 GB de almacenamiento")}</code></td></tr>
                <tr><th>DLCs y Expansiones</th><td>{_esc(", ".join(game.get("dlcs") or []) if game.get("dlcs") else "Ninguno reportado")}</td></tr>
                <tr><th>Versiones y Ediciones</th><td>{_esc(", ".join(game.get("versions") or ["Física", "Digital"]))}</td></tr>
                <tr><th>Remasters y Remakes</th><td>{_esc(", ".join(game.get("remasters") or []) if game.get("remasters") else "Versión original preservada")}</td></tr>
                <tr><th>Compatibilidad Retroactiva</th><td>{_esc(str(game.get("backward_compatibility", {})))}</td></tr>
                <tr><th>Última Actualización Forense</th><td>{_esc(game.get("updated_date", "2026-11-08"))}</td></tr>
            </tbody>
        </table>

        {multilingual_html}
    </div>

    <!-- PESTAÑA 2: TRUCOS Y SECRETOS -->
    <div id="tab-cheats" class="tab-pane">
        <h3 style="font-size: 18px; color: #ffffff; margin-bottom: 16px;">⚡ Trucos, Glitches, Easter Eggs y Desbloqueables</h3>
        {cheats_html if cheats_html else '<p style="color:var(--text-dim);">No hay trucos registrados todavía para este título.</p>'}
    </div>

    <!-- PESTAÑA 3: GUÍAS Y WALKTHROUGHS -->
    <div id="tab-guides" class="tab-pane">
        <h3 style="font-size: 18px; color: #ffffff; margin-bottom: 16px;">📖 Guías Completas, Coleccionables y Trofeos al 100%</h3>
        {guides_html}
    </div>

    <!-- PESTAÑA 4: COMUNIDADES -->
    <div id="tab-community" class="tab-pane">
        <h3 style="font-size: 18px; color: #ffffff; margin-bottom: 16px;">👥 Comunidades Gamer, Discord, Reddit y Speedrunning</h3>
        {comm_html}
    </div>

    <!-- PESTAÑA 5: MODS Y DESARROLLO -->
    <div id="tab-mods" class="tab-pane">
        <h3 style="font-size: 18px; color: #ffffff; margin-bottom: 16px;">🛠️ Mods, Parches de Traducción y Decompilaciones</h3>
        {mods_html}
    </div>

    <!-- PESTAÑA 6: EMULACIÓN Y PRESERVACIÓN -->
    <div id="tab-preservation" class="tab-pane">
        <h3 style="font-size: 18px; color: #ffffff; margin-bottom: 16px;">🏛️ Emulación Verificada y Preservación Digital Legal</h3>
        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); padding: 18px; border-radius: 8px; margin-bottom: 16px;">
            <div style="font-size:12px; color:var(--cyan-accent); font-weight:700;">EMULADOR RECOMENDADO OFICIAL</div>
            <h4 style="margin:6px 0; color:#ffffff; font-size:16px;">{html.escape(pres_info.get('recommended_emulator', 'RetroArch'))}</h4>
            <p style="font-size:13px; color:var(--text-muted); margin-bottom:12px;">{html.escape(pres_info.get('compatibility_status', ''))}</p>
            <a href="{html.escape(pres_info.get('emulator_url', '#'))}" target="_blank" rel="noopener noreferrer" class="btn-details">Sitio Oficial de Descarga ➔</a>
        </div>
        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); padding: 18px; border-radius: 8px; margin-bottom: 16px;">
            <h4 style="color:#ffffff; font-size:15px; margin-bottom:8px;">📦 Guía de Volcado Legal y Ética de Preservación</h4>
            <p style="font-size:13px; color:var(--text-muted); line-height:1.5; margin-bottom:10px;">{html.escape(pres_info.get('legal_dumping_guide', ''))}</p>
            <div style="font-size:12px; color:#ff9e00; background:rgba(255,158,0,0.08); padding:10px 14px; border-radius:6px;">
                <strong>Aviso de Cumplimiento:</strong> {html.escape(pres_info.get('preservation_ethics_statement', ''))}
            </div>
        </div>
    </div>

    <!-- PESTAÑA 7: NOTICIAS -->
    <div id="tab-news" class="tab-pane">
        <h3 style="font-size: 18px; color: #ffffff; margin-bottom: 16px;">📢 Noticias, Actualizaciones y Récords Mundiales</h3>
        {news_html}
    </div>

    <!-- PESTAÑA 8: FUENTES ENCONTRADAS -->
    <div id="tab-sources" class="tab-pane">
        <h3 style="font-size: 18px; color: #ffffff; margin-bottom: 16px;">🔍 Fuentes Independientes Contrastadas (Mínimo 3 Verificadas)</h3>
        {sources_html}
    </div>

    <script>
    function switchGamerTab(evt, tabId) {{
        var panes = document.getElementsByClassName("tab-pane");
        for (var i = 0; i < panes.length; i++) {{
            panes[i].classList.remove("active");
        }}
        var btns = document.getElementsByClassName("tab-btn");
        for (var i = 0; i < btns.length; i++) {{
            btns[i].classList.remove("active");
        }}
        document.getElementById(tabId).classList.add("active");
        evt.currentTarget.classList.add("active");
    }}
    </script>
    """


def render_gaming_library_view(
    sub_section: str,
    selected_console: Optional[Dict[str, Any]],
    available_consoles: List[Dict[str, Any]],
    criteria: str,
    games: List[Dict[str, Any]]
) -> str:
    """Maquetación de la sección principal GAMING LIBRARY (Sección 11)."""
    subsections = [
        ("nintendo", "Nintendo"),
        ("playstation", "PlayStation"),
        ("xbox", "Xbox"),
        ("retro", "Consolas Retro & Portátiles"),
        ("generacion", "Mejores por Generación"),
        ("rankings_historicos", "Rankings Históricos"),
        ("nuevos_descubrimientos", "Nuevos Descubrimientos"),
        ("comunidades", "Comunidades Gamer")
    ]

    sub_nav_html = "".join([
        f'<a href="/library?sub={sid}" class="tab-btn{" active" if sub_section == sid else ""}" style="text-decoration:none;">{label}</a>'
        for sid, label in subsections
    ])

    cur_cid = selected_console.get("id", "") if selected_console else ""
    console_pills_html = "".join([
        f'<a href="/library?sub={sub_section}&console={c.get("id")}&criteria={criteria}" class="nav-pill{" active" if cur_cid == c.get("id") else ""}" style="padding:6px 14px; border-radius:20px; font-size:13px; text-decoration:none; background:{"var(--cyan-accent); color:#0b0f19; font-weight:700;" if cur_cid == c.get("id") else "rgba(255,255,255,0.05); color:var(--text-muted);"}">{html.escape(c.get("name",""))}</a>'
        for c in available_consoles
    ])

    criteria_options = [
        ("ranking_general", "Puntuación Multivariante 5D (Compuesta)"),
        ("mejores_valorados", "Mejores Valorados (Crítica + Jugadores)"),
        ("mas_populares", "Más Populares y Vendidos"),
        ("mayor_importancia_historica", "Mayor Importancia Histórica"),
        ("mejores_segun_comunidad", "Mejores Según la Comunidad Gamer")
    ]
    crit_opts_html = "".join([
        f'<option value="{cid}"{" selected" if criteria == cid else ""}>{label}</option>'
        for cid, label in criteria_options
    ])

    # Generar tarjetas para los 30 juegos
    cards_html = []
    for idx, g in enumerate(games, 1):
        g_id = g.get("id", "")
        g_title = g.get("title", "")
        g_year = g.get("release_year", "")
        g_rating = g.get("rating", 0.0)
        g_genres = " • ".join(g.get("genres", [])[:2])
        g_platforms = "".join(_platform_badge(p) for p in g.get("platforms", [])[:1])
        g_cover = g.get("cover_url", "")
        rank_pos = g.get("rank_position") or idx

        cards_html.append(f"""
        <div class="game-card" style="display:flex; flex-direction:column; justify-content:space-between; position:relative; overflow:hidden;">
            <div style="position:absolute; top:10px; left:10px; background:rgba(0,0,0,0.75); color:var(--cyan-accent); font-size:12px; font-weight:800; padding:3px 8px; border-radius:6px; border:1px solid rgba(0,255,200,0.3); z-index:2;">
                #{rank_pos}
            </div>
            <div>
                <div style="height:140px; background:linear-gradient(180deg, rgba(20,25,40,0.8), rgba(11,15,25,0.95)); display:flex; align-items:center; justify-content:center; border-radius:6px; margin-bottom:12px; overflow:hidden;">
                    <span style="font-size:42px; opacity:0.8;">🎮</span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
                    <h3 style="font-size:15px; font-weight:700; color:#ffffff; margin-bottom:4px; line-height:1.3;">
                        <a href="/juego?id={urllib.parse.quote(g_id)}" style="color:#ffffff; text-decoration:none;">{html.escape(g_title)}</a>
                    </h3>
                    <span class="game-rating-badge" style="font-size:13px; padding:3px 8px; white-space:nowrap;">★ {g_rating:.1f}</span>
                </div>
                <div style="font-size:12px; color:var(--text-dim); margin-top:4px;">
                    {g_year} • {html.escape(g_genres)}
                </div>
                <div style="margin-top:8px;">
                    {g_platforms}
                </div>
            </div>
            <div style="margin-top:14px; padding-top:10px; border-top:1px solid rgba(255,255,255,0.06); display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:11px; color:var(--text-dim);">8 Pestañas Forenses</span>
                <a href="/juego?id={urllib.parse.quote(g_id)}" class="btn-details" style="font-size:12px; padding:5px 10px;">Ver Ficha ➔</a>
            </div>
        </div>
        """)

    return f"""
    <div style="margin-bottom: 24px;">
        <h1 style="font-size: 28px; font-weight: 800; color: #ffffff; display:flex; align-items:center; gap:10px;">
            <span>📚</span> GAMING LIBRARY
        </h1>
        <p style="color: var(--text-muted); font-size: 14px; margin-top: 6px;">
            Directorio maestro histórico: los 30 mejores videojuegos por plataforma para la generación actual y las cuatro anteriores con ponderación 5D.
        </p>
    </div>

    <!-- SUBSECCIONES OBLIGATORIAS -->
    <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:20px;">
        {sub_nav_html}
    </div>

    <!-- SELECTOR DE PLATAFORMA DE LA SUBSECCIÓN -->
    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.08); padding:16px 20px; border-radius:10px; margin-bottom:24px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px;">
            <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center;">
                <span style="font-size:13px; font-weight:700; color:var(--text-dim); margin-right:6px;">Plataforma:</span>
                {console_pills_html}
            </div>

            <form method="GET" action="/library" style="display:flex; align-items:center; gap:8px;">
                <input type="hidden" name="sub" value="{html.escape(sub_section)}">
                <input type="hidden" name="console" value="{html.escape(cur_cid)}">
                <label for="crit-select" style="font-size:12px; color:var(--text-dim);">Ordenar por:</label>
                <select id="crit-select" name="criteria" onchange="this.form.submit()" style="background:#161c2e; color:#ffffff; border:1px solid rgba(255,255,255,0.15); border-radius:6px; padding:6px 12px; font-size:13px;">
                    {crit_opts_html}
                </select>
            </form>
        </div>
    </div>

    <!-- BANNER DE LA CONSOLA SELECCIONADA -->
    {f'''
    <div style="margin-bottom:20px; display:flex; justify-content:space-between; align-items:flex-end;">
        <div>
            <h2 style="font-size:22px; font-weight:700; color:#ffffff;">{html.escape(selected_console.get("name",""))}</h2>
            <div style="font-size:13px; color:var(--text-dim); margin-top:2px;">
                {selected_console.get("generation_label","")} • Lanzamiento: {selected_console.get("release_year","")} • {selected_console.get("lifespan","")}
            </div>
        </div>
        <span style="font-size:13px; color:var(--cyan-accent); font-weight:600;">Mostrando {len(games)} títulos verificados</span>
    </div>
    ''' if selected_console else ''}

    <!-- GRID DE 30 JUEGOS VISUALES -->
    <div class="cards-grid">
        {"".join(cards_html) if cards_html else '<p style="color:var(--text-dim);">No hay videojuegos disponibles para este criterio.</p>'}
    </div>
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
    hero = render_search_hero(query=query, action_url="/investigacion", subtitle="Modo Investigador Gamer: Análisis forense de secretos, glitches, mitos y desmentidos.")

    findings = osint_payload.get("findings", [])
    results = osint_payload.get("results", [])
    target_game = osint_payload.get("target_game", "")
    stats = osint_payload.get("stats", {})

    # Tarjetas de estadísticas de investigación
    stats_html = ""
    if stats:
        stats_html = f"""
        <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px;">
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 8px; padding: 8px 14px; font-size: 13px;">
                <span style="color: #34d399; font-weight: bold;">✔ Confirmado:</span> {stats.get('Confirmado', 0)}
            </div>
            <div style="background: rgba(59, 130, 246, 0.15); border: 1px solid #3b82f6; border-radius: 8px; padding: 8px 14px; font-size: 13px;">
                <span style="color: #60a5fa; font-weight: bold;">👥 Comunitario:</span> {stats.get('Documentado por comunidades', 0)}
            </div>
            <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid #f59e0b; border-radius: 8px; padding: 8px 14px; font-size: 13px;">
                <span style="color: #fbbf24; font-weight: bold;">⏳ Pendiente:</span> {stats.get('Pendiente de verificar', 0)}
            </div>
            <div style="background: rgba(236, 72, 153, 0.15); border: 1px solid #ec4899; border-radius: 8px; padding: 8px 14px; font-size: 13px;">
                <span style="color: #f472b6; font-weight: bold;">❓ Rumor:</span> {stats.get('Rumor', 0)}
            </div>
            <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; border-radius: 8px; padding: 8px 14px; font-size: 13px;">
                <span style="color: #f87171; font-weight: bold;">✖ Desmentido:</span> {stats.get('Desmentido', 0)}
            </div>
        </div>
        """

    findings_html = []
    status_colors = {
        "Confirmado": ("#10b981", "#34d399", "rgba(16, 185, 129, 0.2)"),
        "Documentado por comunidades": ("#3b82f6", "#60a5fa", "rgba(59, 130, 246, 0.2)"),
        "Pendiente de verificar": ("#f59e0b", "#fbbf24", "rgba(245, 158, 11, 0.2)"),
        "Rumor": ("#ec4899", "#f472b6", "rgba(236, 72, 153, 0.2)"),
        "Desmentido": ("#ef4444", "#f87171", "rgba(239, 68, 68, 0.2)"),
    }

    for f in findings:
        classification = f.get("classification", "Pendiente de verificar")
        border_c, text_c, bg_c = status_colors.get(classification, ("#64748b", "#94a3b8", "rgba(100, 116, 139, 0.2)"))

        sources_links = []
        for s in f.get("sources", []):
            sources_links.append(f'<a href="{html.escape(s.get("url", "#"))}" target="_blank" rel="noopener" style="color: var(--cyan-accent); text-decoration: underline; margin-right: 12px; font-size: 12px;">[{html.escape(s.get("type", "Fuente"))}] {html.escape(s.get("name", ""))} ↗</a>')
        sources_html = "".join(sources_links) if sources_links else '<span style="font-size: 12px; color: var(--text-dim);">Sin fuentes externas</span>'

        findings_html.append(f"""
        <div class="preservation-card" style="border-left: 4px solid {border_c}; margin-bottom: 16px;">
            <div class="preservation-header" style="margin-bottom: 8px;">
                <h3 class="preservation-title" style="font-size: 16px;">{html.escape(f.get("title", ""))}</h3>
                <span style="background: {bg_c}; color: {text_c}; border: 1px solid {border_c}; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: bold;">
                    {html.escape(classification.upper())}
                </span>
            </div>
            <div style="font-size: 12.5px; color: var(--cyan-accent); margin-bottom: 8px;">
                Categoría: <strong>{html.escape(f.get("category", ""))}</strong>
            </div>
            <div style="font-size: 13.5px; color: var(--text-muted); margin-bottom: 8px; line-height: 1.5;">
                <strong>Veredicto Técnico:</strong> {html.escape(f.get("verdict_rationale", ""))}
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); padding: 8px 12px; border-radius: 6px; font-size: 12.5px; color: var(--text-dim); margin-bottom: 10px; font-family: monospace;">
                <strong>Evidencia en Archivos/Scripts:</strong> {html.escape(f.get("technical_evidence", ""))}
            </div>
            <div style="margin-top: 8px; border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 8px;">
                <span style="font-size: 12px; color: var(--text-dim); margin-right: 8px;">Fuentes Originales:</span>
                {sources_html}
            </div>
        </div>
        """)

    # Si hay resultados estándar de OSINT, también incluirlos
    for r in results:
        sec = r.get("security", {})
        reputation = sec.get("reputation_score", 100.0)
        tier = sec.get("safety_tier", "CONFIABLE_VERIFICADO")
        badge_cls = "legal-badge-verified" if tier == "CONFIABLE_VERIFICADO" else "game-tag"

        findings_html.append(f"""
        <div class="preservation-card" style="border-left-color: var(--cyan-accent); margin-bottom: 14px;">
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

    total_count = len(findings) + len(results)
    banner_game = f" para <strong style='color: #ffffff;'>{html.escape(target_game)}</strong>" if target_game else ""

    return f"""
    {hero}
    {stats_html}
    <div style="margin-bottom: 16px; color: var(--text-dim);">
        Resultados de Investigación Forense Gamer{banner_game} ({total_count} hallazgos clasificados):
    </div>
    <div class="cards-list">
        {"".join(findings_html) if findings_html else '<p style="color: var(--text-dim);">Ingresa una consulta de investigación para analizar secretos, mitos y desmentidos (ej. <em>"Encuentra todos los secretos conocidos de GTA San Andreas"</em>).</p>'}
    </div>
    """

