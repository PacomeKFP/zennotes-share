"""Logique pure des liens ephemeres (sans Modal, sans FastAPI, testable)."""

from __future__ import annotations

import hashlib
import secrets
import time

TOKEN_BYTES = 24
MIN_TTL_HOURS = 1
MAX_TTL_HOURS = 720
DEFAULT_TTL_HOURS = 24


def new_token() -> str:
    return secrets.token_urlsafe(TOKEN_BYTES)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def normalize_path(raw: str) -> str:
    """Nettoie un chemin vault et refuse les echappements. Leve ValueError."""
    if not raw or not raw.strip():
        raise ValueError("path requis")
    path = raw.strip().replace("\\", "/")
    while path.startswith("/"):
        path = path[1:]
    parts = [p for p in path.split("/") if p not in ("", ".")]
    if not parts or any(p == ".." for p in parts):
        raise ValueError("path invalide (echappement refuse)")
    return "/".join(parts)


def create_link(
    store: dict,
    path: str,
    title: str = "",
    ttl_hours: int = DEFAULT_TTL_HOURS,
    max_views: int | None = None,
    password: str | None = None,
    now: float | None = None,
) -> dict:
    if not isinstance(ttl_hours, int) or isinstance(ttl_hours, bool):
        raise ValueError("ttl_hours doit etre un entier")
    if not (MIN_TTL_HOURS <= ttl_hours <= MAX_TTL_HOURS):
        raise ValueError(f"ttl_hours entre {MIN_TTL_HOURS} et {MAX_TTL_HOURS}")
    if max_views is not None and (not isinstance(max_views, int) or max_views < 1):
        raise ValueError("max_views doit etre un entier >= 1")
    clean = normalize_path(path)
    ts = now if now is not None else time.time()
    token = new_token()
    while token in store:
        token = new_token()
    entry = {
        "path": clean,
        "title": title or clean.rsplit("/", 1)[-1],
        "created_at": ts,
        "expires_at": ts + ttl_hours * 3600,
        "max_views": max_views,
        "views": 0,
        "password_sha256": hash_password(password) if password else None,
    }
    store[token] = entry
    return {"token": token, **entry}


def get_link(store: dict, token: str) -> dict | None:
    return store.get(token)


def check_link(entry: dict, password: str | None = None, now: float | None = None) -> tuple[bool, str]:
    """Retourne (ok, motif). Motifs: ok, expired, exhausted, locked."""
    ts = now if now is not None else time.time()
    if ts >= entry["expires_at"]:
        return False, "expired"
    if entry["max_views"] is not None and entry["views"] >= entry["max_views"]:
        return False, "exhausted"
    if entry["password_sha256"] and hash_password(password or "") != entry["password_sha256"]:
        return False, "locked"
    return True, "ok"


def record_view(store: dict, token: str) -> None:
    entry = store.get(token)
    if entry is not None:
        entry["views"] = entry.get("views", 0) + 1
        store[token] = entry


def revoke(store: dict, token: str) -> bool:
    return store.pop(token, None) is not None


def list_links(store: dict) -> list[dict]:
    items = [{"token": tok, **e} for tok, e in store.items()]
    items.sort(key=lambda e: e["created_at"], reverse=True)
    return items


def public_info(entry: dict, token: str) -> dict:
    return {
        "token": token,
        "path": entry["path"],
        "title": entry["title"],
        "created_at": entry["created_at"],
        "expires_at": entry["expires_at"],
        "views": entry["views"],
        "max_views": entry["max_views"],
        "has_password": entry["password_sha256"] is not None,
    }
