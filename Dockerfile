# ==============================================================================
# SamuBusquedas v3.0 (.onion v3) — Contenedor Docker para Despliegue en la Nube
# Arquitecto y Creador: saghet
# Compatible con: Hugging Face Spaces (Docker SDK), Render.com, Koyeb, OCI
# ==============================================================================
FROM python:3.11-slim-bookworm

# Evitar prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Instalar Tor oficial y utilidades mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    tor \
    ca-certificates \
    procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar código fuente de SamuBusquedas
COPY app/ /app/app/
COPY config/torrc.cloud.conf /etc/tor/torrc
COPY deploy/entrypoint.sh /app/entrypoint.sh

# Crear directorios y preparar permisos estrictos para Tor (usuario debian-tor)
RUN mkdir -p /var/lib/tor/samubusquedas_hs && \
    mkdir -p /var/lib/tor/data && \
    chmod 700 /var/lib/tor/samubusquedas_hs && \
    chmod 700 /var/lib/tor/data && \
    chown -R debian-tor:debian-tor /var/lib/tor

# Copiar las claves criptográficas para mantener la dirección .onion oficial de saghet
COPY .tor_runtime/samubusquedas_hs/ /var/lib/tor/samubusquedas_hs/
RUN sed -i 's/\r$//' /app/entrypoint.sh /etc/tor/torrc && \
    chmod 700 /var/lib/tor/samubusquedas_hs && \
    chmod 600 /var/lib/tor/samubusquedas_hs/* && \
    chown -R debian-tor:debian-tor /var/lib/tor/samubusquedas_hs && \
    chmod +x /app/entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/app/entrypoint.sh"]
