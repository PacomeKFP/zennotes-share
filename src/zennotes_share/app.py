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
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ZenNotes Share</title>
<style>
:root{--bg:#f6f4ef;--card:#fff;--ink:#2b2b2b;--muted:#8a8578;--accent:#4f6df5;
--accent-d:#3d56c4;--line:#e8e2d5;--danger:#c0392b}
*{box-sizing:border-box}
body{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:var(--bg);
color:var(--ink);margin:0}
header{background:#22201b;color:#f6f4ef;padding:.9rem 1.5rem;display:flex;gap:.7rem;align-items:center}
header .dot{width:.7rem;height:.7rem;border-radius:50%;background:var(--accent)}
header small{color:#b9b2a2;margin-left:auto}
main{max-width:72rem;margin:1.5rem auto;padding:0 1rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:.8rem;
padding:1.2rem 1.4rem;margin-bottom:1.2rem;box-shadow:0 1px 3px rgba(0,0,0,.05)}
h2{margin:.2rem 0 1rem;font-size:1.05rem}
.layout{display:grid;grid-template-columns:minmax(16rem,22rem) 1fr;gap:1.2rem;align-items:start}
@media(max-width:800px){.layout{grid-template-columns:1fr}}
input{font-size:.95rem;padding:.5rem .6rem;border:1px solid var(--line);
border-radius:.5rem;width:100%}
input:focus{outline:2px solid var(--accent);border-color:var(--accent)}
button{font-size:.95rem;padding:.5rem 1rem;border:0;border-radius:.5rem;cursor:pointer;
background:var(--accent);color:#fff}
button:hover{background:var(--accent-d)}
button.ghost{background:#efece3;color:var(--ink)}
button.danger{background:#fff;color:var(--danger);border:1px solid var(--danger);padding:.3rem .7rem}
button.danger:hover{background:var(--danger);color:#fff}
.row{display:flex;gap:.6rem;flex-wrap:wrap;margin-top:.7rem}
.row>*{flex:1 1 8rem}
#notelist{max-height:26rem;overflow:auto;border:1px solid var(--line);border-radius:.5rem;margin-top:.6rem}
.note{padding:.55rem .7rem;border-bottom:1px solid var(--line);cursor:pointer}
.note:hover{background:#f0ede4}
.note.sel{background:#e4ebff;border-left:3px solid var(--accent)}
.note .t{font-weight:600;font-size:.92rem;word-break:break-word}
.note .p{color:var(--muted);font-size:.78rem;word-break:break-all}
table{width:100%;border-collapse:collapse;font-size:.9rem}
td,th{border-bottom:1px solid var(--line);padding:.55rem .4rem;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:600}
a{color:var(--accent)}
.badge{display:inline-block;font-size:.75rem;background:#efece3;border-radius:1rem;padding:.1rem .6rem}
#toast{position:fixed;bottom:1.2rem;left:50%;transform:translateX(-50%);background:#22201b;
color:#fff;padding:.6rem 1.2rem;border-radius:.6rem;display:none}
#login{max-width:24rem;margin:6rem auto}
.muted{color:var(--muted);font-size:.85rem}
</style></head>
<body><header><span class="dot"></span><strong>ZenNotes Share</strong>
<small>liens de partage ephemeres</small></header>
<main>
<div class="card" id="login"><h2>Connexion</h2>
<p class="muted">Saisis ta cle admin (conservee dans cet onglet uniquement).</p>
<div class="row"><input type="password" id="key" placeholder="Cle admin">
<button onclick="save()">Ouvrir</button></div></div>
<div id="app" style="display:none">
<div class="layout">
<div class="card"><h2>Notes du vault</h2>
<input id="q" placeholder="Filtrer..." oninput="filterNotes()">
<div id="notelist"><p class="muted">Chargement...</p></div></div>
<div>
<div class="card"><h2>Nouveau lien</h2>
<label class="muted">Note selectionnee</label>
<input id="f_path" placeholder="Clique une note a gauche, ou saisis un chemin">
<div class="row">
<div><label class="muted">Duree (heures)</label><input id="f_ttl" value="24"></div>
<div><label class="muted">Vues max (vide = infini)</label><input id="f_views" placeholder="infini"></div>
<div><label class="muted">Mot de passe (optionnel)</label><input id="f_pw" placeholder="aucun"></div>
</div>
<div class="row"><button onclick="create()">Creer le lien</button>
<button class="ghost" onclick="refresh()">Actualiser</button></div>
<p id="out"></p></div>
<div class="card"><h2>Liens actifs</h2>
<table><thead><tr><th>Note</th><th>Expire</th><th>Vues</th><th></th></tr></thead>
<tbody id="rows"></tbody></table></div>
</div></div>
</div><div id="toast"></div>
<script>
let NOTES=[];
function auth(){return {Authorization:"Bearer "+sessionStorage.getItem("sk")};}
function toast(m){const t=document.getElementById("toast");t.textContent=m;t.style.display="block";
setTimeout(()=>t.style.display="none",2200);}
function save(){const k=document.getElementById("key").value;if(!k)return;
sessionStorage.setItem("sk",k);document.getElementById("login").style.display="none";
document.getElementById("app").style.display="block";loadNotes();refresh();}
async function loadNotes(){
const r=await fetch("/api/notes",{headers:auth()});
if(!r.ok){document.getElementById("notelist").innerHTML="<p class='muted'>Cle invalide.</p>";return;}
NOTES=await r.json();renderNotes("");}
function renderNotes(f){
const box=document.getElementById("notelist");box.innerHTML="";f=f.toLowerCase();
let n=0;for(const x of NOTES){
if(f&&x.path.toLowerCase().indexOf(f)<0&&x.title.toLowerCase().indexOf(f)<0)continue;
n++;const d=document.createElement("div");d.className="note";
const t=document.createElement("div");t.className="t";t.textContent=x.title;
const p=document.createElement("div");p.className="p";p.textContent=x.path;
d.appendChild(t);d.appendChild(p);
d.onclick=(()=>{const path=x.path,el=d;return()=>{document.getElementById("f_path").value=path;
document.querySelectorAll(".note").forEach(e=>e.classList.remove("sel"));el.classList.add("sel");};})();
box.appendChild(d);}
if(!n)box.innerHTML="<p class='muted'>Aucune note.</p>";}
function filterNotes(){renderNotes(document.getElementById("q").value);}
async function create(){
const body={path:document.getElementById("f_path").value,
ttl_hours:parseInt(document.getElementById("f_ttl").value||"24",10)};
const v=document.getElementById("f_views").value;if(v)body.max_views=parseInt(v,10);
const p=document.getElementById("f_pw").value;if(p)body.password=p;
const r=await fetch("/api/links",{method:"POST",headers:Object.assign(
{"Content-Type":"application/json"},auth()),body:JSON.stringify(body)});
const j=await r.json();const o=document.getElementById("out");o.innerHTML="";
if(r.ok){const a=document.createElement("a");a.href=j.url;a.target="_blank";a.textContent=j.url;
o.appendChild(document.createTextNode("Lien : "));o.appendChild(a);o.appendChild(document.createTextNode(" "));
const b=document.createElement("button");b.className="ghost";b.textContent="Copier";
b.onclick=()=>{navigator.clipboard.writeText(j.url);toast("Copie !");};o.appendChild(b);}
else o.textContent="Erreur : "+(j.detail||r.status);
refresh();}
async function refresh(){
const r=await fetch("/api/links",{headers:auth()});
const tb=document.getElementById("rows");tb.innerHTML="";
if(!r.ok){tb.innerHTML="<tr><td>Cle invalide</td></tr>";return;}
for(const l of await r.json()){const tr=document.createElement("tr");
const u=location.origin+"/s/"+l.token;
const c0=document.createElement("td");const a=document.createElement("a");
a.href=u;a.target="_blank";a.textContent=l.title;c0.appendChild(a);
const badge=document.createElement("span");badge.className="badge";
badge.textContent=" "+l.views+(l.max_views?"/"+l.max_views:"/inf");c0.appendChild(badge);
const c1=document.createElement("td");
c1.textContent=new Date(l.expires_at*1000).toLocaleString();
const c2=document.createElement("td");
const cp=document.createElement("button");cp.className="ghost";cp.textContent="Copier";
cp.onclick=(()=>{const x=u;return()=>{navigator.clipboard.writeText(x);toast("Copie !");};})();
const rv=document.createElement("button");rv.className="danger";rv.textContent="Revoquer";
rv.onclick=(()=>{const t=l.token;return async()=>{await fetch("/api/links/"+t,{method:"DELETE",headers:auth()});refresh();};})();
c2.appendChild(cp);c2.appendChild(document.createTextNode(" "));c2.appendChild(rv);
tr.appendChild(c0);tr.appendChild(c1);tr.appendChild(c2);tb.appendChild(tr);}}
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

    @app.get("/api/notes")
    def api_notes(authorization: str | None = Header(default=None)):
        _require_admin(authorization, admin_token)
        out = []
        for dirpath, dirnames, filenames in os.walk(vault_root):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for fn in sorted(filenames):
                if not fn.lower().endswith(".md"):
                    continue
                abs_path = os.path.join(dirpath, fn)
                rel = os.path.relpath(abs_path, vault_root).replace(os.sep, "/")
                try:
                    st = os.stat(abs_path)
                except OSError:
                    continue
                out.append({
                    "path": rel,
                    "title": fn[:-3],
                    "folder": rel.split("/", 1)[0] if "/" in rel else "",
                    "size": st.st_size,
                    "updated_at": st.st_mtime,
                })
        out.sort(key=lambda n: n["path"].lower())
        return out

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
