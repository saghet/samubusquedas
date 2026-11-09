"""
Gaming Discovery & Intelligence Engine - Inventario Histórico de Consolas y Generaciones (Fase 2)
================================================================================================
Modelado formal y delimitación estricta de hardware para:
- Nintendo (Sobremesa actual y 4 anteriores + Catálogo independiente de portátiles y retro)
- PlayStation (Sobremesa actual y 4 anteriores + Catálogo independiente de portátiles PSP y PS Vita)
- Xbox (Sobremesa actual y 3 anteriores + Sistema de resolución de retrocompatibilidad)

Reglas de Oro del Historiador y Arquitecto:
1. No mezclar consolas de sobremesa con portátiles en las cronologías. Mantenerlas como líneas independientes.
2. No contabilizar una versión retrocompatible o parcheada (ej. Smart Delivery, FPS Boost) como un juego nuevo.
3. Permitir actualización dinámica del inventario ante nuevas plataformas.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class Manufacturer(str, Enum):
    NINTENDO = "Nintendo"
    PLAYSTATION = "Sony PlayStation"
    XBOX = "Microsoft Xbox"


class PlatformLine(str, Enum):
    HOME_CONSOLE = "Sobremesa"
    HANDHELD_CONSOLE = "Portátil"
    HYBRID_CONSOLE = "Híbrida"


@dataclass
class ConsoleRecord:
    id: str
    name: str
    short_name: str
    manufacturer: str
    line: str  # Sobremesa, Portátil, Híbrida
    generation_number: int  # 9 (actual), 8, 7, 6, 5, etc.
    generation_label: str  # "Generación Actual (9ª)", "6ª Generación (128-bit)", etc.
    release_year: int
    lifespan: str
    media_format: str
    target_top_games: int = 30
    is_current_gen: bool = False
    is_previous_4_gen: bool = False
    is_retro_handheld_catalogue: bool = False
    backward_compatibility_info: Dict[str, Any] = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)
    hardware_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =====================================================================
# CATÁLOGO CANÓNICO DE PLATAFORMAS HISTÓRICAS
# =====================================================================

CANONICAL_CONSOLES: Dict[str, ConsoleRecord] = {
    # -----------------------------------------------------------------
    # A. NINTENDO: LÍNEA SOBREMESA / HÍBRIDA (Actual y 4 anteriores)
    # -----------------------------------------------------------------
    "nintendo_switch_2": ConsoleRecord(
        id="nintendo_switch_2",
        name="Nintendo Switch 2",
        short_name="Switch 2",
        manufacturer=Manufacturer.NINTENDO.value,
        line=PlatformLine.HYBRID_CONSOLE.value,
        generation_number=10,
        generation_label="Generación Emergente / Próxima Generación",
        release_year=2025,
        lifespan="2025 - Presente",
        media_format="Cartucho de Alta Densidad / Digital NVMe",
        target_top_games=30,
        is_current_gen=True,
        is_previous_4_gen=False,
        is_retro_handheld_catalogue=False,
        backward_compatibility_info={
            "supports_backward_compat": True,
            "compatible_platforms": ["Nintendo Switch"],
            "notes": "Retrocompatibilidad con el catálogo digital y físico de Nintendo Switch, mejoras de rendimiento."
        },
        aliases=["switch 2", "ns2", "nintendo switch 2", "switch successor"],
        hardware_notes="Arquitectura híbrida de nueva generación basada en SoC NVIDIA personalizado con DLSS."
    ),
    "nintendo_switch": ConsoleRecord(
        id="nintendo_switch",
        name="Nintendo Switch",
        short_name="Switch",
        manufacturer=Manufacturer.NINTENDO.value,
        line=PlatformLine.HYBRID_CONSOLE.value,
        generation_number=9,
        generation_label="Generación Actual (9ª Generación)",
        release_year=2017,
        lifespan="2017 - Presente",
        media_format="Game Card propietaria / eShop Digital",
        target_top_games=30,
        is_current_gen=True,
        is_previous_4_gen=False,
        is_retro_handheld_catalogue=False,
        backward_compatibility_info={
            "supports_backward_compat": False,
            "compatible_platforms": [],
            "notes": "Sin compatibilidad física directa; catálogo retro ofrecido a través de emulación oficial Nintendo Switch Online."
        },
        aliases=["switch", "nintendo switch", "ns", "switch oled", "switch lite"],
        hardware_notes="Consola híbrida con Joy-Con desacoplables y dock HDMI para televisión."
    ),
    "nintendo_wii_u": ConsoleRecord(
        id="nintendo_wii_u",
        name="Nintendo Wii U",
        short_name="Wii U",
        manufacturer=Manufacturer.NINTENDO.value,
        line=PlatformLine.HOME_CONSOLE.value,
        generation_number=8,
        generation_label="8ª Generación de Sobremesa",
        release_year=2012,
        lifespan="2012 - 2017",
        media_format="Disco Óptico Wii U (25 GB) / Disco Wii",
        target_top_games=30,
        is_current_gen=False,
        is_previous_4_gen=True,
        is_retro_handheld_catalogue=False,
        backward_compatibility_info={
            "supports_backward_compat": True,
            "compatible_platforms": ["Nintendo Wii"],
            "notes": "Compatibilidad 100% nativa con discos ópticos y periféricos (Wiimotes, Nunchuks, Balance Board) de Wii."
        },
        aliases=["wii u", "wiiu", "nintendo wii u"],
        hardware_notes="Primera consola HD de Nintendo con pantalla secundaria táctil capacitiva en el Wii U GamePad."
    ),
    "nintendo_wii": ConsoleRecord(
        id="nintendo_wii",
        name="Nintendo Wii",
        short_name="Wii",
        manufacturer=Manufacturer.NINTENDO.value,
        line=PlatformLine.HOME_CONSOLE.value,
        generation_number=7,
        generation_label="7ª Generación de Sobremesa",
        release_year=2006,
        lifespan="2006 - 2013",
        media_format="Disco Óptico Wii (12 cm) / Disco GameCube (8 cm)",
        target_top_games=30,
        is_current_gen=False,
        is_previous_4_gen=True,
        is_retro_handheld_catalogue=False,
        backward_compatibility_info={
            "supports_backward_compat": True,
            "compatible_platforms": ["Nintendo GameCube"],
            "notes": "Los modelos originales (RVL-001) incluyen puertos de mandos y memory cards de GameCube."
        },
        aliases=["wii", "nintendo wii", "rvl-001"],
        hardware_notes="Revolución por control de movimiento (Wii Remote y MotionPlus)."
    ),
    "nintendo_gamecube": ConsoleRecord(
        id="nintendo_gamecube",
        name="Nintendo GameCube",
        short_name="GameCube",
        manufacturer=Manufacturer.NINTENDO.value,
        line=PlatformLine.HOME_CONSOLE.value,
        generation_number=6,
        generation_label="6ª Generación de Sobremesa (128-bit)",
        release_year=2001,
        lifespan="2001 - 2007",
        media_format="MiniDVD Propietario (1.5 GB)",
        target_top_games=30,
        is_current_gen=False,
        is_previous_4_gen=True,
        is_retro_handheld_catalogue=False,
        backward_compatibility_info={
            "supports_backward_compat": False,
            "compatible_platforms": [],
            "notes": "Soporta Game Boy Player mediante periférico inferior para ejecutar juegos de GB, GBC y GBA."
        },
        aliases=["gamecube", "nintendo gamecube", "gcn", "gc", "dol-001"],
        hardware_notes="Procesador IBM PowerPC Gekko y GPU ATI Flipper con salida progresiva 480p."
    ),

    # -----------------------------------------------------------------
    # A2. NINTENDO: CATÁLOGO RETRO INDEPENDIENTE (Sobremesa Clásica)
    # -----------------------------------------------------------------
    "nintendo_64": ConsoleRecord(
        id="nintendo_64",
        name="Nintendo 64",
        short_name="N64",
        manufacturer=Manufacturer.NINTENDO.value,
        line=PlatformLine.HOME_CONSOLE.value,
        generation_number=5,
        generation_label="5ª Generación de Sobremesa (64-bit)",
        release_year=1996,
        lifespan="1996 - 2002",
        media_format="Cartucho ROM (4 a 64 MB)",
        target_top_games=30,
        is_current_gen=False,
        is_previous_4_gen=False,
        is_retro_handheld_catalogue=True,
        backward_compatibility_info={"supports_backward_compat": False, "compatible_platforms": []},
        aliases=["n64", "nintendo 64", "ultra 64"],
        hardware_notes="Pionera en entornos 3D en tiempo real con stick analógico y Expansion Pak (8MB RAM)."
    ),
    "super_nintendo": ConsoleRecord(
        id="super_nintendo",
        name="Super Nintendo Entertainment System",
        short_name="SNES",
        manufacturer=Manufacturer.NINTENDO.value,
        line=PlatformLine.HOME_CONSOLE.value,
        generation_number=4,
        generation_label="4ª Generación de Sobremesa (16-bit)",
        release_year=1990,
        lifespan="1990 - 1999",
        media_format="Cartucho ROM (hasta 48 Mbit)",
        target_top_games=30,
        is_current_gen=False,
        is_previous_4_gen=False,
        is_retro_handheld_catalogue=True,
        backward_compatibility_info={"supports_backward_compat": False, "compatible_platforms": []},
        aliases=["snes", "super nintendo", "super famicom", "sfc"],
        hardware_notes="Procesador Ricoh 5A22 con Modo 7 y chips de apoyo como Super FX."
    ),
    "nes": ConsoleRecord(
        id="nes",
        name="Nintendo Entertainment System",
        short_name="NES",
        manufacturer=Manufacturer.NINTENDO.value,
        line=PlatformLine.HOME_CONSOLE.value,
        generation_number=3,
        generation_label="3ª Generación de Sobremesa (8-bit)",
        release_year=1983,
        lifespan="1983 - 1995",
        media_format="Cartucho ROM 72-pin (NES) / 60-pin (Famicom)",
        target_top_games=30,
        is_current_gen=False,
        is_previous_4_gen=False,
        is_retro_handheld_catalogue=True,
        backward_compatibility_info={"supports_backward_compat": False, "compatible_platforms": []},
        aliases=["nes", "nintendo entertainment system", "famicom", "family computer"],
        hardware_notes="Plataforma que revitalizó la industria tras la crisis del videojuego de 1983."
    ),

    # -----------------------------------------------------------------
    # A3. NINTENDO: CATÁLOGO INDEPENDIENTE DE PORTÁTILES
    # -----------------------------------------------------------------
    "nintendo_3ds": ConsoleRecord(
        id="nintendo_3ds",
        name="Nintendo 3DS",
        short_name="3DS",
        manufacturer=Manufacturer.NINTENDO.value,
        line=PlatformLine.HANDHELD_CONSOLE.value,
        generation_number=8,
        generation_label="Portátil Generación 8",
        release_year=2011,
        lifespan="2011 - 2020",
        media_format="Cartucho 3DS (hasta 8 GB) / SD Card",
        target_top_games=30,
        is_current_gen=False,
        is_previous_4_gen=False,
        is_retro_handheld_catalogue=True,
        backward_compatibility_info={
            "supports_backward_compat": True,
            "compatible_platforms": ["Nintendo DS"],
            "notes": "Compatibilidad física directa con cartuchos de Nintendo DS y DSi."
        },
        aliases=["3ds", "nintendo 3ds", "2ds", "new 3ds", "new 3ds xl"],
        hardware_notes="Pantalla superior 3D estereoscópica autoestereoscópica sin gafas."
    ),
    "nintendo_ds": ConsoleRecord(
        id="nintendo_ds",
        name="Nintendo DS",
        short_name="NDS",
        manufacturer=Manufacturer.NINTENDO.value,
        line=PlatformLine.HANDHELD_CONSOLE.value,
        generation_number=7,
        generation_label="Portátil Generación 7",
        release_year=2004,
        lifespan="2004 - 2013",
        media_format="Cartucho DS (hasta 512 MB)",
        target_top_games=30,
        is_current_gen=False,
        is_previous_4_gen=False,
        is_retro_handheld_catalogue=True,
        backward_compatibility_info={
            "supports_backward_compat": True,
            "compatible_platforms": ["Game Boy Advance"],
            "notes": "Modelos original y DS Lite cuentan con Slot-2 para cartuchos GBA."
        },
        aliases=["nds", "nintendo ds", "ds lite", "dsi"],
        hardware_notes="Doble pantalla (inferior táctil resistiva) y micrófono integrado."
    ),
    "game_boy_advance": ConsoleRecord(
        id="game_boy_advance",
        name="Game Boy Advance",
        short_name="GBA",
        manufacturer=Manufacturer.NINTENDO.value,
        line=PlatformLine.HANDHELD_CONSOLE.value,
        generation_number=6,
        generation_label="Portátil Generación 6 (32-bit)",
        release_year=2001,
        lifespan="2001 - 2008",
        media_format="Cartucho GBA (hasta 32 MB)",
        target_top_games=30,
        is_current_gen=False,
        is_previous_4_gen=False,
        is_retro_handheld_catalogue=True,
        backward_compatibility_info={
            "supports_backward_compat": True,
            "compatible_platforms": ["Game Boy", "Game Boy Color"],
            "notes": "GBA y GBA SP contienen procesador Z80 secundario para soporte retro completo."
        },
        aliases=["gba", "game boy advance", "gba sp", "game boy micro"],
        hardware_notes="CPU ARM7TDMI de 32 bits a 16.78 MHz."
    ),
    "game_boy_color": ConsoleRecord(
        id="game_boy_color",
        name="Game Boy Color",
        short_name="GBC",
        manufacturer=Manufacturer.NINTENDO.value,
        line=PlatformLine.HANDHELD_CONSOLE.value,
        generation_number=5,
        generation_label="Portátil Generación 5",
        release_year=1998,
        lifespan="1998 - 2003",
        media_format="Cartucho GBC (doble muesca / transparente)",
        target_top_games=30,
        is_current_gen=False,
        is_previous_4_gen=False,
        is_retro_handheld_catalogue=True,
        backward_compatibility_info={
            "supports_backward_compat": True,
            "compatible_platforms": ["Game Boy"],
            "notes": "Compatibilidad retro total con paletas de color asignables."
        },
        aliases=["gbc", "game boy color"],
        hardware_notes="Pantalla a color reflectiva TFT sin retroiluminación."
    ),
    "game_boy": ConsoleRecord(
        id="game_boy",
        name="Game Boy",
        short_name="GB",
        manufacturer=Manufacturer.NINTENDO.value,
        line=PlatformLine.HANDHELD_CONSOLE.value,
        generation_number=4,
        generation_label="Portátil Generación 4 (8-bit)",
        release_year=1989,
        lifespan="1989 - 2003",
        media_format="Cartucho Game Boy (gris)",
        target_top_games=30,
        is_current_gen=False,
        is_previous_4_gen=False,
        is_retro_handheld_catalogue=True,
        backward_compatibility_info={"supports_backward_compat": False, "compatible_platforms": []},
        aliases=["gb", "game boy", "game boy pocket", "game boy light"],
        hardware_notes="Diseñada por Gunpei Yokoi con CPU Sharp LR35902 monocromática."
    ),

    # -----------------------------------------------------------------
    # B. PLAYSTATION: LÍNEA SOBREMESA (Actual y 4 anteriores)
    # -----------------------------------------------------------------
    "playstation_5": ConsoleRecord(
        id="playstation_5",
        name="PlayStation 5",
        short_name="PS5",
        manufacturer=Manufacturer.PLAYSTATION.value,
        line=PlatformLine.HOME_CONSOLE.value,
        generation_number=9,
        generation_label="Generación Actual (9ª Generación)",
        release_year=2020,
        lifespan="2020 - Presente",
        media_format="Ultra HD Blu-ray (100 GB) / SSD NVMe Digital",
        target_top_games=30,
        is_current_gen=True,
        is_previous_4_gen=False,
        is_retro_handheld_catalogue=False,
        backward_compatibility_info={
            "supports_backward_compat": True,
            "compatible_platforms": ["PlayStation 4"],
            "notes": "Retrocompatibilidad con más del 99% del catálogo de PS4 con Game Boost."
        },
        aliases=["ps5", "playstation 5", "playstation5", "ps5 slim", "ps5 pro"],
        hardware_notes="SSD PCIe 4.0 ultra-rápido (5.5 GB/s), audio 3D Tempest y mando DualSense háptico."
    ),
    "playstation_4": ConsoleRecord(
        id="playstation_4",
        name="PlayStation 4",
        short_name="PS4",
        manufacturer=Manufacturer.PLAYSTATION.value,
        line=PlatformLine.HOME_CONSOLE.value,
        generation_number=8,
        generation_label="8ª Generación de Sobremesa",
        release_year=2013,
        lifespan="2013 - Presente",
        media_format="Blu-ray Disc (50 GB) / HDD Digital",
        target_top_games=30,
        is_current_gen=False,
        is_previous_4_gen=True,
        is_retro_handheld_catalogue=False,
        backward_compatibility_info={
            "supports_backward_compat": False,
            "compatible_platforms": [],
            "notes": "Sin compatibilidad física nativa con PS3, PS2 ni PS1; emulación parcial PS2 Classics."
        },
        aliases=["ps4", "playstation 4", "playstation4", "ps4 slim", "ps4 pro"],
        hardware_notes="Arquitectura x86-64 AMD Jaguar con memoria unificada GDDR5 de 8 GB."
    ),
    "playstation_3": ConsoleRecord(
        id="playstation_3",
        name="PlayStation 3",
        short_name="PS3",
        manufacturer=Manufacturer.PLAYSTATION.value,
        line=PlatformLine.HOME_CONSOLE.value,
        generation_number=7,
        generation_label="7ª Generación de Sobremesa",
        release_year=2006,
        lifespan="2006 - 2017",
        media_format="Blu-ray Disc (25/50 GB) / DVD / CD",
        target_top_games=30,
        is_current_gen=False,
        is_previous_4_gen=True,
        is_retro_handheld_catalogue=False,
        backward_compatibility_info={
            "supports_backward_compat": True,
            "compatible_platforms": ["PlayStation 1", "PlayStation 2 (Modelos de lanzamiento 20/60GB)"],
            "notes": "Todos los modelos soportan discos de PS1. Los modelos originales CECHA/CECHB incluyen hardware Emotion Engine de PS2."
        },
        aliases=["ps3", "playstation 3", "playstation3", "ps3 slim", "ps3 super slim"],
        hardware_notes="Arquitectura Cell Broadband Engine con 1 PPE y 7 SPEs y GPU RSX."
    ),
    "playstation_2": ConsoleRecord(
        id="playstation_2",
        name="PlayStation 2",
        short_name="PS2",
        manufacturer=Manufacturer.PLAYSTATION.value,
        line=PlatformLine.HOME_CONSOLE.value,
        generation_number=6,
        generation_label="6ª Generación de Sobremesa (128-bit)",
        release_year=2000,
        lifespan="2000 - 2013",
        media_format="DVD-ROM (4.7/8.5 GB) / CD-ROM",
        target_top_games=30,
        is_current_gen=False,
        is_previous_4_gen=True,
        is_retro_handheld_catalogue=False,
        backward_compatibility_info={
            "supports_backward_compat": True,
            "compatible_platforms": ["PlayStation 1"],
            "notes": "Compatibilidad de hardware nativa casi al 100% con discos y memory cards de PS1."
        },
        aliases=["ps2", "playstation 2", "playstation2", "ps2 slim"],
        hardware_notes="La consola más vendida de la historia (>158 millones de unidades) con CPU Emotion Engine."
    ),
    "playstation_1": ConsoleRecord(
        id="playstation_1",
        name="PlayStation (PS1)",
        short_name="PS1",
        manufacturer=Manufacturer.PLAYSTATION.value,
        line=PlatformLine.HOME_CONSOLE.value,
        generation_number=5,
        generation_label="5ª Generación de Sobremesa (32-bit)",
        release_year=1994,
        lifespan="1994 - 2006",
        media_format="CD-ROM (650 MB)",
        target_top_games=30,
        is_current_gen=False,
        is_previous_4_gen=True,
        is_retro_handheld_catalogue=False,
        backward_compatibility_info={"supports_backward_compat": False, "compatible_platforms": []},
        aliases=["ps1", "psx", "playstation", "playstation 1", "psone"],
        hardware_notes="CPU MIPS R3000A de 32 bits a 33.86 MHz con chip de sonido SPU de 24 canales."
    ),

    # -----------------------------------------------------------------
    # B2. PLAYSTATION: CATÁLOGO INDEPENDIENTE DE PORTÁTILES
    # -----------------------------------------------------------------
    "playstation_portable": ConsoleRecord(
        id="playstation_portable",
        name="PlayStation Portable (PSP)",
        short_name="PSP",
        manufacturer=Manufacturer.PLAYSTATION.value,
        line=PlatformLine.HANDHELD_CONSOLE.value,
        generation_number=7,
        generation_label="Portátil Generación 7",
        release_year=2004,
        lifespan="2004 - 2014",
        media_format="Universal Media Disc (UMD 1.8 GB) / Memory Stick PRO Duo",
        target_top_games=30,
        is_current_gen=False,
        is_previous_4_gen=False,
        is_retro_handheld_catalogue=True,
        backward_compatibility_info={
            "supports_backward_compat": True,
            "compatible_platforms": ["PlayStation 1 (Digital Classics)"],
            "notes": "Motor de emulación PS1 POPS integrado en firmware oficial."
        },
        aliases=["psp", "playstation portable", "psp slim", "psp-3000", "psp go", "psp street"],
        hardware_notes="Pantalla panorámica 16:9 LCD TFT y capacidades multimedia avanzadas."
    ),
    "playstation_vita": ConsoleRecord(
        id="playstation_vita",
        name="PlayStation Vita",
        short_name="PS Vita",
        manufacturer=Manufacturer.PLAYSTATION.value,
        line=PlatformLine.HANDHELD_CONSOLE.value,
        generation_number=8,
        generation_label="Portátil Generación 8",
        release_year=2011,
        lifespan="2011 - 2019",
        media_format="NVG Card propietaria / Tarjeta de Memoria PS Vita",
        target_top_games=30,
        is_current_gen=False,
        is_previous_4_gen=False,
        is_retro_handheld_catalogue=True,
        backward_compatibility_info={
            "supports_backward_compat": True,
            "compatible_platforms": ["PlayStation Portable (Digital)", "PlayStation 1 (Digital)"],
            "notes": "Sub-procesador ARM MIPS emula entorno PSP de forma nativa."
        },
        aliases=["ps vita", "psvita", "playstation vita", "vita slim"],
        hardware_notes="Pantalla OLED táctil capacitiva (PCH-1000), panel táctil trasero y dos sticks analógicos."
    ),

    # -----------------------------------------------------------------
    # C. XBOX: LÍNEA SOBREMESA (Actual y 3 anteriores)
    # -----------------------------------------------------------------
    "xbox_series_xs": ConsoleRecord(
        id="xbox_series_xs",
        name="Xbox Series X/S",
        short_name="Xbox Series",
        manufacturer=Manufacturer.XBOX.value,
        line=PlatformLine.HOME_CONSOLE.value,
        generation_number=9,
        generation_label="Generación Actual (9ª Generación)",
        release_year=2020,
        lifespan="2020 - Presente",
        media_format="Ultra HD Blu-ray (Series X) / SSD NVMe Digital",
        target_top_games=30,
        is_current_gen=True,
        is_previous_4_gen=False,
        is_retro_handheld_catalogue=False,
        backward_compatibility_info={
            "supports_backward_compat": True,
            "compatible_platforms": ["Xbox One", "Xbox 360", "Xbox original"],
            "notes": "Retrocompatibilidad líder en la industria: ejecuta miles de títulos de Xbox One, cientos de Xbox 360 y decenas de Xbox original con Auto-HDR, FPS Boost y resolución 4K nativa."
        },
        aliases=["xbox series x", "xbox series s", "xbox series", "xsx", "xss", "series x", "series s"],
        hardware_notes="Xbox Velocity Architecture, 12 TFLOPS RDNA2 (Series X) y Quick Resume de múltiples juegos."
    ),
    "xbox_one": ConsoleRecord(
        id="xbox_one",
        name="Xbox One",
        short_name="Xbox One",
        manufacturer=Manufacturer.XBOX.value,
        line=PlatformLine.HOME_CONSOLE.value,
        generation_number=8,
        generation_label="8ª Generación de Sobremesa",
        release_year=2013,
        lifespan="2013 - 2020",
        media_format="Blu-ray Disc (50 GB) / HDD Digital",
        target_top_games=30,
        is_current_gen=False,
        is_previous_4_gen=True,
        is_retro_handheld_catalogue=False,
        backward_compatibility_info={
            "supports_backward_compat": True,
            "compatible_platforms": ["Xbox 360", "Xbox original"],
            "notes": "Programa de retrocompatibilidad iniciado en 2015 que abarcó más de 600 juegos mediante recompilación estática y emulación por VM."
        },
        aliases=["xbox one", "xone", "xbox one s", "xbox one x", "durango"],
        hardware_notes="CPU AMD Jaguar de 8 núcleos con 8 GB DDR3 y 32 MB de eSRAM rápida."
    ),
    "xbox_360": ConsoleRecord(
        id="xbox_360",
        name="Xbox 360",
        short_name="Xbox 360",
        manufacturer=Manufacturer.XBOX.value,
        line=PlatformLine.HOME_CONSOLE.value,
        generation_number=7,
        generation_label="7ª Generación de Sobremesa",
        release_year=2005,
        lifespan="2005 - 2016",
        media_format="DVD-DL de 12 cm (hasta 7.8 GB) / HDD Digital",
        target_top_games=30,
        is_current_gen=False,
        is_previous_4_gen=True,
        is_retro_handheld_catalogue=False,
        backward_compatibility_info={
            "supports_backward_compat": True,
            "compatible_platforms": ["Xbox original"],
            "notes": "Soporte de casi la mitad del catálogo de Xbox original requiriendo disco duro oficial."
        },
        aliases=["xbox 360", "x360", "xbox360", "360 slim", "360 e"],
        hardware_notes="CPU tri-core Xenon PowerPC a 3.2 GHz con arquitectura unificada de shaders en GPU Xenos."
    ),
    "xbox_original": ConsoleRecord(
        id="xbox_original",
        name="Xbox (Original)",
        short_name="Xbox",
        manufacturer=Manufacturer.XBOX.value,
        line=PlatformLine.HOME_CONSOLE.value,
        generation_number=6,
        generation_label="6ª Generación de Sobremesa (128-bit)",
        release_year=2001,
        lifespan="2001 - 2009",
        media_format="DVD-ROM (hasta 8.5 GB)",
        target_top_games=30,
        is_current_gen=False,
        is_previous_4_gen=True,
        is_retro_handheld_catalogue=False,
        backward_compatibility_info={"supports_backward_compat": False, "compatible_platforms": []},
        aliases=["xbox", "xbox original", "og xbox", "xbox classic"],
        hardware_notes="Primera consola con disco duro interno de serie y puerto Ethernet para Xbox Live."
    ),
}


class ConsoleInventoryEngine:
    """Motor de gestión, consulta y deduplicación del inventario de plataformas."""

    def __init__(self):
        self._consoles = dict(CANONICAL_CONSOLES)

    def register_console(self, console: ConsoleRecord) -> None:
        """Permite registrar dinámicamente nuevas plataformas o revisiones."""
        self._consoles[console.id] = console

    def get_console(self, console_id_or_name: str) -> Optional[ConsoleRecord]:
        """Localiza una consola por ID canónico, nombre oficial o alias."""
        norm = console_id_or_name.strip().lower()
        if norm in self._consoles:
            return self._consoles[norm]

        for c in self._consoles.values():
            if norm == c.name.lower() or norm == c.short_name.lower() or norm in [a.lower() for a in c.aliases]:
                return c
        return None

    def get_consoles_by_manufacturer(self, manufacturer: str) -> List[ConsoleRecord]:
        """Retorna consolas filtradas por fabricante."""
        return [c for c in self._consoles.values() if c.manufacturer.lower() == manufacturer.lower()]

    def get_home_consoles_current_and_previous(self, manufacturer: str) -> List[ConsoleRecord]:
        """
        Retorna las consolas de sobremesa correspondientes a la generación actual
        y las cuatro generaciones anteriores para un fabricante dado.
        """
        consoles = [
            c for c in self._consoles.values()
            if c.manufacturer.lower() == manufacturer.lower()
            and c.line in (PlatformLine.HOME_CONSOLE.value, PlatformLine.HYBRID_CONSOLE.value)
            and not c.is_retro_handheld_catalogue
        ]
        # Ordenar por generación decreciente
        consoles.sort(key=lambda x: x.generation_number, reverse=True)
        return consoles

    def get_retro_and_handheld_catalogue(self, manufacturer: Optional[str] = None) -> List[ConsoleRecord]:
        """Retorna el catálogo independiente de portátiles y consolas retro."""
        consoles = [c for c in self._consoles.values() if c.is_retro_handheld_catalogue]
        if manufacturer:
            consoles = [c for c in consoles if c.manufacturer.lower() == manufacturer.lower()]
        consoles.sort(key=lambda x: (x.manufacturer, -x.generation_number))
        return consoles

    def resolve_backward_compatibility(
        self,
        game_title: str,
        original_platform_id: str,
        played_on_platform_id: str
    ) -> Dict[str, Any]:
        """
        Resuelve si una instancia de juego es nativa o retrocompatible.
        Regla de oro: No contabilizar una versión retrocompatible como un juego diferente.
        """
        orig = self.get_console(original_platform_id)
        played = self.get_console(played_on_platform_id)

        if not orig or not played:
            return {
                "is_native": True,
                "is_backward_compatible": False,
                "canonical_platform": original_platform_id
            }

        if orig.id == played.id:
            return {
                "is_native": True,
                "is_backward_compatible": False,
                "canonical_platform": orig.name
            }

        # Comprobar si 'played' soporta retrocompatibilidad con 'orig'
        compat_info = played.backward_compatibility_info
        compat_plats = compat_info.get("compatible_platforms", [])
        is_compat = any(p.lower() in orig.name.lower() or orig.name.lower() in p.lower() for p in compat_plats)

        return {
            "is_native": not is_compat,
            "is_backward_compatible": is_compat,
            "canonical_platform": orig.name,
            "host_platform": played.name,
            "note": f"'{game_title}' es un título nativo de {orig.name} ejecutado vía retrocompatibilidad en {played.name}." if is_compat else f"Versión nativa o relanzamiento específico para {played.name}."
        }


# Instancia singleton del inventario
CONSOLE_INVENTORY = ConsoleInventoryEngine()
