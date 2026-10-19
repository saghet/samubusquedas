"""
SamuBusquedas — Motor de Despliegue Continuo a Render Cloud y Verificación .onion (v1.99.7)
===========================================================================================
Arquitecto Principal: saghet

Garantiza que todos los cambios realizados en el repositorio local se suban siempre a
Render (`https://samubusquedas.onrender.com`) mediante Git (`origin/main`), validando:
1. Integridad del par de llaves Ed25519 para `x4wgcuog7p6i3gh5t2mcshhfe5cjlkiygl24vf4ac6xmqm5g62jkehyd.onion`.
2. Configuración de auto-despliegue en `render.yaml`, `Dockerfile` y `deploy/entrypoint.sh`.
3. Subida automática (`git add -A`, `git commit`, `git push origin main`).
4. Sondeo en vivo a `https://samubusquedas.onrender.com/healthz` hasta confirmar la versión desplegada.
5. Sondeo en vivo vía SOCKS5h (`127.0.0.1:19050`) al dominio oficial `.onion v3`.
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
from typing import Dict, Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.join(REPO_ROOT, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from onion_guardian import OFFICIAL_ONION_HOST, OFFICIAL_ONION_URL, ONION_GUARDIAN  # noqa: E402
from version import ENGINE_VERSION  # noqa: E402

RENDER_PUBLIC_URL = "https://samubusquedas.onrender.com"
RENDER_HEALTHZ_URL = f"{RENDER_PUBLIC_URL}/healthz"


def verify_onion_keypair_and_render_config() -> Dict[str, object]:
    """
    Audita que la identidad criptográfica `.onion v3` y los manifiestos de despliegue en
    Render (`render.yaml`, `Dockerfile`, `deploy/entrypoint.sh`) estén completos y sincronizados.
    """
    hs_dir = os.path.join(REPO_ROOT, ".tor_runtime", "samubusquedas_hs")
    hostname_path = os.path.join(hs_dir, "hostname")
    sec_key_path = os.path.join(hs_dir, "hs_ed25519_secret_key")
    pub_key_path = os.path.join(hs_dir, "hs_ed25519_public_key")
    dockerfile_path = os.path.join(REPO_ROOT, "Dockerfile")
    render_yaml_path = os.path.join(REPO_ROOT, "render.yaml")
    entrypoint_path = os.path.join(REPO_ROOT, "deploy", "entrypoint.sh")

    hostname_val = ""
    if os.path.exists(hostname_path):
        with open(hostname_path, "r", encoding="utf-8") as fh:
            hostname_val = fh.read().strip()

    sec_key_ok = os.path.exists(sec_key_path) and os.path.getsize(sec_key_path) >= 64
    pub_key_ok = os.path.exists(pub_key_path) and os.path.getsize(pub_key_path) >= 32

    dockerfile_text = ""
    if os.path.exists(dockerfile_path):
        with open(dockerfile_path, "r", encoding="utf-8") as fh:
            dockerfile_text = fh.read()

    render_yaml_text = ""
    if os.path.exists(render_yaml_path):
        with open(render_yaml_path, "r", encoding="utf-8") as fh:
            render_yaml_text = fh.read()

    entrypoint_text = ""
    if os.path.exists(entrypoint_path):
        with open(entrypoint_path, "r", encoding="utf-8") as fh:
            entrypoint_text = fh.read()

    torrc_cloud_path = os.path.join(REPO_ROOT, "config", "torrc.cloud.conf")
    torrc_cloud_text = ""
    if os.path.exists(torrc_cloud_path):
        with open(torrc_cloud_path, "r", encoding="utf-8") as fh:
            torrc_cloud_text = fh.read()

    dockerfile_present = os.path.exists(dockerfile_path)
    render_autodeploy = "autoDeploy: true" in render_yaml_text and "healthCheckPath: /healthz" in render_yaml_text
    entrypoint_supervises_tor = "debian-tor" in entrypoint_text and "tor -f /etc/tor/torrc" in entrypoint_text
    cloud_hs_enabled = (
        "HiddenServiceDir /var/lib/tor/samubusquedas_hs" in torrc_cloud_text
        and "HiddenServicePort 80" in torrc_cloud_text
        and "HiddenServicePort 443" in torrc_cloud_text
    )

    all_ok = bool(
        hostname_val == OFFICIAL_ONION_HOST
        and sec_key_ok
        and pub_key_ok
        and dockerfile_present
        and render_autodeploy
        and entrypoint_supervises_tor
        and cloud_hs_enabled
    )

    return {
        "ok": all_ok,
        "version": ENGINE_VERSION,
        "official_onion_url": OFFICIAL_ONION_URL,
        "render_public_url": RENDER_PUBLIC_URL,
        "hostname_matches": hostname_val == OFFICIAL_ONION_HOST,
        "ed25519_secret_key_present": sec_key_ok,
        "ed25519_public_key_present": pub_key_ok,
        "dockerfile_present": dockerfile_present,
        "render_autodeploy_enabled": render_autodeploy,
        "entrypoint_supervises_tor": entrypoint_supervises_tor,
        "cloud_hs_enabled": cloud_hs_enabled,
    }


def git_commit_and_push_all(commit_message: Optional[str] = None) -> Dict[str, object]:
    """
    Empaqueta todos los cambios del árbol de trabajo (`git add -A`), crea el commit incremental
    si existen cambios pendientes y ejecuta `git push origin main` hacia GitHub/Render.
    """
    msg = commit_message or (
        f"feat(v{ENGINE_VERSION}): auto-deploy all changes to Render Cloud + 24/7 OnionAlwaysOnGuardian"
    )
    subprocess.run(["git", "add", "-A"], cwd=REPO_ROOT, check=True)
    status_proc = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    has_changes = bool(status_proc.stdout.strip())
    committed = False
    if has_changes:
        subprocess.run(["git", "commit", "-m", msg], cwd=REPO_ROOT, check=True)
        committed = True

    push_proc = subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    head_proc = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return {
        "committed_new_changes": committed,
        "commit_sha": head_proc.stdout.strip(),
        "push_output": (push_proc.stdout + "\n" + push_proc.stderr).strip(),
    }


def wait_for_render_deployment(
    expected_version: str = ENGINE_VERSION,
    max_wait_seconds: int = 240,
    poll_interval: int = 8,
) -> Dict[str, object]:
    """
    Consulta periódicamente `https://samubusquedas.onrender.com/healthz` hasta confirmar
    que Render Cloud compiló y desplegó la versión `expected_version`.
    """
    deadline = time.time() + max_wait_seconds
    last_payload: Dict[str, object] = {}
    while time.time() < deadline:
        try:
            req = urllib.request.Request(
                RENDER_HEALTHZ_URL,
                headers={"User-Agent": f"SamuRenderDeployVerifier/{expected_version}"},
            )
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    last_payload = data
                    live_ver = str(data.get("version", ""))
                    print(
                        f"  [*] Render /healthz -> versión en vivo: v{live_ver} "
                        f"(esperada: v{expected_version})"
                    )
                    if live_ver == expected_version:
                        return {
                            "deployed": True,
                            "live_version": live_ver,
                            "healthz": data,
                        }
        except Exception as exc:
            print(f"  [!] Esperando a Render ({exc})...")
        time.sleep(poll_interval)

    return {
        "deployed": str(last_payload.get("version", "")) == expected_version,
        "live_version": str(last_payload.get("version", "unknown")),
        "healthz": last_payload,
    }


def main() -> None:
    print("======================================================================")
    print(f"  SAMUBUSQUEDAS v{ENGINE_VERSION} — AUTO-DEPLOY PIPELINE A RENDER + TOR")
    print(f"  URL .ONION V3 : {OFFICIAL_ONION_URL}/")
    print(f"  URL RENDER    : {RENDER_PUBLIC_URL}/")
    print("======================================================================")

    audit = verify_onion_keypair_and_render_config()
    if not audit["ok"]:
        print("[ERROR] Falló la auditoría previa de llaves .onion o configuración de Render:")
        print(json.dumps(audit, indent=2))
        sys.exit(1)
    print("[1/3] Auditoría de llaves Ed25519 (.onion v3) y manifiestos Render: APROBADA")

    git_res = git_commit_and_push_all()
    print(f"[2/3] Git Push completado hacia origin/main (Commit: {git_res['commit_sha']})")

    print("[3/3] Verificando despliegue en vivo en Render Cloud y sonda .onion v3...")
    onion_status = ONION_GUARDIAN.run_self_onion_heartbeat(timeout=10.0)
    print(
        f"  [*] Estado Nodo .onion ({OFFICIAL_ONION_URL}/): "
        f"ok={onion_status['last_self_probe_ok']} ({onion_status['last_self_probe_reason']})"
    )

    render_res = wait_for_render_deployment(expected_version=ENGINE_VERSION, max_wait_seconds=240, poll_interval=10)
    print("======================================================================")
    print(f"  [LISTO] Render Cloud versión en vivo: v{render_res['live_version']}")
    print(f"  [LISTO] URL Deep Web (.onion)       : {OFFICIAL_ONION_URL}/")
    print("======================================================================")


if __name__ == "__main__":
    main()
