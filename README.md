# GAMER SEARCH ENGINE
## Motor de Búsqueda Inteligente de Videojuegos, Trucos, Preservación y Comunidades Gamer

Plataforma de búsqueda especializada capaz de encontrar información en múltiples fuentes abiertas y profundas, analizarla mediante inteligencia artificial semántica, clasificarla y presentarla organizada en una interfaz gamer moderna con tema oscuro.

---

## 🎮 Ecosistemas Prioritarios y Cobertura
- **Nintendo**: Nintendo Switch (OLED/Lite), Wii U, Wii, GameCube, Nintendo 64, SNES, NES, Game Boy, GBA, Nintendo DS, 3DS.
- **PlayStation**: PlayStation 5, PlayStation 4, PlayStation 3, PlayStation 2, PlayStation 1, PSP, PS Vita.
- **Xbox**: Xbox Series X, Xbox Series S, Xbox One, Xbox 360, Xbox Original.
- **Retro & Arcade**: Sega (Genesis / Dreamcast), Atari (2600), Coin-Op Arcade y proyectos de dominio público.

---

## 🧩 9 Secciones Especializadas
1. **Videojuegos (`/juegos`)**: Fichas técnicas completas con plataformas, fechas de lanzamiento, desarrolladores, géneros, ediciones, DLCs, parches, compatibilidad, requisitos técnicos y valoraciones.
2. **Trucos & Secretos (`/trucos`)**: Códigos, easter eggs, secretos, glitches conocidos, builds, trofeos de PS5, logros de Xbox y desafíos de Nintendo con fuente original y fecha de verificación.
3. **ROMs Legales & Preservación (`/preservacion`)**: Archivos autorizados de dominio público, videojuegos homebrew, freeware y descompilaciones limpias. Garantía estricta contra malware y piratería.
4. **Emuladores Oficiales (`/emuladores`)**: Emuladores verificados de código abierto (RetroArch, Dolphin, PCSX2, RPCS3, DuckStation, PPSSPP, xemu, Xenia, Mesen, SameBoy, melonDS, Lime3DS, Vita3K, Flycast, Stella).
5. **Mods & Parches (`/mods`)**: Parches de traducción comunitaria (IPS, BPS, UPS), mejoras de rendimiento (60fps, widescreen) y herramientas de modding.
6. **Comunidades Gamer (`/comunidades`) [PRIORITARIO]**: Subreddits activos, servidores oficiales verificados de Discord, foros especializados y tablas de récords de Speedrun.com con recuento de miembros y nivel de actividad real.
7. **Guías & 100% (`/guias`)**: Walkthroughs paso a paso, guías de trofeos de platino y guías de optimización de personajes/builds.
8. **Investigación Avanzada OSINT (`/investigacion`)**: Consultas en tiempo real a APIs de Speedrun.com, Internet Archive y GitHub con evaluación de seguridad.
9. **Favoritos & Historial (`/favoritos`)**: Gestión de partidas guardadas, videojuegos seguidos y registro de consultas en almacenamiento seguro.

---

## 🤖 Inteligencia Artificial Semántica
- **Entendimiento de lenguaje natural**: Identifica automáticamente videojuego, plataforma, tipo de recurso e intención a partir de frases completas.
  - *Ejemplo 1:* `"Quiero encontrar todos los trucos de Zelda Tears of the Kingdom para Nintendo Switch"` $\to$ Enruta a trucos de Switch con fuentes recomendadas (GameFAQs, Reddit).
  - *Ejemplo 2:* `"Quiero encontrar comunidades de jugadores de Elden Ring que compartan builds y secretos"` $\to$ Enruta a comunidades con foco en Discord y Reddit.
- **Desambiguación de acrónimos gamer**: Reconoce automáticamente términos como `totk`, `botw`, `gow`, `sm64`, `fh5`, `ssbu`, `sh2`, etc.
- **Escudo Anti-Malware y Prevención de Amenazas**: Detección de patrones fraudulentos, generadores falsos y ejecutables peligrosos (`.exe`, keygens), emitiendo alertas técnicas preventivas.

---

## 🛠️ Ejecución y Pruebas

### 1. Iniciar el servidor
```bash
python app/main.py
```
El buscador estará disponible en `http://localhost:8080/` (o el puerto configurado).

### 2. Ejecutar la suite completa de pruebas unitarias e integración (38 tests)
```bash
python -m unittest discover -s tests
```
