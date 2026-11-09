"""
Gamer Search Engine - Motor de Expansión Automática de Consultas Semántica y Multilingüe (Fase 4)
=================================================================================================
Módulo crítico para transformar una consulta breve del usuario en múltiples vectores de búsqueda
especializados, multilingües (ES, EN, JA), clasificados por categoría y variaciones de plataforma.

Ejemplos requeridos:
- 'GTA V trucos secretos' ->
    * GTA 5 hidden secrets
    * GTA V cheat codes
    * GTA 5 easter eggs
    * GTA V rare locations
    * GTA 5 hidden missions
    * GTA V glitches
    * GTA 5 community discoveries
    * GTA V undocumented features
    * GTA V secrets Reddit
    * GTA V guides forums
    * GTA V mods GitHub
    * GTA V game files research

- 'Zelda Tears of the Kingdom' ->
    * Zelda TOTK secrets
    * Zelda TOTK hidden mechanics
    * Zelda TOTK glitches
    * Zelda TOTK walkthrough
    * Zelda TOTK shrines guide
    * Zelda TOTK hidden locations
    * Zelda TOTK discoveries Reddit
    * Zelda TOTK community forums
    * Zelda TOTK speedrun
    * Zelda TOTK mods
    * Zelda TOTK game research
"""

import json
import logging
import re
import unicodedata
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("QueryExpander")

# Catálogo canónico de entidades de juego con alias, acrónimos y títulos oficiales multilingües
CANONICAL_GAME_CATALOG: Dict[str, Dict[str, Any]] = {
    "Grand Theft Auto V": {
        "aliases": ["gta v", "gta 5", "gtav", "grand theft auto v", "grand theft auto 5"],
        "short_name": "GTA 5",
        "acronym": "GTA V",
        "japanese": "グランド・セフト・オートV",
        "platforms": ["PC", "PS5", "PS4", "Xbox Series X/S", "Xbox One", "Xbox 360", "PS3"],
        "developer": "Rockstar North"
    },
    "Grand Theft Auto VI": {
        "aliases": ["gta vi", "gta 6", "gta6", "grand theft auto vi", "grand theft auto 6"],
        "short_name": "GTA 6",
        "acronym": "GTA VI",
        "japanese": "グランド・セフト・オートVI",
        "platforms": ["PS5", "Xbox Series X/S"],
        "developer": "Rockstar Games"
    },
    "Grand Theft Auto: San Andreas": {
        "aliases": ["gta san andreas", "san andreas", "gta sa", "gtasa", "grand theft auto san andreas"],
        "short_name": "GTA San Andreas",
        "acronym": "GTA SA",
        "japanese": "グランド・セフト・オート・サンアンドレアス",
        "platforms": ["PC", "PS2", "Xbox", "PS3", "Xbox 360", "Android", "iOS"],
        "developer": "Rockstar North"
    },
    "Grand Theft Auto: Vice City": {
        "aliases": ["gta vice city", "vice city", "gta vc", "gtavc", "grand theft auto vice city"],
        "short_name": "GTA Vice City",
        "acronym": "GTA VC",
        "japanese": "グランド・セフト・オート・バイスシティ",
        "platforms": ["PC", "PS2", "Xbox"],
        "developer": "Rockstar North"
    },
    "The Legend of Zelda: Tears of the Kingdom": {
        "aliases": ["zelda tears of the kingdom", "tears of the kingdom", "totk", "zelda totk", "zelda tears"],
        "short_name": "Zelda TOTK",
        "acronym": "TOTK",
        "japanese": "ゼルダの伝説 ティアーズ オブ ザ キングダム",
        "platforms": ["Nintendo Switch"],
        "developer": "Nintendo EPD"
    },
    "The Legend of Zelda: Breath of the Wild": {
        "aliases": ["zelda breath of the wild", "breath of the wild", "botw", "zelda botw", "zelda breath"],
        "short_name": "Zelda BOTW",
        "acronym": "BOTW",
        "japanese": "ゼルダの伝説 ブレス オブ ザ ワイルド",
        "platforms": ["Nintendo Switch", "Wii U"],
        "developer": "Nintendo EPD"
    },
    "The Legend of Zelda: Ocarina of Time": {
        "aliases": ["zelda ocarina of time", "ocarina of time", "oot", "zelda oot", "ocarina"],
        "short_name": "Zelda Ocarina of Time",
        "acronym": "OOT",
        "japanese": "ゼルダの伝説 時のオカリナ",
        "platforms": ["Nintendo 64", "GameCube", "Nintendo 3DS", "Nintendo Switch Online"],
        "developer": "Nintendo EAD"
    },
    "The Legend of Zelda: Twilight Princess": {
        "aliases": ["zelda twilight princess", "twilight princess", "tp", "zelda tp", "zelda twilight"],
        "short_name": "Zelda Twilight Princess",
        "acronym": "Zelda TP",
        "japanese": "ゼルダの伝説 トワイライトプリンセス",
        "platforms": ["GameCube", "Wii", "Wii U"],
        "developer": "Nintendo EAD"
    },
    "The Legend of Zelda: Skyward Sword": {
        "aliases": ["zelda skyward sword", "skyward sword", "ss", "zelda ss", "zelda skyward"],
        "short_name": "Zelda Skyward Sword",
        "acronym": "Zelda SS",
        "japanese": "ゼルダの伝説 スカイウォードソード",
        "platforms": ["Wii", "Nintendo Switch"],
        "developer": "Nintendo EAD"
    },
    "Red Dead Redemption 2": {
        "aliases": ["red dead redemption 2", "red dead 2", "rdr2", "rdr 2"],
        "short_name": "RDR2",
        "acronym": "RDR2",
        "japanese": "レッド・デッド・リデンプション2",
        "platforms": ["PC", "PS4", "Xbox One"],
        "developer": "Rockstar Studios"
    },
    "Elden Ring": {
        "aliases": ["elden ring", "er", "shadow of the erdtree"],
        "short_name": "Elden Ring",
        "acronym": "ER",
        "japanese": "エルデンリング",
        "platforms": ["PC", "PS5", "PS4", "Xbox Series X/S", "Xbox One"],
        "developer": "FromSoftware"
    },
    "Minecraft": {
        "aliases": ["minecraft", "mc"],
        "short_name": "Minecraft",
        "acronym": "MC",
        "japanese": "マインクラフト",
        "platforms": ["PC", "Nintendo Switch", "PS5", "Xbox Series X/S", "Android", "iOS"],
        "developer": "Mojang Studios"
    },
    "Super Mario Odyssey": {
        "aliases": ["super mario odyssey", "mario odyssey", "odyssey", "smo"],
        "short_name": "Mario Odyssey",
        "acronym": "SMO",
        "japanese": "スーパーマリオ オデッセイ",
        "platforms": ["Nintendo Switch"],
        "developer": "Nintendo EPD"
    }
}


class GamerQueryExpander:
    """
    Motor inteligente de generación y expansión de consultas gamer.
    Genera consultas alternativas orientadas por categorías y plataformas.
    """

    def __init__(self):
        pass

    def normalize(self, text: str) -> str:
        if not text:
            return ""
        nfd = unicodedata.normalize("NFD", text.lower())
        clean = "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")
        return re.sub(r"\s+", " ", clean).strip()

    def detect_canonical_game(self, raw_query: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Detecta si la consulta refiere a un juego canónico conocido."""
        norm_q = self.normalize(raw_query)
        # Ordenar por longitud de alias descendente para buscar frases más largas primero
        candidates = []
        for game_title, meta in CANONICAL_GAME_CATALOG.items():
            for alias in meta["aliases"]:
                candidates.append((alias, game_title, meta))
        candidates.sort(key=lambda x: len(x[0]), reverse=True)

        for alias, game_title, meta in candidates:
            pattern = rf"\b{re.escape(alias)}\b"
            if re.search(pattern, norm_q):
                return game_title, meta
        return None, None

    def fetch_live_engine_suggestions(self, base_query: str, limit: int = 5) -> List[str]:
        """
        Consulta en tiempo real sugerencias vivas de la comunidad en OpenSearch
        para incorporar tendencias y variantes activas.
        """
        if not base_query or len(base_query.strip()) < 3:
            return []

        clean_q = base_query.strip()
        url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={urllib.parse.quote(clean_q)}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GamerOSINT/2.0"}
        )
        suggestions: List[str] = []
        try:
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    if len(data) > 1 and isinstance(data[1], list):
                        suggestions = [str(s) for s in data[1][:limit]]
        except Exception as e:
            logger.debug(f"Live engine suggestions timeout/error for '{base_query}': {e}")
        return suggestions

    def expand_query(self, raw_query: str, fetch_live_suggestions: bool = True) -> Dict[str, Any]:
        """
        Genera el árbol completo de consultas expandidas:
        1. Consulta original preservada.
        2. Consultas por categoría temática (trucos, secretos, glitches, guías, mods, comunidad).
        3. Consultas multilingües (inglés, español, japonés).
        4. Consultas por plataforma y versión.
        5. Sugerencias vivas de la comunidad gamer.
        """
        clean_raw = raw_query.strip()
        norm_q = self.normalize(clean_raw)
        canonical_game, game_meta = self.detect_canonical_game(clean_raw)

        # Términos identificadores del juego (canónico, corto, acrónimo)
        if game_meta:
            primary_name = game_meta["short_name"]
            acronym_name = game_meta["acronym"]
            japanese_name = game_meta["japanese"]
            platforms = game_meta.get("platforms", [])
        else:
            primary_name = clean_raw
            acronym_name = clean_raw
            japanese_name = ""
            platforms = ["PC", "PS5", "Nintendo Switch", "Xbox Series X/S"]

        # Detectar intención temática en la consulta original
        has_cheats = any(w in norm_q for w in ["truco", "trucos", "cheat", "cheats", "codigo", "codigos"])
        has_secrets = any(w in norm_q for w in ["secreto", "secretos", "secret", "secrets", "easter egg", "misterio"])
        has_glitches = any(w in norm_q for w in ["glitch", "glitches", "bug", "dupe", "exploit"])
        has_guides = any(w in norm_q for w in ["guia", "guias", "guide", "guides", "walkthrough", "100%"])
        has_mods = any(w in norm_q for w in ["mod", "mods", "modding", "texturas", "patch", "parche"])
        has_community = any(w in norm_q for w in ["comunidad", "reddit", "foro", "forum", "discord"])

        generated_queries: List[str] = []

        # Siempre incluir la consulta original en primer lugar
        generated_queries.append(clean_raw)

        # Reglas de generación para consultas específicas de GTA V / GTA / Zelda / Generales
        if "gta" in norm_q or canonical_game and "Grand Theft Auto" in canonical_game:
            # Plantilla requerida para GTA V / GTA
            name1 = acronym_name  # GTA V / GTA 5
            name2 = primary_name  # GTA 5
            
            if has_cheats or has_secrets or not (has_guides or has_mods):
                generated_queries.extend([
                    f"{name2} hidden secrets",
                    f"{name1} cheat codes",
                    f"{name2} easter eggs",
                    f"{name1} rare locations",
                    f"{name2} hidden missions",
                    f"{name1} glitches",
                    f"{name2} community discoveries",
                    f"{name1} undocumented features",
                    f"{name1} secrets Reddit",
                    f"{name1} guides forums",
                    f"{name1} mods GitHub",
                    f"{name1} game files research",
                ])
            if has_mods:
                generated_queries.extend([
                    f"{name1} script hook mods GitHub",
                    f"{name2} best graphics mod",
                    f"{name1} fan translation patch"
                ])
        elif "zelda" in norm_q or canonical_game and "Zelda" in canonical_game:
            # Plantilla requerida para Zelda (TOTK, BOTW, TP, etc.)
            name1 = primary_name  # Zelda TOTK / Zelda Twilight Princess
            name2 = acronym_name  # TOTK / Zelda TP

            generated_queries.extend([
                f"{name1} secrets",
                f"{name2} hidden mechanics",
                f"{name1} glitches",
                f"{name2} walkthrough",
                f"{name1} shrines guide" if "totk" in norm_q or "botw" in norm_q else f"{name1} 100% walkthrough",
                f"{name2} hidden locations",
                f"{name1} discoveries Reddit",
                f"{name2} community forums",
                f"{name1} speedrun",
                f"{name2} mods",
                f"{name1} game research",
            ])
        else:
            # Plantilla universal gamer para otros videojuegos (Elden Ring, Minecraft, RDR2, etc.)
            generated_queries.extend([
                f"{primary_name} secrets",
                f"{primary_name} cheat codes" if has_cheats else f"{primary_name} hidden secrets",
                f"{primary_name} glitches and exploits",
                f"{primary_name} walkthrough guide",
                f"{primary_name} community Reddit",
                f"{primary_name} mods and tools",
                f"{primary_name} speedrun leaderboards",
                f"{primary_name} game files research"
            ])

        # Variaciones por plataforma relevante
        if platforms:
            for p in platforms[:3]:
                if has_cheats:
                    generated_queries.append(f"{primary_name} trucos {p}")
                elif has_guides:
                    generated_queries.append(f"{primary_name} guia {p}")

        # Consulta en japonés si existe título oficial
        if japanese_name:
            generated_queries.append(f"{japanese_name} 攻略")

        # Sugerencias vivas de Google Suggest / OpenSearch en tiempo real
        live_suggs: List[str] = []
        if fetch_live_suggestions:
            base_for_sugg = f"{primary_name} trucos" if has_cheats else primary_name
            live_suggs = self.fetch_live_engine_suggestions(base_for_sugg, limit=4)
            for s in live_suggs:
                if s not in generated_queries:
                    generated_queries.append(s)

        # Deduplicar preservando el orden
        seen = set()
        dedup_queries = []
        for q in generated_queries:
            q_clean = q.strip()
            q_lower = q_clean.lower()
            if q_lower not in seen and len(q_clean) > 2:
                seen.add(q_lower)
                dedup_queries.append(q_clean)

        return {
            "original_query": clean_raw,
            "detected_game": canonical_game,
            "canonical_metadata": game_meta,
            "total_generated": len(dedup_queries),
            "expanded_queries": dedup_queries,
            "live_suggestions": live_suggs,
            "categories_covered": [
                "secrets", "cheats", "easter_eggs", "glitches",
                "walkthrough", "community_reddit", "mods_github", "game_research"
            ]
        }

    def expand_multilingual_game_queries(
        self,
        title: str,
        aliases: Optional[List[str]] = None,
        platform: str = ""
    ) -> Dict[str, Any]:
        """
        Genera el árbol estructurado de consultas de investigación multilingüe (Fase 8 / Sección 9):
        - Español (ES): trucos, secretos, guías, glitches, comunidades, speedrun.
        - Inglés (EN): secrets, hidden items, glitches, walkthrough, community, speedrun, Reddit, forums.
        - Japonés (JA): 攻略 (kōryaku), 裏技 (urawaza), バグ (glitch), スピードラン (speedrun).
        - Portugués (PT): dicas, segredos, detonado completo, trapaças, comunidade, speedrun.
        - Global/Otros: enlaces específicos a foros y agregadores internacionales.
        """
        clean_title = title.strip()
        short_title = aliases[0] if aliases and len(aliases) > 0 else clean_title.split(":")[0]

        es_queries = [
            f"{clean_title} trucos y secretos",
            f"{short_title} objetos ocultos y armas secretas",
            f"{clean_title} guia completa paso a paso 100%",
            f"{short_title} glitches conocidos y atajos",
            f"{clean_title} comunidad foros reddit espanol",
            f"{short_title} speedrun espanol"
        ]

        en_queries = [
            f"{clean_title} secrets",
            f"{short_title} hidden items",
            f"{clean_title} glitches",
            f"{short_title} walkthrough",
            f"{clean_title} community",
            f"{short_title} speedrun",
            f"{short_title} Reddit",
            f"{clean_title} forums"
        ]

        ja_queries = [
            f"{clean_title} 攻略",
            f"{short_title} 裏技",
            f"{clean_title} バグ",
            f"{short_title} スピードラン",
            f"{clean_title} コミュニティ"
        ]

        pt_queries = [
            f"{clean_title} dicas e segredos",
            f"{short_title} detonado completo",
            f"{clean_title} itens ocultos",
            f"{short_title} trapaças",
            f"{clean_title} comunidade brasil",
            f"{short_title} speedrun brasil"
        ]

        all_flat = []
        for q_list in [es_queries, en_queries, ja_queries, pt_queries]:
            all_flat.extend(q_list)

        return {
            "title": clean_title,
            "short_title": short_title,
            "platform": platform,
            "languages": {
                "es": es_queries,
                "en": en_queries,
                "ja": ja_queries,
                "pt": pt_queries
            },
            "total_queries": len(all_flat),
            "all_queries": all_flat
        }


# Instancia singleton del motor de expansión
QUERY_EXPANDER = GamerQueryExpander()
