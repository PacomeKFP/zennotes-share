"""Smoke live de zennotes-share. Env requises : SHARE_URL, SHARE_ADMIN_TOKEN."""

import json
import os
import sys
import urllib.request
import urllib.error

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = os.environ["SHARE_URL"].rstrip("/")
ADMIN = os.environ["SHARE_ADMIN_TOKEN"]


def call(method, path, payload=None, admin=False):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    if admin:
        req.add_header("Authorization", "Bearer " + ADMIN)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="ignore")[:200]


H = True


def check(name, cond):
    global H
    print(("PASS " if cond else "FAIL ") + name)
    H = H and cond


s, _ = call("POST", "/api/links", {"path": "Bienvenue.md", "ttl_hours": 1}, admin=False)
check("admin requise", s == 401)
s, b = call("POST", "/api/links", {"path": "Bienvenue.md", "ttl_hours": 1, "max_views": 1}, admin=True)
check("creation", s == 200)
info = json.loads(b)
tok = info["token"]
check("url formee", info["url"].endswith("/s/" + tok))
s, b = call("GET", "/api/links", admin=True)
check("liste", s == 200 and tok in b)
s, b = call("GET", f"/s/{tok}")
check("page 200 + contenu", s == 200 and "Bienvenue" in b and "<script" not in b)
s, _ = call("GET", f"/s/{tok}")
check("quota max_views=1", s == 404)
s, _ = call("DELETE", f"/api/links/{tok}", admin=True)
check("revocation", s == 200)
s, b = call("POST", "/api/links", {"path": "Bienvenue.md", "ttl_hours": 1, "password": "pw"}, admin=True)
tok2 = json.loads(b)["token"]
s, b = call("GET", f"/s/{tok2}")
check("mot de passe protege", s == 401 and "protegee" in b)
s, _ = call("GET", f"/s/{tok2}?p=pw")
check("mot de passe ok", s == 200)
s, b = call("DELETE", f"/api/links/{tok2}", admin=True)
s, b = call("GET", "/")
check("admin UI", s == 200 and "ZenNotes Share" in b)

print("SMOKE_" + ("OK" if H else "KO"))
sys.exit(0 if H else 1)
