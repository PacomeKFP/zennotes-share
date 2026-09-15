"""Application FastAPI du sidecar de partage (sans import Modal)."""

from __future__ import annotations

import mimetypes
import os

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from .links import (
    DEFAULT_TTL_HOURS,
    check_link,
    create_link,
    get_link,
    list_links,
    normalize_path,
    public_info,
    record_view,
    revoke,
)
from .render import render_markdown

NOT_FOUND_HTML = """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="robots" content="noindex, nofollow"><title>Lien indisponible</title>
<style>body{font-family:system-ui,sans-serif;max-width:40rem;margin:4rem auto;padding:0 1rem;color:#333}</style>
</head><body><h1>Lien indisponible</h1>
<p>Ce lien est invalide, expire ou a ete revoque.</p></body></html>"""

PASSWORD_HTML = """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="robots" content="noindex, nofollow"><title>Note protegee</title>
<style>body{font-family:system-ui,sans-serif;max-width:40rem;margin:4rem auto;padding:0 1rem;color:#333}
input,button{font-size:1rem;padding:.5rem}</style></head>
<body><h1>Note protegee</h1>
<form method="get"><input type="password" name="p" placeholder="Mot de passe" autofocus>
<button type="submit">Ouvrir</button></form></body></html>"""

PAGE_HTML = """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="robots" content="noindex, nofollow"><title>{title}</title>
<style>body{{font-family:system-ui,sans-serif;max-width:46rem;margin:2rem auto;padding:0 1rem;color:#222;line-height:1.6}}
img{{max-width:100%}}pre{{background:#f4f4f4;padding:1rem;overflow:auto}}
code{{background:#f4f4f4}}table{{border-collapse:collapse}}td,th{{border:1px solid #ccc;padding:.4rem .8rem}}
footer{{margin-top:3rem;color:#888;font-size:.85rem}}</style></head>
<body><article>{content}</article>
<footer>Lien de partage ephemere. Ne pas indexer.</footer></body></html>"""

ADMIN_HTML = """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>ZenNotes Share (admin)</title>
<style>body{font-family:system-ui,sans-serif;max-width:52rem;margin:2rem auto;padding:0 1rem}
input,button{font-size:1rem;padding:.4rem;margin:.2rem}table{border-collapse:collapse;width:100%}
td,th{border:1px solid #ccc;padding:.4rem .6rem;font-size:.9rem}#app{display:none}a{word-break:break-all}</style>
</head><body><h1>ZenNotes Share</h1>
<div id="login"><input type="password" id="key" placeholder="Cle admin">
<button onclick="save()">Ouvrir</button></div>
<div id="app">
<h2>Nouveau lien</h2>
<input id="f_path" size="40" placeholder="quick/ma-note.md">
<input id="f_ttl" size="8" placeholder="24 (heures)">
<input id="f_views" size="10" placeholder="vues max (vide = infini)">
<input id="f_pw" size="14" placeholder="mot de passe (optionnel)">
<button onclick="create()">Creer</button>
<p id="out"></p>
<h2>Liens actifs</h2>
<button onclick="refresh()">Actualiser</button>
<table><thead><tr><th>Note</th><th>Expire</th><th>Vues</th><th></th></tr></thead>
<tbody id="rows"></tbody></table>
</div>
<script>
function auth(){return {Authorization:"Bearer "+sessionStorage.getItem("sk")};}
function save(){sessionStorage.setItem("sk",document.getElementById("key").value);
document.getElementById("login").style.display="none";
document.getElementById("app").style.display="block";refresh();}
async function create(){
const body={path:document.getElementById("f_path").value,
ttl_hours:parseInt(document.getElementById("f_ttl").value||"24",10)};
const v=document.getElementById("f_views").value;if(v)body.max_views=parseInt(v,10);
const p=document.getElementById("f_pw").value;if(p)body.password=p;
const r=await fetch("/api/links",{method:"POST",headers:Object.assign(
{"Content-Type":"application/json"},auth()),body:JSON.stringify(body)});
const j=await r.json();
document.getElementById("out").innerHTML=r.ok?("Lien : <a href='"+j.url+"'>"+j.url+"</a>"):"Erreur : "+(j.detail||r.status);
refresh();}
async function refresh(){
const r=await fetch("/api/links",{headers:auth()});
if(!r.ok){document.getElementById("rows").innerHTML="<tr><td>Cle invalide</td></tr>";return;}
const j=await r.json();const tb=document.getElementById("rows");tb.innerHTML="";
for(const l of j){const tr=document.createElement("tr");
tr.innerHTML="<td><a href='/s/"+l.token+"'>"+l.title+"</a></td><td>"+new Date(
l.expires_at*1000).toLocaleString()+"</td><td>"+l.views+(l.max_views?"/"+l.max_views:"")+"</td>";
const td=document.createElement("td");const b=document.createElement("button");
b.textContent="Revoquer";b.onclick=((t)=>()=>revoke(t))(l.token);td.appendChild(b);
tr.appendChild(td);tb.appendChild(tr);}}
async function revoke(t){await fetch("/api/links/"+t,{method:"DELETE",headers:auth()});refresh();}
</script></body></html>"""


def _require_admin(authorization: str | None, admin_token: str) -> None:
    if not admin_token or authorization != f"Bearer {admin_token}":
        raise HTTPException(status_code=401, detail="cle admin invalide")


def _confined_abs(vault_root: str, rel: str) -> str:
    abs_path = os.path.realpath(os.path.join(vault_root, rel))
    root = os.path.realpath(vault_root)
    if abs_path != root and not abs_path.startswith(root + os.sep):
        raise HTTPException(status_code=400, detail="chemin hors vault")
    return abs_path


def create_app(store, vault_root: str, admin_token: str, public_base: str = ""):
    app = FastAPI(title="zennotes-share", docs_url=None, redoc_url=None)

    def _url(token: str) -> str:
        return f"{public_base.rstrip('/')}/s/{token}" if public_base else f"/s/{token}"

    @app.get("/", response_class=HTMLResponse)
    def admin_home():
        return ADMIN_HTML

    @app.post("/api/links")
    def api_create(payload: dict, authorization: str | None = Header(default=None)):
        _require_admin(authorization, admin_token)
        try:
            rel = normalize_path(str(payload.get("path", "")))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        abs_path = _confined_abs(vault_root, rel)
        if not os.path.isfile(abs_path) or not rel.lower().endswith(".md"):
            raise HTTPException(status_code=404, detail="note introuvable (fichier .md)")
        try:
            created = create_link(
                store,
                rel,
                title=str(payload.get("title", "")),
                ttl_hours=payload.get("ttl_hours", DEFAULT_TTL_HOURS),
                max_views=payload.get("max_views"),
                password=payload.get("password"),
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return {"url": _url(created["token"]), **public_info(created, created["token"])}

    @app.get("/api/links")
    def api_list(authorization: str | None = Header(default=None)):
        _require_admin(authorization, admin_token)
        return [public_info(e, e["token"]) for e in list_links(store)]

    @app.delete("/api/links/{token}")
    def api_revoke(token: str, authorization: str | None = Header(default=None)):
        _require_admin(authorization, admin_token)
        revoke(store, token)
        return {"ok": True}

    def _load(token: str, password: str | None):
        entry = get_link(store, token)
        if entry is None:
            return None, None
        ok, _ = check_link(entry, password=password)
        if not ok:
            return entry, None
        abs_path = _confined_abs(vault_root, entry["path"])
        if not os.path.isfile(abs_path):
            return entry, None
        return entry, abs_path

    @app.get("/s/{token}", response_class=HTMLResponse)
    def public_page(token: str, p: str | None = Query(default=None)):
        entry, abs_path = _load(token, p)
        if entry is None:
            return HTMLResponse(NOT_FOUND_HTML, status_code=404)
        if abs_path is None:
            _, reason = check_link(entry, password=p)
            if reason == "locked":
                return HTMLResponse(PASSWORD_HTML, status_code=401)
            return HTMLResponse(NOT_FOUND_HTML, status_code=404)
        with open(abs_path, encoding="utf-8") as f:
            raw = f.read()
        html = render_markdown(raw, vault_root)
        record_view(store, token)
        page = PAGE_HTML.format(title=entry["title"], content=html)
        return HTMLResponse(page, headers={"X-Robots-Tag": "noindex, nofollow", "Cache-Control": "no-store"})

    @app.get("/s/{token}/a/{asset:path}")
    def public_asset(token: str, asset: str, p: str | None = Query(default=None)):
        entry = get_link(store, token)
        if entry is None:
            raise HTTPException(status_code=404)
        ok, reason = check_link(entry, password=p)
        if not ok:
            raise HTTPException(status_code=404 if reason != "locked" else 401)
        try:
            rel = normalize_path(asset)
        except ValueError:
            raise HTTPException(status_code=400)
        abs_path = _confined_abs(vault_root, rel)
        if not os.path.isfile(abs_path):
            raise HTTPException(status_code=404)
        media, _ = mimetypes.guess_type(abs_path)
        return FileResponse(
            abs_path,
            media_type=media or "application/octet-stream",
            headers={"X-Robots-Tag": "noindex, nofollow", "Cache-Control": "no-store"},
        )

    return app
