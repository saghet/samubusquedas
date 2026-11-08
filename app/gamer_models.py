"""
Gamer Search Engine - Modelos de Datos Tipados y Validaciones
============================================================
Entidades del dominio de videojuegos, trucos, preservación digital y comunidades gamer.
Cumple con la arquitectura modular para los 3 ecosistemas prioritarios:
- Nintendo (Switch y plataformas retro)
- PlayStation (PS5 y generaciones previas)
- Xbox (Xbox Series X/S y generaciones previas)
Además de retro, arcade y preservación histórica.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
import datetime


@dataclass
class GameRecord:
    id: str
    title: str
    aliases: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)
    release_year: int = 0
    release_date: str = ""
    developer: str = ""
    publisher: str = ""
    genres: List[str] = field(default_factory=list)
    editions: List[str] = field(default_factory=list)
    dlcs: List[str] = field(default_factory=list)
    updates_patches: List[str] = field(default_factory=list)
    compatibility: str = ""
    technical_requirements: str = ""
    rating: float = 0.0
    rating_source: str = ""
    price_status: str = ""
    summary: str = ""
    cover_url: str = ""
    tags: List[str] = field(default_factory=list)
    region: str = "Global"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CheatRecord:
    id: str
    game_title: str
    platform: str
    category: str  # trucos_codigos, easter_eggs, secretos, desbloqueables, personajes, armas_habilidades, mapas, glitches, walkthroughs, guias_100, trofeos_ps, logros_xbox, desafios_nintendo
    title: str
    content: str
    original_source: str
    source_url: str
    verified_date: str = ""
    updated_date: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PreservationRecord:
    id: str
    title: str
    game_title: str
    platform: str
    item_type: str  # homebrew, freeware, public_domain, demo, translation_patch, mod, modding_tool, compatibility_database, emulator, technical_documentation
    description: str
    developer_author: str
    source_url: str
    license: str
    legal_status: str  # LEGAL_VERIFIED, COMMUNITY_PATCH, PRESERVATION_AUTHORIZED
    download_safe: bool = True
    safe_download_url: str = ""
    sha256: str = ""
    technical_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CommunityRecord:
    id: str
    name: str
    platform: str  # Nintendo, PlayStation 5, Xbox Series X/S, Retro, Multiplataforma
    theme: str  # General, Builds & Estrategias, Speedrunning, Emulación, Modding, Esports, Preservación
    platform_type: str  # reddit, discord, forum, speedrun, modding, esports, facebook
    related_games: List[str] = field(default_factory=list)
    members_count: int = 0
    members_display: str = ""
    recent_activity: str = ""
    language: str = "Español / Inglés"
    official_url: str = ""
    entry_requirements: str = "Público / Libre acceso"
    activity_level: str = "Alta"  # Muy Alta, Alta, Media, Baja
    verified: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SourceSecurityReport:
    domain: str
    reputation_score: float = 100.0  # 0.0 a 100.0
    safety_tier: str = "CONFIABLE_VERIFICADO"  # CONFIABLE_VERIFICADO, COMUNITARIO_SEGURO, PRECAUCION, PELIGROSO_BLOQUEADO
    flags: List[str] = field(default_factory=list)
    warning_message: str = ""
    is_known_malicious: bool = False
    has_fake_download_traps: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
