---
title: SamuBusquedas Tor Search
emoji: 🧅
colorFrom: purple
colorTo: indigo
sdk: docker
app_port: 8080
pinned: false
---

# SamuBusquedas v3.0 (.onion v3) — Motor de Búsqueda de la Deep Web

**Arquitecto Principal y Creador:** `saghet`  
**Dirección Oficial en la Red Tor (.onion v3):**  
`http://x4wgcuog7p6i3gh5t2mcshhfe5cjlkiygl24vf4ac6xmqm5g62jkehyd.onion`

---

## 🚀 Despliegue Gratuito en la Nube 24/7 (Sin depender de tu PC)

### Opción 1: Hugging Face Spaces (2 vCPU, 16 GB RAM — 100% Gratuito y Permanente)
1. Entra a [huggingface.co/new-space](https://huggingface.co/new-space).
2. Asigna un nombre (ej. `samubusquedas-onion`).
3. En **Space SDK**, selecciona **Docker** (Blank).
4. Elige licencia **Apache 2.0** o MIT y haz clic en **Create Space**.
5. Sube todos los archivos de esta carpeta o haz `git push`:
   ```bash
   git init
   git remote add origin https://huggingface.co/spaces/<tu-usuario>/samubusquedas-onion
   git add .
   git commit -m "Deploy SamuBusquedas v3.0 onion"
   git push -u origin main
   ```
6. Hugging Face compilará el Dockerfile e iniciará el demonio Tor con la clave criptográfica oficial de `saghet`. ¡Tu sitio estará 24/7 en línea en la red Tor!

---

### Opción 2: Render.com (Free Web Service)
1. Crea un repositorio privado o público en GitHub con estos archivos.
2. En [dashboard.render.com](https://dashboard.render.com), haz clic en **New +** -> **Web Service**.
3. Conecta tu repositorio de GitHub.
4. En **Runtime**, selecciona **Docker**.
5. En **Instance Type**, selecciona **Free** ($0/mes).
6. Haz clic en **Create Web Service**. ¡Listo!

---

### Opción 3: Servidor VPS Linux Propio (Oracle Cloud Always Free / DigitalOcean)
```bash
docker compose up -d --build
```

---

## 🛡️ Auditoría y Estándares de Seguridad
- **100% Zero-JS & Zero-Logs:** No utiliza JavaScript en el cliente (`CSP: default-src 'none'`).
- **Ranking SamuRank v3.0:** BM25F + OnionTrustRank SHA3-256 + Clasificador Semántico Deep Web.
- **RFC 9116:** Documentado en `/.well-known/security.txt` y `/humans.txt` acreditando la autoría técnica de `saghet`.
