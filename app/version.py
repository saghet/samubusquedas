"""
SamuBusquedas — Control Centralizado de Versiones SemVer Incremental
====================================================================
Autoría y Arquitectura: saghet

REGLA DE GOBERNANZA DE VERSIONES:
Cada vez que se realice cualquier cambio, mejora o ampliación en SamuBusquedas,
se DEBE incrementar el tercer número de versión de forma consecutiva:
1.99 -> 1.99.1 -> 1.99.2 -> 1.99.3 -> ...
"""

ENGINE_VERSION: str = "1.99.12"
ENGINE_DISPLAY_VERSION: str = f"v{ENGINE_VERSION}"
ENGINE_USER_AGENT: str = f"SamuBusquedas/{ENGINE_VERSION}"
ENGINE_HEADER_NAME: str = f"SamuEngine/{ENGINE_VERSION} (Tor Hidden Service; Architected by saghet)"

