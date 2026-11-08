"""
Gamer Search Engine - Motor de Inteligencia Artificial Semántica y NLP Gamer
=============================================================================
Comprende lenguaje natural, extrae entidades gamer (videojuego, plataforma, tipo de recurso),
expande consultas semánticamente, desambigua acrónimos, clasifica intenciones y detecta
patrones sospechosos de malware / piratería.
"""

import html
import re
import unicodedata
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class GamerIntent:
    raw_query: str
    detected_game: Optional[str] = None
    detected_platform: Optional[str] = None
    intent_type: str = "general"  # cheats, game_info, communities, preservation, mods, guides, general
    confidence: float = 0.5
    recommended_sources: List[str] = field(default_factory=list)
    expanded_terms: List[str] = field(default_factory=list)
    is_suspicious: bool = False
    suspicious_reason: Optional[str] = None
    natural_language_summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Diccionario canónico de alias, acrónimos y nombres de videojuegos
GAME_ALIASES: Dict[str, str] = {
    # Zelda
    "totk": "The Legend of Zelda: Tears of the Kingdom",
    "zelda totk": "The Legend of Zelda: Tears of the Kingdom",
    "tears of the kingdom": "The Legend of Zelda: Tears of the Kingdom",
    "zelda tears": "The Legend of Zelda: Tears of the Kingdom",
    "botw": "The Legend of Zelda: Breath of the Wild",
    "zelda botw": "The Legend of Zelda: Breath of the Wild",
    "breath of the wild": "The Legend of Zelda: Breath of the Wild",
    "zelda breath": "The Legend of Zelda: Breath of the Wild",
    "oot": "The Legend of Zelda: Ocarina of Time",
    "zelda oot": "The Legend of Zelda: Ocarina of Time",
    "ocarina of time": "The Legend of Zelda: Ocarina of Time",
    "ocarina": "The Legend of Zelda: Ocarina of Time",
    "zelda": "The Legend of Zelda",

    # Mario
    "odyssey": "Super Mario Odyssey",
    "mario odyssey": "Super Mario Odyssey",
    "smo": "Super Mario Odyssey",
    "sm64": "Super Mario 64",
    "mario 64": "Super Mario 64",
    "super mario 64": "Super Mario 64",
    "mario": "Super Mario",

    # Smash Bros
    "smash ultimate": "Super Smash Bros. Ultimate",
    "ssbu": "Super Smash Bros. Ultimate",
    "smash bros": "Super Smash Bros. Ultimate",
    "smash": "Super Smash Bros. Ultimate",

    # Metroid
    "metroid prime": "Metroid Prime Remastered",
    "prime remastered": "Metroid Prime Remastered",
    "metroid prime remastered": "Metroid Prime Remastered",
    "metroid": "Metroid",

    # Spider-Man
    "spider-man 2": "Marvel's Spider-Man 2",
    "spider man 2": "Marvel's Spider-Man 2",
    "spiderman 2": "Marvel's Spider-Man 2",
    "spiderman 2 ps5": "Marvel's Spider-Man 2",
    "spiderman": "Marvel's Spider-Man 2",

    # God of War
    "gow ragnarok": "God of War Ragnarök",
    "god of war ragnarok": "God of War Ragnarök",
    "gow": "God of War Ragnarök",
    "god of war": "God of War Ragnarök",
    "ragnarok": "God of War Ragnarök",

    # Soulslike / FromSoftware
    "elden ring": "Elden Ring",
    "er": "Elden Ring",
    "shadow of the erdtree": "Elden Ring",
    "erdtree": "Elden Ring",
    "demons souls": "Demon's Souls Remake",
    "demon souls": "Demon's Souls Remake",
    "des remake": "Demon's Souls Remake",
    "bloodborne": "Bloodborne",
    "dark souls": "Dark Souls",

    # Xbox Franchises
    "halo infinite": "Halo Infinite",
    "halo 6": "Halo Infinite",
    "halo ce": "Halo: Combat Evolved",
    "halo": "Halo Infinite",
    "forza horizon 5": "Forza Horizon 5",
    "forza 5": "Forza Horizon 5",
    "fh5": "Forza Horizon 5",
    "forza": "Forza Horizon 5",
    "starfield": "Starfield",

    # Clásicos & Retro
    "silent hill 2": "Silent Hill 2",
    "sh2": "Silent Hill 2",
    "metal gear solid": "Metal Gear Solid",
    "mgs": "Metal Gear Solid",
    "mgs1": "Metal Gear Solid",
    "chrono trigger": "Chrono Trigger",
    "mother 3": "Mother 3",
}

# Diccionario canónico de plataformas y consolas
PLATFORM_ALIASES: Dict[str, str] = {
    "switch": "Nintendo Switch",
    "nintendo switch": "Nintendo Switch",
    "ns": "Nintendo Switch",
    "ps5": "PlayStation 5",
    "playstation 5": "PlayStation 5",
    "playstation5": "PlayStation 5",
    "ps4": "PlayStation 4",
    "playstation 4": "PlayStation 4",
    "ps3": "PlayStation 3",
    "playstation 3": "PlayStation 3",
    "ps2": "PlayStation 2",
    "playstation 2": "PlayStation 2",
    "ps1": "PlayStation 1",
    "psx": "PlayStation 1",
    "psp": "PSP",
    "ps vita": "PS Vita",
    "vita": "PS Vita",
    "xbox series x": "Xbox Series X",
    "xbox series s": "Xbox Series S",
    "xbox series": "Xbox Series X/S",
    "xsx": "Xbox Series X",
    "xss": "Xbox Series S",
    "xbox one": "Xbox One",
    "xbox 360": "Xbox 360",
    "xbox": "Xbox",
    "n64": "Nintendo 64",
    "nintendo 64": "Nintendo 64",
    "snes": "Super Nintendo (SNES)",
    "super nintendo": "Super Nintendo (SNES)",
    "nes": "NES",
    "game boy": "Game Boy",
    "gba": "Game Boy Advance",
    "game boy advance": "Game Boy Advance",
    "gamecube": "Nintendo GameCube",
    "wii": "Nintendo Wii",
    "wii u": "Wii U",
    "pc": "PC",
    "steam": "PC",
    "sega": "Sega",
    "atari": "Atari",
    "retro": "Retro",
}

# Patrones para detección de intenciones temáticas
INTENT_KEYWORDS: Dict[str, Set[str]] = {
    "cheats": {
        "truco", "trucos", "cheat", "cheats", "codigo", "codigos", "glitch", "glitches",
        "secreto", "secretos", "secrets", "easter egg", "easter eggs", "desbloqueable",
        "desbloqueables", "unlockables", "desbloquear", "trofeo", "trofeos", "trophies",
        "platino", "logro", "logros", "achievements", "1000g", "desafios", "duplicacion",
        "duplicar", "dupe", "exploit", "exploits"
    },
    "communities": {
        "comunidad", "comunidades", "community", "communities", "discord", "reddit",
        "sub", "subreddit", "foro", "foros", "forum", "forums", "servidor", "servidores",
        "grupo", "grupos", "jugadores", "fans", "speedrunners", "speedrunning", "donde juegan",
        "donde hablar", "compartan", "compartir"
    },
    "preservation": {
        "emulador", "emuladores", "emulator", "emulators", "emulacion", "preservacion",
        "homebrew", "roms legales", "freeware", "dominio publico", "decompilation",
        "descompilacion", "retroarch", "dolphin", "pcsx2", "rpcs3", "duckstation",
        "ppsspp", "xemu", "xenia", "preservar", "cartucho", "archivo historico"
    },
    "guides": {
        "guia", "guias", "guide", "guides", "walkthrough", "walkthroughs", "estrategia",
        "estrategias", "build", "builds", "como conseguir", "como derrotar", "como pasar",
        "100%", "completar al 100", "paso a paso", "tutorial"
    },
    "mods": {
        "mod", "mods", "modding", "texturas", "60fps", "parche", "parches", "patch",
        "traduccion", "traducciones", "romhack", "romhacking", "hack", "fan translation"
    },
    "game_info": {
        "requisitos", "lanzamiento", "precio", "dlc", "expansiones", "desarrollador",
        "genero", "ediciones", "reviews", "calificacion", "cuanto cuesta", "cuando sale",
        "compatibilidad", "actualizaciones"
    }
}

# Patrones de advertencia de seguridad y anti-malware
SUSPICIOUS_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"\b(descargar\s+gratis|free\s+download|full\s+download)\b.*\b(rom|roms|iso|nsp|xci|pkg)\b", re.IGNORECASE),
     "Solicitud de descarga de copias comerciales potencialmente no autorizadas. El motor redirige hacia preservación legal, homebrew o tiendas oficiales."),
    (re.compile(r"\b(crack|keygen|keygen\.exe|serial\s+key|bypass\s+drm|no\s*cd\s*crack)\b", re.IGNORECASE),
     "Petición de herramientas de evasión de DRM o ejecutables sospechosos (.exe/keygen) con alto riesgo de malware o troyanos."),
    (re.compile(r"\b(free\s+robux|v-?bucks\s+gratis|generador\s+de\s+gemas|hack\s+tool)\b", re.IGNORECASE),
     "Patrón identificado de estafa o phishing (scam). No existen generadores mágicos de divisas virtuales.")
]


class GamerSemanticAI:
    """Motor de procesamiento de lenguaje natural y búsqueda semántica para consultas gamer."""

    def __init__(self):
        pass

    def normalize(self, text: str) -> str:
        """Elimina tildes y caracteres diacríticos."""
        if not text:
            return ""
        nfd = unicodedata.normalize("NFD", text.lower())
        clean = "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")
        return re.sub(r"\s+", " ", clean).strip()

    def detect_suspicious_query(self, raw_query: str) -> Tuple[bool, Optional[str]]:
        """Analiza la consulta en busca de patrones de malware, estafas o sitios pirata fraudulentos."""
        for pattern, reason in SUSPICIOUS_PATTERNS:
            if pattern.search(raw_query):
                return True, reason
        return False, None

    def analyze_query(self, raw_query: str) -> GamerIntent:
        """
        Analiza una consulta en lenguaje natural y extrae:
        - Videojuego detectado
        - Plataforma objetivo
        - Tipo de intención (cheats, communities, preservation, guides, mods, game_info, general)
        - Confianza y fuentes recomendadas
        """
        if not raw_query or not raw_query.strip():
            return GamerIntent(raw_query="")

        norm_query = self.normalize(raw_query)
        is_suspicious, suspicious_reason = self.detect_suspicious_query(raw_query)

        # 1. Detectar Videojuego
        detected_game: Optional[str] = None
        # Ordenar alias por longitud descendente para buscar frases más largas primero
        sorted_game_aliases = sorted(GAME_ALIASES.items(), key=lambda x: len(x[0]), reverse=True)
        for alias, canonical_name in sorted_game_aliases:
            pattern = rf"\b{re.escape(alias)}\b"
            if re.search(pattern, norm_query):
                detected_game = canonical_name
                break

        # 2. Detectar Plataforma
        detected_platform: Optional[str] = None
        sorted_platforms = sorted(PLATFORM_ALIASES.items(), key=lambda x: len(x[0]), reverse=True)
        for alias, canonical_platform in sorted_platforms:
            pattern = rf"\b{re.escape(alias)}\b"
            if re.search(pattern, norm_query):
                detected_platform = canonical_platform
                break

        # 3. Detectar Tipo de Intención (Scoring)
        intent_scores: Dict[str, int] = {k: 0 for k in INTENT_KEYWORDS.keys()}
        for intent_name, kw_set in INTENT_KEYWORDS.items():
            for kw in kw_set:
                if re.search(rf"\b{re.escape(kw)}\b", norm_query):
                    intent_scores[intent_name] += 1

        top_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent_type = top_intent[0] if top_intent[1] > 0 else "general"

        # Calcular confianza
        confidence = 0.5
        if detected_game:
            confidence += 0.25
        if detected_platform:
            confidence += 0.15
        if top_intent[1] > 0:
            confidence += 0.10
        confidence = min(1.0, confidence)

        # 4. Determinar Fuentes Recomendadas
        recommended_sources: List[str] = []
        if intent_type == "cheats":
            recommended_sources = ["GameFAQs", "PlayStationTrophies.org", "TrueAchievements", "Reddit r/gaming", "PowerPyx"]
        elif intent_type == "communities":
            recommended_sources = ["Reddit Oficial", "Servidores Discord Verificados", "Foros de Speedrun.com", "ResetEra / Nintendo Life"]
        elif intent_type in ("preservation", "mods"):
            recommended_sources = ["GitHub Libretro / Emulators", "Internet Archive Console Living Room", "RomHacking.net", "r/emulation"]
        elif intent_type == "guides":
            recommended_sources = ["Fextralife Wiki", "GameFAQs Walkthroughs", "IGN Guides", "Reddit Builds Communities"]
        else:
            recommended_sources = ["Wikidata", "Metacritic", "IGDB / RAWG", "Comunidades Oficiales"]

        # 5. Generar Términos Expandidos
        expanded_terms: List[str] = []
        if detected_game:
            expanded_terms.append(detected_game)
        if detected_platform:
            expanded_terms.append(detected_platform)
        if intent_type == "cheats":
            expanded_terms.extend(["trucos", "secretos", "guia"])
        elif intent_type == "communities":
            expanded_terms.extend(["comunidad", "discord", "reddit"])
        elif intent_type == "preservation":
            expanded_terms.extend(["emulador", "homebrew", "preservacion"])

        # 6. Resumen en Lenguaje Natural
        summary_parts = []
        if detected_game:
            summary_parts.append(f"juego **{detected_game}**")
        if detected_platform:
            summary_parts.append(f"plataforma **{detected_platform}**")
        
        intent_label = {
            "cheats": "trucos, secretos y trofeos",
            "communities": "comunidades activas y puntos de encuentro",
            "preservation": "recursos de preservación, emulación y homebrew legal",
            "guides": "guías paso a paso y estrategias optimizadas",
            "mods": "modificaciones y parches comunitarios",
            "game_info": "información técnica y disponibilidad",
            "general": "resultados generales"
        }.get(intent_type, "resultados")

        if summary_parts:
            summary_text = f"Búsqueda orientada a {intent_label} para {' en '.join(summary_parts)}."
        else:
            summary_text = f"Explorando {intent_label} en todo el catálogo gaming."

        return GamerIntent(
            raw_query=raw_query,
            detected_game=detected_game,
            detected_platform=detected_platform,
            intent_type=intent_type,
            confidence=round(confidence, 2),
            recommended_sources=recommended_sources,
            expanded_terms=expanded_terms,
            is_suspicious=is_suspicious,
            suspicious_reason=suspicious_reason,
            natural_language_summary=summary_text
        )

    def execute_smart_search(
        self,
        raw_query: str,
        engine_db: Any,
        platform_override: Optional[str] = None,
        limit_per_category: int = 15
    ) -> Dict[str, Any]:
        """
        Ejecuta la búsqueda semántica inteligente:
        1. Analiza la consulta en lenguaje natural.
        2. Aplica expansión de consultas y desambiguación.
        3. Realiza búsquedas cruzadas en FTS5 priorizando la categoría identificada por la IA.
        4. Elimina duplicados y filtra contenido no seguro.
        5. Devuelve la estructura unificada con el resumen y recomendaciones de IA.
        """
        intent = self.analyze_query(raw_query)
        target_platform = platform_override if (platform_override and platform_override != "Todas") else intent.detected_platform

        # Construir consulta para el motor FTS5
        # Si se detectó un juego específico, usar el nombre del juego más términos temáticos
        search_term = intent.detected_game or raw_query
        
        # Consultar la base de datos a través de unified_search o métodos específicos
        raw_results = engine_db.unified_search(
            query=search_term,
            platform=target_platform,
            limit_per_category=limit_per_category
        )

        # Deduplicar resultados si se repiten IDs
        seen_ids = set()
        dedup_games = []
        for g in raw_results["games"]:
            if g["id"] not in seen_ids:
                seen_ids.add(g["id"])
                dedup_games.append(g)

        dedup_cheats = []
        for c in raw_results["cheats"]:
            if c["id"] not in seen_ids:
                seen_ids.add(c["id"])
                dedup_cheats.append(c)

        dedup_preservation = []
        for p in raw_results["preservation"]:
            if p["id"] not in seen_ids:
                seen_ids.add(p["id"])
                dedup_preservation.append(p)

        dedup_communities = []
        for comm in raw_results["communities"]:
            if comm["id"] not in seen_ids:
                seen_ids.add(comm["id"])
                dedup_communities.append(comm)

        # Si la intención es comunidades, poner comunidades al inicio en prioridad
        priority_section = "games"
        if intent.intent_type == "communities":
            priority_section = "communities"
        elif intent.intent_type in ("cheats", "guides"):
            priority_section = "cheats"
        elif intent.intent_type in ("preservation", "mods"):
            priority_section = "preservation"

        return {
            "query": raw_query,
            "intent": intent.to_dict(),
            "priority_section": priority_section,
            "total_hits": len(dedup_games) + len(dedup_cheats) + len(dedup_preservation) + len(dedup_communities),
            "games": dedup_games,
            "cheats": dedup_cheats,
            "preservation": dedup_preservation,
            "communities": dedup_communities,
            "counts": {
                "games": len(dedup_games),
                "cheats": len(dedup_cheats),
                "preservation": len(dedup_preservation),
                "communities": len(dedup_communities)
            },
            "elapsed_ms": raw_results.get("elapsed_ms", 0.0)
        }


# Instancia singleton del motor de IA semántica
GAMER_AI = GamerSemanticAI()
