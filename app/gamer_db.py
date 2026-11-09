"""
Gamer Search Engine - Motor de Base de Datos SQLite FTS5 Multifacético
======================================================================
Motor de indexación y búsqueda relacional + FTS5 para el ecosistema Gamer:
- Videojuegos (Nintendo, PS5, Xbox Series X/S, Retro)
- Trucos, Secretos, Guías, Trofeos y Logros
- Preservación Digital, Homebrew, Emuladores y Parches Legales
- Comunidades Gamer (Reddit, Discord, Foros, Speedrun)
- Favoritos e Historial de Búsquedas
"""

import json
import os
import re
import sqlite3
import threading
import time
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

from gamer_models import (
    GameRecord,
    CheatRecord,
    PreservationRecord,
    CommunityRecord,
)
from gamer_seed_data import GAMES_SEED, CHEATS_SEED, PRESERVATION_SEED, COMMUNITIES_SEED

_DB_LOCK = threading.RLock()


def normalize_gamer_query(text: str) -> str:
    """Elimina acentos y normaliza caracteres para búsquedas insensibles a diacríticos."""
    if not text:
        return ""
    nfd = unicodedata.normalize("NFD", text.lower())
    clean = "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")
    clean = re.sub(r"[^\w\s-]", " ", clean)
    return re.sub(r"\s+", " ", clean).strip()


def highlight_safe_snippet(text: str, query_tokens: List[str], max_len: int = 180) -> str:
    """Genera un fragmento resaltado seguro con <mark class="hl"> sin romper HTML."""
    if not text:
        return ""
    import html
    escaped = html.escape(text)
    if not query_tokens:
        return escaped[:max_len] + ("..." if len(escaped) > max_len else "")

    for token in query_tokens:
        tok = token.strip()
        if len(tok) < 2:
            continue
        pattern = re.compile(rf"(?i)\b({re.escape(html.escape(tok))})\b")
        escaped = pattern.sub(r'<mark class="hl">\1</mark>', escaped)

    # Si el texto es muy largo, recortar manteniendo el primer highlight si es posible
    if len(escaped) > max_len:
        mark_idx = escaped.find('<mark class="hl">')
        if mark_idx != -1 and mark_idx > 40:
            start = max(0, mark_idx - 30)
            end = min(len(escaped), start + max_len)
            prefix = "..." if start > 0 else ""
            suffix = "..." if end < len(escaped) else ""
            return prefix + escaped[start:end] + suffix
        return escaped[:max_len] + "..."
    return escaped


class GamerSearchEngineDB:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Base de datos persistente en directorio app
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(base_dir, "gamer_engine.db")
        else:
            self.db_path = db_path

        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()
        self._seed_initial_data()

    def _init_schema(self) -> None:
        with _DB_LOCK:
            cur = self._conn.cursor()
            # Tablas relacionales estructuradas con los 24 atributos requeridos
            cur.executescript("""
                CREATE TABLE IF NOT EXISTS games (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    aliases_json TEXT,
                    platforms_json TEXT,
                    canonical_platform_id TEXT,
                    generation TEXT,
                    generation_number INTEGER,
                    release_year INTEGER,
                    release_date TEXT,
                    developer TEXT,
                    publisher TEXT,
                    genres_json TEXT,
                    languages_json TEXT,
                    regions_released_json TEXT,
                    critic_score REAL DEFAULT 0.0,
                    user_score REAL DEFAULT 0.0,
                    sales_documented TEXT,
                    units_sold_millions REAL,
                    rank_position INTEGER DEFAULT 0,
                    summary TEXT,
                    features_json TEXT,
                    dlcs_json TEXT,
                    expansions_json TEXT,
                    versions_json TEXT,
                    remasters_json TEXT,
                    remakes_json TEXT,
                    backward_compatibility_json TEXT,
                    score_5d_json TEXT,
                    consulted_sources_json TEXT,
                    updated_date TEXT,
                    editions_json TEXT,
                    updates_patches_json TEXT,
                    compatibility TEXT,
                    technical_requirements TEXT,
                    rating REAL,
                    rating_source TEXT,
                    price_status TEXT,
                    cover_url TEXT,
                    screenshots_json TEXT,
                    tags_json TEXT,
                    region TEXT
                );

                CREATE TABLE IF NOT EXISTS cheats (
                    id TEXT PRIMARY KEY,
                    game_title TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    original_source TEXT,
                    source_url TEXT,
                    verified_date TEXT,
                    updated_date TEXT,
                    tags_json TEXT
                );

                CREATE TABLE IF NOT EXISTS preservation (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    game_title TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    developer_author TEXT,
                    source_url TEXT,
                    license TEXT,
                    legal_status TEXT NOT NULL,
                    download_safe INTEGER DEFAULT 1,
                    safe_download_url TEXT,
                    sha256 TEXT,
                    technical_notes TEXT
                );

                CREATE TABLE IF NOT EXISTS communities (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    related_games_json TEXT,
                    theme TEXT NOT NULL,
                    platform_type TEXT NOT NULL,
                    members_count INTEGER,
                    members_display TEXT,
                    recent_activity TEXT,
                    language TEXT,
                    official_url TEXT,
                    entry_requirements TEXT,
                    activity_level TEXT,
                    verified INTEGER DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    section TEXT DEFAULT 'all',
                    results_count INTEGER DEFAULT 0,
                    timestamp REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS favorites (
                    id TEXT PRIMARY KEY,
                    item_type TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    subtitle TEXT,
                    url TEXT,
                    saved_at REAL NOT NULL,
                    data_json TEXT
                );
            """)

            # Migración no destructiva de columnas añadidas para bases de datos existentes
            cur.execute("PRAGMA table_info(games);")
            existing_cols = {row[1] for row in cur.fetchall()}
            new_cols = [
                ("canonical_platform_id", "TEXT"),
                ("generation", "TEXT"),
                ("generation_number", "INTEGER"),
                ("screenshots_json", "TEXT"),
                ("languages_json", "TEXT"),
                ("regions_released_json", "TEXT"),
                ("critic_score", "REAL DEFAULT 0.0"),
                ("user_score", "REAL DEFAULT 0.0"),
                ("sales_documented", "TEXT"),
                ("units_sold_millions", "REAL"),
                ("rank_position", "INTEGER DEFAULT 0"),
                ("features_json", "TEXT"),
                ("expansions_json", "TEXT"),
                ("versions_json", "TEXT"),
                ("remasters_json", "TEXT"),
                ("remakes_json", "TEXT"),
                ("backward_compatibility_json", "TEXT"),
                ("score_5d_json", "TEXT"),
                ("consulted_sources_json", "TEXT"),
                ("updated_date", "TEXT"),
            ]
            for col_name, col_type in new_cols:
                if col_name not in existing_cols:
                    cur.execute(f"ALTER TABLE games ADD COLUMN {col_name} {col_type};")

            # Tablas virtuales FTS5 para búsqueda de texto completo con BM25
            cur.executescript("""
                CREATE VIRTUAL TABLE IF NOT EXISTS games_fts USING fts5(
                    id UNINDEXED,
                    title,
                    aliases,
                    platforms,
                    developer,
                    publisher,
                    genres,
                    summary,
                    tags,
                    tokenize='unicode61 remove_diacritics 2'
                );

                CREATE VIRTUAL TABLE IF NOT EXISTS cheats_fts USING fts5(
                    id UNINDEXED,
                    game_title,
                    platform,
                    category,
                    title,
                    content,
                    original_source,
                    tags,
                    tokenize='unicode61 remove_diacritics 2'
                );

                CREATE VIRTUAL TABLE IF NOT EXISTS preservation_fts USING fts5(
                    id UNINDEXED,
                    title,
                    game_title,
                    platform,
                    item_type,
                    description,
                    developer_author,
                    license,
                    technical_notes,
                    tokenize='unicode61 remove_diacritics 2'
                );

                CREATE VIRTUAL TABLE IF NOT EXISTS communities_fts USING fts5(
                    id UNINDEXED,
                    name,
                    platform,
                    related_games,
                    theme,
                    platform_type,
                    recent_activity,
                    language,
                    tokenize='unicode61 remove_diacritics 2'
                );
            """)
            self._conn.commit()

    def _seed_initial_data(self) -> None:
        with _DB_LOCK:
            cur = self._conn.cursor()
            cur.execute("SELECT COUNT(*) FROM games;")
            if cur.fetchone()[0] == 0:
                for g in GAMES_SEED:
                    self.insert_game(g)
            
            cur.execute("SELECT COUNT(*) FROM cheats;")
            if cur.fetchone()[0] == 0:
                for c in CHEATS_SEED:
                    self.insert_cheat(c)

            cur.execute("SELECT COUNT(*) FROM preservation;")
            if cur.fetchone()[0] == 0:
                for p in PRESERVATION_SEED:
                    self.insert_preservation(p)

            cur.execute("SELECT COUNT(*) FROM communities;")
            if cur.fetchone()[0] == 0:
                for comm in COMMUNITIES_SEED:
                    self.insert_community(comm)

    # --- INSERCIONES RELACIONALES + FTS5 ---
    def insert_game(self, g: GameRecord) -> None:
        with _DB_LOCK:
            cur = self._conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO games (
                    id, title, aliases_json, platforms_json, canonical_platform_id,
                    generation, generation_number, release_year, release_date,
                    developer, publisher, genres_json, languages_json, regions_released_json,
                    critic_score, user_score, sales_documented, units_sold_millions,
                    rank_position, summary, features_json, dlcs_json, expansions_json,
                    versions_json, remasters_json, remakes_json, backward_compatibility_json,
                    score_5d_json, consulted_sources_json, updated_date, editions_json,
                    updates_patches_json, compatibility, technical_requirements, rating,
                    rating_source, price_status, cover_url, screenshots_json, tags_json, region
                ) VALUES (
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?
                );
            """, (
                g.id, g.title, json.dumps(g.aliases), json.dumps(g.platforms), g.canonical_platform_id,
                g.generation, g.generation_number, g.release_year, g.release_date,
                g.developer, g.publisher, json.dumps(g.genres), json.dumps(g.languages), json.dumps(g.regions_released),
                g.critic_score, g.user_score, g.sales_documented, g.units_sold_millions,
                g.rank_position, g.summary, json.dumps(g.features), json.dumps(g.dlcs), json.dumps(g.expansions),
                json.dumps(g.versions), json.dumps(g.remasters), json.dumps(g.remakes), json.dumps(g.backward_compatibility),
                json.dumps(g.score_5d), json.dumps(g.consulted_sources), g.updated_date, json.dumps(getattr(g, 'editions', [])),
                json.dumps(getattr(g, 'updates_patches', [])), g.compatibility, g.technical_requirements, g.rating or g.critic_score,
                g.rating_source or "Metacritic / OpenCritic", g.price_status, g.cover_url, json.dumps(g.screenshots), json.dumps(g.tags), g.region
            ))
            # Sincronizar FTS5
            cur.execute("DELETE FROM games_fts WHERE id = ?;", (g.id,))
            cur.execute("""
                INSERT INTO games_fts (id, title, aliases, platforms, developer, publisher, genres, summary, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                g.id, g.title, " ".join(g.aliases), " ".join(g.platforms), g.developer, g.publisher,
                " ".join(g.genres), g.summary, " ".join(g.tags)
            ))
            self._conn.commit()

    def insert_cheat(self, c: CheatRecord) -> None:
        with _DB_LOCK:
            cur = self._conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO cheats (
                    id, game_title, platform, category, title, content, original_source, source_url, verified_date, updated_date, tags_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                c.id, c.game_title, c.platform, c.category, c.title, c.content, c.original_source, c.source_url, c.verified_date, c.updated_date, json.dumps(c.tags)
            ))
            cur.execute("DELETE FROM cheats_fts WHERE id = ?;", (c.id,))
            cur.execute("""
                INSERT INTO cheats_fts (id, game_title, platform, category, title, content, original_source, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                c.id, c.game_title, c.platform, c.category, c.title, c.content, c.original_source, " ".join(c.tags)
            ))
            self._conn.commit()

    def insert_preservation(self, p: PreservationRecord) -> None:
        with _DB_LOCK:
            cur = self._conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO preservation (
                    id, title, game_title, platform, item_type, description, developer_author, source_url, license, legal_status, download_safe, safe_download_url, sha256, technical_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                p.id, p.title, p.game_title, p.platform, p.item_type, p.description, p.developer_author, p.source_url, p.license, p.legal_status, 1 if p.download_safe else 0, p.safe_download_url, p.sha256, p.technical_notes
            ))
            cur.execute("DELETE FROM preservation_fts WHERE id = ?;", (p.id,))
            cur.execute("""
                INSERT INTO preservation_fts (id, title, game_title, platform, item_type, description, developer_author, license, technical_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                p.id, p.title, p.game_title, p.platform, p.item_type, p.description, p.developer_author, p.license, p.technical_notes
            ))
            self._conn.commit()

    def insert_community(self, comm: CommunityRecord) -> None:
        with _DB_LOCK:
            cur = self._conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO communities (
                    id, name, platform, related_games_json, theme, platform_type, members_count, members_display, recent_activity, language, official_url, entry_requirements, activity_level, verified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                comm.id, comm.name, comm.platform, json.dumps(comm.related_games), comm.theme, comm.platform_type, comm.members_count, comm.members_display, comm.recent_activity, comm.language, comm.official_url, comm.entry_requirements, comm.activity_level, 1 if comm.verified else 0
            ))
            cur.execute("DELETE FROM communities_fts WHERE id = ?;", (comm.id,))
            cur.execute("""
                INSERT INTO communities_fts (id, name, platform, related_games, theme, platform_type, recent_activity, language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                comm.id, comm.name, comm.platform, " ".join(comm.related_games), comm.theme, comm.platform_type, comm.recent_activity, comm.language
            ))
            self._conn.commit()

    # --- BÚSQUEDA ESPECIALIZADA POR MÓDULO ---

    def search_games(
        self,
        query: str = "",
        platform: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        region: Optional[str] = None,
        sort_by: str = "relevance",
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """Buscador avanzado de videojuegos con soporte de filtros por plataforma, género, año y ordenación."""
        with _DB_LOCK:
            cur = self._conn.cursor()
            tokens = [t for t in normalize_gamer_query(query).split() if t]
            
            where_clauses: List[str] = []
            params: List[Any] = []

            if tokens:
                # Búsqueda FTS5
                fts_query = " ".join(f'"{t}"*' for t in tokens)
                where_clauses.append("g.id IN (SELECT id FROM games_fts WHERE games_fts MATCH ?)")
                params.append(fts_query)

            if platform and platform != "Todas":
                where_clauses.append("g.platforms_json LIKE ?")
                params.append(f"%{platform}%")

            if genre and genre != "Todos":
                where_clauses.append("g.genres_json LIKE ?")
                params.append(f"%{genre}%")

            if year:
                where_clauses.append("g.release_year = ?")
                params.append(year)

            if region and region != "Todas":
                where_clauses.append("g.region = ?")
                params.append(region)

            where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
            
            order_sql = "ORDER BY g.rating DESC, g.release_year DESC"
            if sort_by == "year_desc":
                order_sql = "ORDER BY g.release_year DESC"
            elif sort_by == "rating_desc":
                order_sql = "ORDER BY g.rating DESC"
            elif sort_by == "title_asc":
                order_sql = "ORDER BY g.title ASC"

            query_sql = f"""
                SELECT g.* FROM games g
                {where_sql}
                {order_sql}
                LIMIT ?;
            """
            params.append(limit)
            cur.execute(query_sql, params)
            rows = cur.fetchall()

            results: List[Dict[str, Any]] = [self._row_to_game_dict(r, tokens) for r in rows]
            return results

    def _row_to_game_dict(self, r: sqlite3.Row, tokens: Optional[List[str]] = None) -> Dict[str, Any]:
        """Convierte una fila de la base de datos a un diccionario completo con los 24 atributos."""
        d = dict(r)
        d["aliases"] = json.loads(d.get("aliases_json") or "[]")
        d["platforms"] = json.loads(d.get("platforms_json") or "[]")
        d["genres"] = json.loads(d.get("genres_json") or "[]")
        d["languages"] = json.loads(d.get("languages_json") or "[]")
        d["regions_released"] = json.loads(d.get("regions_released_json") or "[]")
        d["screenshots"] = json.loads(d.get("screenshots_json") or "[]")
        d["features"] = json.loads(d.get("features_json") or "[]")
        d["dlcs"] = json.loads(d.get("dlcs_json") or "[]")
        d["expansions"] = json.loads(d.get("expansions_json") or "[]")
        d["versions"] = json.loads(d.get("versions_json") or "[]")
        d["remasters"] = json.loads(d.get("remasters_json") or "[]")
        d["remakes"] = json.loads(d.get("remakes_json") or "[]")
        d["backward_compatibility"] = json.loads(d.get("backward_compatibility_json") or "{}")
        d["score_5d"] = json.loads(d.get("score_5d_json") or "{}")
        d["consulted_sources"] = json.loads(d.get("consulted_sources_json") or "[]")
        d["editions"] = json.loads(d.get("editions_json") or "[]")
        d["updates_patches"] = json.loads(d.get("updates_patches_json") or "[]")
        d["tags"] = json.loads(d.get("tags_json") or "[]")
        if tokens:
            d["highlighted_summary"] = highlight_safe_snippet(d.get("summary", ""), tokens)
        return d

    def get_game_by_id(self, game_id_or_title: str) -> Optional[Dict[str, Any]]:
        """Recupera la ficha individual completa de 24 atributos por ID o título."""
        with _DB_LOCK:
            cur = self._conn.cursor()
            cur.execute("SELECT * FROM games WHERE id = ? OR LOWER(title) = LOWER(?);", (game_id_or_title, game_id_or_title))
            row = cur.fetchone()
            if row:
                return self._row_to_game_dict(row)
            return None

    def get_top_games_by_console(
        self,
        console_id_or_name: str,
        criteria: str = "ranking_general",
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """Recupera los mejores videojuegos clasificados de una consola mediante el motor 5D."""
        with _DB_LOCK:
            cur = self._conn.cursor()
            cur.execute("""
                SELECT * FROM games
                WHERE canonical_platform_id = ?
                   OR platforms_json LIKE ?;
            """, (console_id_or_name, f"%{console_id_or_name}%"))
            rows = cur.fetchall()
            games = [self._row_to_game_dict(r) for r in rows]

            from gamer_ranker import GAMER_RANKER, RankingCriteria
            try:
                crit_enum = RankingCriteria(criteria)
            except Exception:
                crit_enum = RankingCriteria.RANKING_GENERAL

            return GAMER_RANKER.sort_games(games, criteria=crit_enum, limit=limit)

    def search_cheats(
        self,
        query: str = "",
        platform: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """Buscador de trucos, secretos, glitches, guías y trofeos."""
        with _DB_LOCK:
            cur = self._conn.cursor()
            tokens = [t for t in normalize_gamer_query(query).split() if t]

            where_clauses: List[str] = []
            params: List[Any] = []

            if tokens:
                fts_query = " ".join(f'"{t}"*' for t in tokens)
                where_clauses.append("c.id IN (SELECT id FROM cheats_fts WHERE cheats_fts MATCH ?)")
                params.append(fts_query)

            if platform and platform != "Todas":
                where_clauses.append("c.platform LIKE ?")
                params.append(f"%{platform}%")

            if category and category != "Todas":
                where_clauses.append("c.category = ?")
                params.append(category)

            where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
            query_sql = f"""
                SELECT c.* FROM cheats c
                {where_sql}
                ORDER BY c.verified_date DESC
                LIMIT ?;
            """
            params.append(limit)
            cur.execute(query_sql, params)
            rows = cur.fetchall()

            results: List[Dict[str, Any]] = []
            for r in rows:
                d = dict(r)
                d["tags"] = json.loads(d.get("tags_json") or "[]")
                d["highlighted_title"] = highlight_safe_snippet(d.get("title", ""), tokens)
                d["highlighted_content"] = highlight_safe_snippet(d.get("content", ""), tokens, max_len=240)
                results.append(d)
            return results

    def search_preservation(
        self,
        query: str = "",
        platform: Optional[str] = None,
        item_type: Optional[str] = None,
        legal_only: bool = True,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """Buscador de emuladores, homebrew, freeware, proyectos de preservación y parches."""
        with _DB_LOCK:
            cur = self._conn.cursor()
            tokens = [t for t in normalize_gamer_query(query).split() if t]

            where_clauses: List[str] = []
            params: List[Any] = []

            if tokens:
                fts_query = " ".join(f'"{t}"*' for t in tokens)
                where_clauses.append("p.id IN (SELECT id FROM preservation_fts WHERE preservation_fts MATCH ?)")
                params.append(fts_query)

            if platform and platform != "Todas":
                where_clauses.append("p.platform LIKE ?")
                params.append(f"%{platform}%")

            if item_type and item_type != "Todos":
                where_clauses.append("p.item_type = ?")
                params.append(item_type)

            if legal_only:
                where_clauses.append("p.download_safe = 1")

            where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
            query_sql = f"""
                SELECT p.* FROM preservation p
                {where_sql}
                ORDER BY p.download_safe DESC, p.title ASC
                LIMIT ?;
            """
            params.append(limit)
            cur.execute(query_sql, params)
            rows = cur.fetchall()

            results: List[Dict[str, Any]] = []
            for r in rows:
                d = dict(r)
                d["highlighted_desc"] = highlight_safe_snippet(d.get("description", ""), tokens)
                results.append(d)
            return results

    def search_communities(
        self,
        query: str = "",
        platform: Optional[str] = None,
        theme: Optional[str] = None,
        platform_type: Optional[str] = None,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """Buscador prioritario de comunidades gamer (Discord, Reddit, Foros, Speedrun)."""
        with _DB_LOCK:
            cur = self._conn.cursor()
            tokens = [t for t in normalize_gamer_query(query).split() if t]

            where_clauses: List[str] = []
            params: List[Any] = []

            if tokens:
                fts_query = " ".join(f'"{t}"*' for t in tokens)
                where_clauses.append("c.id IN (SELECT id FROM communities_fts WHERE communities_fts MATCH ?)")
                params.append(fts_query)

            if platform and platform != "Todas":
                where_clauses.append("c.platform LIKE ?")
                params.append(f"%{platform}%")

            if theme and theme != "Todos":
                where_clauses.append("c.theme LIKE ?")
                params.append(f"%{theme}%")

            if platform_type and platform_type != "Todos":
                where_clauses.append("c.platform_type = ?")
                params.append(platform_type)

            where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
            query_sql = f"""
                SELECT c.* FROM communities c
                {where_sql}
                ORDER BY c.members_count DESC
                LIMIT ?;
            """
            params.append(limit)
            cur.execute(query_sql, params)
            rows = cur.fetchall()

            results: List[Dict[str, Any]] = []
            for r in rows:
                d = dict(r)
                d["related_games"] = json.loads(d.get("related_games_json") or "[]")
                d["highlighted_name"] = highlight_safe_snippet(d.get("name", ""), tokens)
                results.append(d)
            return results

    def unified_search(
        self,
        query: str = "",
        platform: Optional[str] = None,
        limit_per_category: int = 10
    ) -> Dict[str, Any]:
        """Búsqueda integral unificada que distribuye resultados entre todos los módulos del buscador."""
        start_time = time.time()
        games = self.search_games(query=query, platform=platform, limit=limit_per_category)
        cheats = self.search_cheats(query=query, platform=platform, limit=limit_per_category)
        preservation = self.search_preservation(query=query, platform=platform, limit=limit_per_category)
        communities = self.search_communities(query=query, platform=platform, limit=limit_per_category)
        elapsed_ms = (time.time() - start_time) * 1000.0

        total_hits = len(games) + len(cheats) + len(preservation) + len(communities)
        
        # Registrar en historial si hay consulta
        if query.strip():
            self.add_search_history(query=query.strip(), section="unified", count=total_hits)

        return {
            "query": query,
            "platform_filter": platform or "Todas",
            "total_hits": total_hits,
            "elapsed_ms": round(elapsed_ms, 2),
            "games": games,
            "cheats": cheats,
            "preservation": preservation,
            "communities": communities,
            "counts": {
                "games": len(games),
                "cheats": len(cheats),
                "preservation": len(preservation),
                "communities": len(communities),
            }
        }

    # --- GESTIÓN DE HISTORIAL Y FAVORITOS ---

    def add_search_history(self, query: str, section: str = "all", count: int = 0) -> None:
        if not query or len(query) < 2:
            return
        with _DB_LOCK:
            cur = self._conn.cursor()
            cur.execute("""
                INSERT INTO search_history (query, section, results_count, timestamp)
                VALUES (?, ?, ?, ?);
            """, (query[:120], section, count, time.time()))
            self._conn.commit()

    def get_search_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        with _DB_LOCK:
            cur = self._conn.cursor()
            cur.execute("""
                SELECT query, section, results_count, timestamp
                FROM search_history
                ORDER BY timestamp DESC
                LIMIT ?;
            """, (limit,))
            return [dict(r) for r in cur.fetchall()]

    def clear_search_history(self) -> None:
        with _DB_LOCK:
            cur = self._conn.cursor()
            cur.execute("DELETE FROM search_history;")
            self._conn.commit()

    def add_favorite(self, item_type: str, item_id: str, title: str, subtitle: str = "", url: str = "", extra_data: Optional[Dict[str, Any]] = None) -> bool:
        fav_id = f"{item_type}_{item_id}"
        with _DB_LOCK:
            cur = self._conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO favorites (id, item_type, item_id, title, subtitle, url, saved_at, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (fav_id, item_type, item_id, title, subtitle, url, time.time(), json.dumps(extra_data or {})))
            self._conn.commit()
            return True

    def get_favorites(self, item_type: Optional[str] = None) -> List[Dict[str, Any]]:
        with _DB_LOCK:
            cur = self._conn.cursor()
            if item_type:
                cur.execute("SELECT * FROM favorites WHERE item_type = ? ORDER BY saved_at DESC;", (item_type,))
            else:
                cur.execute("SELECT * FROM favorites ORDER BY saved_at DESC;")
            favs: List[Dict[str, Any]] = []
            for r in cur.fetchall():
                d = dict(r)
                d["data"] = json.loads(d.get("data_json") or "{}")
                favs.append(d)
            return favs

    def remove_favorite(self, fav_id: str) -> bool:
        with _DB_LOCK:
            cur = self._conn.cursor()
            cur.execute("DELETE FROM favorites WHERE id = ?;", (fav_id,))
            self._conn.commit()
            return True

    def close(self) -> None:
        """Cierra la conexión con la base de datos."""
        with _DB_LOCK:
            if self._conn:
                self._conn.close()

    def get_database_stats(self) -> Dict[str, int]:
        with _DB_LOCK:
            cur = self._conn.cursor()
            cur.execute("SELECT COUNT(*) FROM games;")
            g_cnt = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM cheats;")
            c_cnt = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM preservation;")
            p_cnt = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM communities;")
            comm_cnt = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM favorites;")
            fav_cnt = cur.fetchone()[0]
            return {
                "total_games": g_cnt,
                "total_cheats": c_cnt,
                "total_preservation": p_cnt,
                "total_communities": comm_cnt,
                "total_favorites": fav_cnt
            }
