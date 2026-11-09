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
    """Ficha técnica individual exhaustiva de videojuego con los 24 atributos requeridos."""
    id: str
    title: str  # 1. Nombre oficial
    aliases: List[str] = field(default_factory=list)  # 2. Nombre alternativo y títulos multilingües
    cover_url: str = ""  # 3. Portada
    screenshots: List[str] = field(default_factory=list)  # 4. Capturas de pantalla
    platforms: List[str] = field(default_factory=list)  # 5. Plataforma
    canonical_platform_id: str = ""  # ID de consola en console_inventory
    generation: str = ""  # 6. Generación (ej. "9ª Generación")
    generation_number: int = 0
    release_date: str = ""  # 7. Fecha de lanzamiento exacta
    release_year: int = 0
    developer: str = ""  # 8. Desarrollador
    publisher: str = ""  # 9. Distribuidor
    genres: List[str] = field(default_factory=list)  # 10. Género
    languages: List[str] = field(default_factory=list)  # 11. Idiomas
    regions_released: List[str] = field(default_factory=list)  # 12. Regiones
    critic_score: float = 0.0  # 13. Valoración de crítica (0-100)
    user_score: float = 0.0  # 14. Valoración de usuarios (0-100)
    sales_documented: str = "No reportada oficialmente"  # 15. Ventas documentadas
    units_sold_millions: Optional[float] = None
    rank_position: int = 0  # 16. Posición en el ranking
    summary: str = ""  # 17. Descripción
    features: List[str] = field(default_factory=list)  # 18. Características
    dlcs: List[str] = field(default_factory=list)  # 19. DLC
    expansions: List[str] = field(default_factory=list)  # 20. Expansiones
    versions: List[str] = field(default_factory=list)  # 21. Versiones / Ediciones
    editions: List[str] = field(default_factory=list)  # Compatibilidad con semillas existentes
    updates_patches: List[str] = field(default_factory=list)
    remasters: List[str] = field(default_factory=list)  # 22. Remasterizaciones
    remakes: List[str] = field(default_factory=list)  # 23. Remakes
    backward_compatibility: Dict[str, Any] = field(default_factory=dict)  # 24. Compatibilidad retroactiva
    
    # Metadatos analíticos y de auditoría
    score_5d: Dict[str, Any] = field(default_factory=dict)  # Desglose del algoritmo 5D
    consulted_sources: List[Dict[str, str]] = field(default_factory=list)  # Mínimo 3 fuentes independientes
    updated_date: str = ""
    rating: float = 0.0
    rating_source: str = ""
    price_status: str = ""
    compatibility: str = ""
    technical_requirements: str = ""
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
