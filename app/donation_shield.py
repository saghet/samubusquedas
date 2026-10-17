"""
SamuBusquedas — Sistema de Sostenibilidad Bitcoin & Muro Agresivo de 15 Segundos (v1.99.5)
==========================================================================================
Arquitecto Principal: saghet

Características:
1. Dirección Oficial BTC (Red Bitcoin P2PKH): `13CCAjcHanNyKNcR3eFSh2PEu9tBzpXq3d`
2. Código QR Oficial servido localmente en `/static/btc_qr.png` (100% Zero-JS / CSP `'self'`).
3. Widget Fijo de Donación en la Esquina Izquierda en todas las páginas del buscador.
4. Plan de Solicitud Agresiva (Spam Gate de 15 Segundos) cuando un usuario supera las 10 búsquedas:
   - Búsquedas 1 a 10: Acceso directo e instantáneo (0 segundos de espera).
   - A partir de la búsqueda #11 (`search_count > 10`): Muestra una pantalla intersticial agresiva
     con el código QR de Bitcoin y la dirección `13CCAjcHanNyKNcR3eFSh2PEu9tBzpXq3d` durante
     15 segundos exactos (`<meta http-equiv="refresh" content="15;url=...">` + barra CSS de 15s)
     antes de mostrar los resultados de la búsqueda.
"""

import hashlib
import secrets
import threading
import time
from http.cookies import SimpleCookie
from typing import Dict, Optional, Tuple

_DONATION_LOCK = threading.RLock()

BTC_ADDRESS: str = "13CCAjcHanNyKNcR3eFSh2PEu9tBzpXq3d"
BTC_URI: str = f"bitcoin:{BTC_ADDRESS}"
BTC_QR_PATH: str = "/static/btc_qr.png"
BTC_NETWORK_NOTE: str = (
    'Red BTC (Bitcoin) — Admite depósitos desde todas las direcciones de BTC (que comienzan con "1", "3", "bc1p" y "bc1q").'
)

FREE_SEARCH_LIMIT: int = 10
DONATION_GATE_SECONDS: int = 15
COOKIE_NAME: str = "samu_sid"
SESSION_TTL_SECONDS: int = 43200  # 12 horas en RAM efímera


class DonationGateTracker:
    """
    Rastreador efímero en RAM (Zero-Disk-Logs) del número de búsquedas por sesión/circuito
    para activar el plan agresivo de donación de 15 segundos al superar las 10 búsquedas.
    """

    def __init__(
        self,
        free_limit: int = FREE_SEARCH_LIMIT,
        gate_seconds: int = DONATION_GATE_SECONDS,
    ) -> None:
        self.free_limit = free_limit
        self.gate_seconds = gate_seconds
        self._sessions: Dict[str, Dict[str, float]] = {}
        self.total_gate_impressions: int = 0

    def _cleanup_expired(self, now: float) -> None:
        if len(self._sessions) < 512:
            return
        expired = [
            sid
            for sid, data in self._sessions.items()
            if (now - data.get("updated_at", now)) > SESSION_TTL_SECONDS
        ]
        for sid in expired:
            self._sessions.pop(sid, None)

    def resolve_session_id(
        self,
        headers: Dict[str, str],
        client_ip: str = "127.0.0.1",
    ) -> Tuple[str, bool]:
        """
        Obtiene o genera un identificador efímero de sesión (`samu_sid`).
        Si el navegador no envía cookies (ej. modo estricto o cliente CLI con header),
        deriva una huella efímera en RAM para esa sesión.
        """
        raw_cookie = headers.get("Cookie") or headers.get("cookie") or ""
        if raw_cookie:
            cookie = SimpleCookie()
            try:
                cookie.load(raw_cookie)
                if COOKIE_NAME in cookie:
                    val = cookie[COOKIE_NAME].value.strip()
                    if 12 <= len(val) <= 64 and val.isalnum():
                        return val, False
            except Exception:
                pass

        explicit_sid = (headers.get("X-Samu-Session") or headers.get("x-samu-session") or "").strip()
        if 8 <= len(explicit_sid) <= 64 and explicit_sid.isalnum():
            return explicit_sid, False

        # Fallback por huella efímera o nueva cookie aleatoria
        ua = headers.get("User-Agent") or headers.get("user-agent") or ""
        forwarded = headers.get("X-Forwarded-For") or headers.get("x-forwarded-for") or client_ip
        if ua or forwarded != "127.0.0.1":
            seed = f"samu-v1995|{forwarded}|{ua}".encode("utf-8", errors="ignore")
            derived = hashlib.sha256(seed).hexdigest()[:24]
            return derived, True

        new_sid = secrets.token_hex(12)
        return new_sid, True

    def get_search_count(self, session_id: str) -> int:
        with _DONATION_LOCK:
            entry = self._sessions.get(session_id)
            if not entry:
                return 0
            return int(entry.get("count", 0))

    def register_search_and_evaluate_gate(
        self,
        session_id: str,
        is_real_search: bool,
        dpass_completed: bool,
    ) -> Dict[str, object]:
        """
        Incrementa el contador cuando el usuario lanza una búsqueda nueva (`is_real_search=True`
        y `dpass_completed=False`).
        Si `count > self.free_limit` (más de 10 búsquedas) y aún no ha pasado por los 15 segundos
        de espera (`dpass_completed=False`), devuelve `should_gate=True`.
        """
        now = time.time()
        with _DONATION_LOCK:
            self._cleanup_expired(now)
            entry = self._sessions.get(session_id)
            if not entry:
                entry = {"count": 0.0, "updated_at": now}
                self._sessions[session_id] = entry

            entry["updated_at"] = now
            if is_real_search and not dpass_completed:
                entry["count"] = float(int(entry.get("count", 0)) + 1)

            current_count = int(entry.get("count", 0))
            over_limit = current_count > self.free_limit
            should_gate = bool(is_real_search and over_limit and not dpass_completed)
            if should_gate:
                self.total_gate_impressions += 1

            return {
                "session_id": session_id,
                "search_count": current_count,
                "free_limit": self.free_limit,
                "remaining_free": max(0, self.free_limit - current_count),
                "over_limit": over_limit,
                "should_gate": should_gate,
                "gate_seconds": self.gate_seconds,
                "btc_address": BTC_ADDRESS,
            }

    def reset_session(self, session_id: Optional[str] = None) -> None:
        with _DONATION_LOCK:
            if session_id:
                self._sessions.pop(session_id, None)
            else:
                self._sessions.clear()

    def get_stats(self) -> Dict[str, object]:
        with _DONATION_LOCK:
            return {
                "btc_address": BTC_ADDRESS,
                "free_search_limit": self.free_limit,
                "gate_wait_seconds": self.gate_seconds,
                "active_ephemeral_sessions": len(self._sessions),
                "total_gate_impressions": self.total_gate_impressions,
            }


DONATION_TRACKER = DonationGateTracker()
