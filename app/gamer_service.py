"""
Gamer Search Engine - Capa de Servicios y Controladores Especializados
======================================================================
Coordina la lógica de negocio, filtros dinámicos, búsquedas especializadas por módulo,
fichas de detalle, comparador de versiones y taxonomías de las secciones:
1. Videojuegos
2. Trucos y Secretos
3. ROMs Legales, Emulación y Preservación
4. Comunidades Gamer
"""

from typing import Any, Dict, List, Optional
from gamer_db import GamerSearchEngineDB
from gamer_ai import GAMER_AI, GamerIntent


# Mapeo de categorías de trucos a etiquetas legibles
CHEAT_CATEGORY_LABELS: Dict[str, str] = {
    "trucos_codigos": "Trucos y Códigos",
    "easter_eggs": "Easter Eggs",
    "secretos": "Secretos Ocultos",
    "desbloqueables": "Desbloqueables y Trajes",
    "personajes": "Personajes Secretos",
    "armas_habilidades": "Armas, Habilidades y Builds",
    "mapas": "Mapas Ocultos",
    "glitches": "Glitches Conocidos y Speedrunning",
    "walkthroughs": "Walkthroughs y Guías Paso a Paso",
    "guia_100": "Guías para Completar al 100%",
    "trofeos_ps": "Trofeos de PlayStation",
    "logros_xbox": "Logros de Xbox",
    "desafios_nintendo": "Desafíos de Nintendo",
}

# Mapeo de tipos de preservación a etiquetas legibles
PRESERVATION_TYPE_LABELS: Dict[str, str] = {
    "emulator": "Emulador Oficial Verificado",
    "homebrew": "Videojuego Homebrew Independiente",
    "freeware": "Juego Freeware Legal",
    "public_domain": "Archivo Histórico de Dominio Público",
    "demo": "Demo Jugable Autorizada",
    "preservation_archive": "Proyecto de Preservación / Descompilación",
    "translation_patch": "Parche de Traducción Comunitaria (IPS/BPS/UPS)",
    "mod": "Modificación y Texturas HD",
    "modding_tool": "Herramienta de Modding y Parcheo",
    "compatibility_database": "Base de Datos de Compatibilidad",
    "technical_documentation": "Documentación Técnica y Arquitectura",
}

# Mapeo de tipos de comunidad a etiquetas legibles
COMMUNITY_TYPE_LABELS: Dict[str, str] = {
    "reddit": "Subreddit de Reddit",
    "discord": "Servidor Oficial de Discord",
    "forum": "Foro Especializado Web",
    "speedrun": "Comunidad de Speedrun.com",
    "modding": "Comunidad de Modding y ROM Hacking",
    "esports": "Comunidad Competitiva Esports",
    "facebook": "Grupo Comunitario",
}


class GamerSearchService:
    """Capa de servicios unificada para alimentar el backend y las vistas de la UI."""

    def __init__(self, db: Optional[GamerSearchEngineDB] = None):
        self.db = db if db is not None else GamerSearchEngineDB()
        self.ai = GAMER_AI

    # --- FILTROS DINÁMICOS DISPONIBLES ---

    def get_filter_options(self) -> Dict[str, Any]:
        """Obtiene las opciones únicas de filtros dinámicos presentes en el catálogo."""
        # Plataformas principales
        platforms = [
            "Todas",
            "Nintendo Switch",
            "PlayStation 5",
            "Xbox Series X",
            "Xbox Series S",
            "PlayStation 4",
            "Xbox One",
            "Nintendo 64",
            "Super Nintendo (SNES)",
            "NES",
            "PlayStation 2",
            "PlayStation 1",
            "Xbox 360",
            "Xbox Original",
            "Game Boy",
            "Game Boy Advance",
            "Nintendo DS",
            "Nintendo 3DS",
            "PSP",
            "PS Vita",
            "Sega",
            "Atari",
            "PC"
        ]

        # Géneros
        genres = [
            "Todos",
            "Action-Adventure",
            "Open World",
            "Action RPG",
            "Soulslike",
            "First-Person Shooter",
            "Platformer",
            "Fighting",
            "Racing",
            "Survival Horror",
            "JRPG",
            "Puzzle",
            "Sci-Fi"
        ]

        # Años
        years = ["Todos", "2024", "2023", "2022", "2021", "2020", "2018", "2017", "2015", "2001", "1998", "1996", "1995"]

        # Regiones
        regions = ["Todas", "Global", "América", "Europa", "Japón"]

        return {
            "platforms": platforms,
            "genres": genres,
            "years": years,
            "regions": regions,
            "cheat_categories": [{"id": k, "label": v} for k, v in CHEAT_CATEGORY_LABELS.items()],
            "preservation_types": [{"id": k, "label": v} for k, v in PRESERVATION_TYPE_LABELS.items()],
            "community_types": [{"id": k, "label": v} for k, v in COMMUNITY_TYPE_LABELS.items()],
        }

    # --- CONTROLADOR MÓDULO 1: VIDEOJUEGOS ---

    def search_games_module(
        self,
        query: str = "",
        platform: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[str] = None,
        region: Optional[str] = None,
        sort_by: str = "relevance",
        limit: int = 30
    ) -> Dict[str, Any]:
        """Ejecuta la búsqueda de videojuegos con filtros dinámicos."""
        int_year = int(year) if (year and year.isdigit()) else None
        games = self.db.search_games(
            query=query,
            platform=platform,
            genre=genre,
            year=int_year,
            region=region,
            sort_by=sort_by,
            limit=limit
        )
        return {
            "query": query,
            "filters": {
                "platform": platform or "Todas",
                "genre": genre or "Todos",
                "year": year or "Todos",
                "region": region or "Todas",
                "sort_by": sort_by
            },
            "count": len(games),
            "results": games
        }

    def get_game_detail(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene la ficha técnica completa de un videojuego junto a sus trucos y comunidades relacionadas."""
        all_games = self.db.search_games(query="", limit=200)
        matched_game = next((g for g in all_games if g["id"] == game_id), None)
        if not matched_game:
            return None

        # Trucos y guías del mismo juego
        related_cheats = self.db.search_cheats(query=matched_game["title"], limit=10)

        # Comunidades relacionadas
        related_communities = self.db.search_communities(query=matched_game["title"], limit=6)

        return {
            "game": matched_game,
            "cheats": related_cheats,
            "communities": related_communities
        }

    def compare_game_versions(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Genera una comparación estructurada de versiones, requisitos técnicos, DLCs y compatibilidad."""
        detail = self.get_game_detail(game_id)
        if not detail:
            return None
        game = detail["game"]
        return {
            "title": game["title"],
            "platforms": game.get("platforms", []),
            "editions": game.get("editions", []),
            "dlcs": game.get("dlcs", []),
            "updates_patches": game.get("updates_patches", []),
            "compatibility": game.get("compatibility", ""),
            "technical_requirements": game.get("technical_requirements", ""),
            "price_status": game.get("price_status", ""),
            "rating": game.get("rating", 0.0),
            "rating_source": game.get("rating_source", "")
        }

    # --- CONTROLADOR MÓDULO 2: TRUCOS Y SECRETOS ---

    def search_cheats_module(
        self,
        query: str = "",
        platform: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 30
    ) -> Dict[str, Any]:
        """Ejecuta la búsqueda de trucos, secretos, trofeos y guías."""
        cheats = self.db.search_cheats(
            query=query,
            platform=platform,
            category=category,
            limit=limit
        )
        return {
            "query": query,
            "filters": {
                "platform": platform or "Todas",
                "category": category or "Todas"
            },
            "count": len(cheats),
            "results": cheats
        }

    # --- CONTROLADOR MÓDULO 3: PRESERVACIÓN Y EMULADORES ---

    def search_preservation_module(
        self,
        query: str = "",
        platform: Optional[str] = None,
        item_type: Optional[str] = None,
        legal_only: bool = True,
        limit: int = 30
    ) -> Dict[str, Any]:
        """Ejecuta la búsqueda de emuladores legítimos, homebrew, freeware y proyectos de preservación."""
        items = self.db.search_preservation(
            query=query,
            platform=platform,
            item_type=item_type,
            legal_only=legal_only,
            limit=limit
        )
        return {
            "query": query,
            "filters": {
                "platform": platform or "Todas",
                "item_type": item_type or "Todos",
                "legal_only": legal_only
            },
            "count": len(items),
            "results": items
        }

    # --- CONTROLADOR MÓDULO 4: COMUNIDADES GAMER ---

    def search_communities_module(
        self,
        query: str = "",
        platform: Optional[str] = None,
        theme: Optional[str] = None,
        platform_type: Optional[str] = None,
        limit: int = 30
    ) -> Dict[str, Any]:
        """Ejecuta la búsqueda de comunidades activas de jugadores."""
        communities = self.db.search_communities(
            query=query,
            platform=platform,
            theme=theme,
            platform_type=platform_type,
            limit=limit
        )
        return {
            "query": query,
            "filters": {
                "platform": platform or "Todas",
                "theme": theme or "Todos",
                "platform_type": platform_type or "Todos"
            },
            "count": len(communities),
            "results": communities
        }

    # --- CONTROLADOR UNIFICADO CON INTELIGENCIA ARTIFICIAL ---

    def search_smart(
        self,
        raw_query: str,
        platform_override: Optional[str] = None,
        limit_per_category: int = 15
    ) -> Dict[str, Any]:
        """Punto de entrada principal para búsquedas con IA semántica, desambiguación y ordenamiento temático."""
        return self.ai.execute_smart_search(
            raw_query=raw_query,
            engine_db=self.db,
            platform_override=platform_override,
            limit_per_category=limit_per_category
        )


# Instancia de servicio por defecto
GAMER_SERVICE = GamerSearchService()
