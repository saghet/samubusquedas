"""
Gamer Search Engine - Motor de Normalización y Traducción Multilingüe Gamer (ES <-> EN)
======================================================================================
Traduce y expande bidireccionalmente la jerga y términos técnicos entre Español e Inglés
para que consultas en español descubran guías en foros angloparlantes (Reddit, GameFAQs)
y consultas en inglés descubran recursos en comunidades hispanas.
"""

import re
import unicodedata
from typing import Dict, List, Set, Tuple


# Diccionario bidireccional de conceptos y jerga gamer
GAMER_BILINGUAL_DICTIONARY: Dict[str, List[str]] = {
    # Guías y estrategias
    "truco": ["cheat", "code", "trick", "glitch"],
    "trucos": ["cheats", "cheat codes", "glitches", "tricks", "secrets"],
    "cheat": ["truco", "trucos", "codigo"],
    "cheats": ["trucos", "codigos", "glitches"],
    "guia": ["guide", "walkthrough", "tutorial", "faq"],
    "guias": ["guides", "walkthroughs", "tutorials", "faqs"],
    "walkthrough": ["guia completa", "paso a paso", "recorrido"],
    "walkthroughs": ["guias completas", "paso a paso"],
    "build": ["configuracion de personaje", "armado", "atributos", "build"],
    "builds": ["configuraciones", "armados de personaje", "atributos"],
    "estrategia": ["strategy", "tactics", "build"],
    "estrategias": ["strategies", "tactics", "builds"],
    
    # Secretos y logros
    "secreto": ["secret", "hidden", "easter egg"],
    "secretos": ["secrets", "hidden secrets", "easter eggs"],
    "desbloqueable": ["unlockable", "secret item", "suit"],
    "desbloqueables": ["unlockables", "secret suits", "rewards"],
    "trofeo": ["trophy", "achievement"],
    "trofeos": ["trophies", "achievements", "platinum"],
    "platino": ["platinum trophy", "100 percent completion"],
    "logro": ["achievement", "gamerscore"],
    "logros": ["achievements", "1000g", "gamerscore"],
    "calaveras": ["skulls", "hidden skulls"],
    "easter egg": ["huevo de pascua", "secreto", "cameo"],
    "easter eggs": ["huevos de pascua", "secretos ocultos", "cameos"],
    
    # Preservación y emulación
    "emulador": ["emulator", "frontend", "core"],
    "emuladores": ["emulators", "cores", "libretro"],
    "preservacion": ["preservation", "digital heritage", "archival"],
    "parche": ["patch", "translation patch", "ips", "bps"],
    "parches": ["patches", "translation patches", "mods"],
    "traduccion": ["translation", "fan translation", "english patch", "spanish patch"],
    "traducciones": ["translations", "fan translations", "localization"],
    "descompilacion": ["decompilation", "reverse engineering", "clean room", "native port"],
    "homebrew": ["software casero", "indie retro", "juego independiente"],
    "pantalla ancha": ["widescreen", "16:9", "ultrawide"],
    "requisitos": ["requirements", "system specs", "hardware specs"],
    "lanzamiento": ["release date", "launch", "release"],
    
    # Comunidades
    "comunidad": ["community", "subreddit", "discord server", "forum"],
    "comunidades": ["communities", "subreddits", "discord servers", "forums"],
    "foro": ["forum", "message board", "discussion"],
    "foros": ["forums", "boards", "discussions"],
    "jugadores": ["players", "gamers", "tarnished", "speedrunners"],
    "partida rapida": ["speedrun", "any percent", "100 percent run"],
    "records": ["leaderboards", "world records", "wr"],
}


class GamerTranslationEngine:
    """Motor de traducción automática de términos gamer para búsquedas multilingües."""

    def __init__(self):
        pass

    def normalize(self, text: str) -> str:
        if not text:
            return ""
        nfd = unicodedata.normalize("NFD", text.lower())
        clean = "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")
        return re.sub(r"\s+", " ", clean).strip()

    def translate_and_expand_query(self, raw_query: str) -> List[str]:
        """
        Analiza los tokens de la consulta y genera variantes traducidas (ES <-> EN).
        Retorna la lista de términos expandidos para potenciar el recall en FTS5.
        """
        if not raw_query:
            return []

        norm = self.normalize(raw_query)
        tokens = norm.split()
        expanded: Set[str] = set()

        # Comprobar frases de múltiples palabras
        for phrase, translations in GAMER_BILINGUAL_DICTIONARY.items():
            if phrase in norm:
                for trans in translations:
                    expanded.add(trans)

        # Comprobar tokens individuales
        for token in tokens:
            if token in GAMER_BILINGUAL_DICTIONARY:
                for trans in GAMER_BILINGUAL_DICTIONARY[token]:
                    expanded.add(trans)

        return sorted(list(expanded))

    def get_bilingual_explanation(self, term: str) -> Tuple[str, List[str]]:
        """Devuelve la traducción técnica recomendada para un término gamer."""
        norm = self.normalize(term)
        translations = GAMER_BILINGUAL_DICTIONARY.get(norm, [])
        return norm, translations


# Instancia singleton
GAMER_TRANSLATOR = GamerTranslationEngine()
