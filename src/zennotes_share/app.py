"""Application FastAPI du sidecar de partage (sans import Modal)."""

from __future__ import annotations

import html
import mimetypes
import os
from datetime import datetime

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
from .render import PYGMENTS_CSS, count_h2, reading_time_minutes, render_article

BASE_CSS = """:root{color-scheme:light dark;
--bg:#fbfaf7;--fg:#23211c;--muted:#6f6a5e;--surface:#fff;--border:#e8e2d5;
--link:#3d56c4;--accent:#4f6df5;--focus:#2f4bff;--code-bg:#f1eee6;--danger:#b3261e;--ok:#1a7f37;
--font-read:"Source Serif 4",Georgia,"Bitstream Charter","Times New Roman",serif;
--font-ui:Inter,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
--font-mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
--radius-s:.375rem;--radius-m:.5rem;--radius-l:.8rem;--shadow-sm:0 1px 3px rgba(0,0,0,.06)}
@media(prefers-color-scheme:dark){:root{--bg:#191813;--fg:#ece7db;--muted:#a8a294;
--surface:#23211b;--border:#3a372e;--link:#9db1ff;--accent:#7c93ff;--focus:#aebfff;
--code-bg:#26221c;--danger:#ff8a80;--ok:#7dd88f}}
html[data-theme="light"]{color-scheme:light;--bg:#fbfaf7;--fg:#23211c;--muted:#6f6a5e;
--surface:#fff;--border:#e8e2d5;--link:#3d56c4;--accent:#4f6df5;--focus:#2f4bff;
--code-bg:#f1eee6;--danger:#b3261e;--ok:#1a7f37}
html[data-theme="dark"]{color-scheme:dark;--bg:#191813;--fg:#ece7db;--muted:#a8a294;
--surface:#23211b;--border:#3a372e;--link:#9db1ff;--accent:#7c93ff;--focus:#aebfff;
--code-bg:#26221c;--danger:#ff8a80;--ok:#7dd88f}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--font-ui);
font-size:1rem;line-height:1.5;-webkit-text-size-adjust:100%}
:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
.pub-wrap{max-width:40rem;width:100%;margin:0 auto;padding:1.25rem;overflow-wrap:break-word}
@media(min-width:700px){.pub-wrap{padding:1.5rem}}
.topbar{position:sticky;top:0;z-index:40;background:var(--surface);
border-bottom:1px solid var(--border);font-size:.875rem}
.topbar-in{max-width:40rem;margin:0 auto;padding:.5rem 1.25rem;display:flex;
gap:.6rem;align-items:center}
.brand{display:flex;gap:.45rem;align-items:center;font-weight:700}
.brand .dot{width:.6rem;height:.6rem;border-radius:50%;background:var(--accent)}
.badge{display:inline-block;font-size:.75rem;background:var(--code-bg);
border:1px solid var(--border);border-radius:1rem;padding:.1rem .6rem;color:var(--muted)}
.readtime{margin-left:auto;color:var(--muted);font-size:.8125rem;white-space:nowrap}
.progress{position:fixed;top:0;left:0;right:0;height:3px;z-index:60}
.progress span{display:block;height:100%;width:0;background:var(--accent)}
.hero h1{font-family:var(--font-read);font-weight:600;
font-size:clamp(1.75rem,1.3rem+2.2vw,2.5rem);line-height:1.15;
text-wrap:balance;margin:1.8rem 0 .6rem}
.meta{color:var(--muted);font-size:.875rem;margin:0 0 1rem}
.filet{border:0;border-top:1px solid var(--border);margin:0 0 1.2rem}
details.toc{border:1px solid var(--border);border-radius:var(--radius-m);
background:var(--surface);margin:0 0 1.5rem;box-shadow:var(--shadow-sm)}
details.toc summary{cursor:pointer;padding:.8rem 1rem;font-weight:600;min-height:44px}
details.toc .toc{padding:0 1rem 1rem}
details.toc .toc ul{margin:.2rem 0;padding-left:1.2rem}
details.toc .toc a{color:var(--link);text-decoration:none;line-height:2}
details.toc .toc a:hover{text-decoration:underline}
.pub-article{font-family:var(--font-read);font-size:1.0625rem;line-height:1.6;
max-width:65ch;text-wrap:pretty}
.pub-article p{margin:0 0 1.1em;hyphens:auto}
.pub-article h2,.pub-article h3{font-family:var(--font-read);line-height:1.25;
text-wrap:balance;margin:1.8em 0 .6em}
.pub-article h2{font-size:1.5rem}
.pub-article h3{font-size:1.25rem}
.pub-article h4{font-size:1.1rem;line-height:1.3}
.pub-article a{color:var(--link)}
.pub-article ul,.pub-article ol{padding-left:1.4rem;margin:0 0 1.1em}
.pub-article li{margin:.25em 0}
.pub-article blockquote{border-left:3px solid var(--border);margin:1.2em 0;
padding:.2em 0 .2em 1em;color:var(--muted)}
.pub-article hr{border:0;border-top:1px solid var(--border);margin:2em 0}
.pub-article code{font-family:var(--font-mono);font-size:.88em;
background:var(--code-bg);border-radius:var(--radius-s);padding:.1em .3em}
.pub-article pre{background:var(--code-bg);border:1px solid var(--border);
border-radius:var(--radius-m);padding:1rem;overflow-x:auto;line-height:1.5;
max-width:100%;font-size:.875rem}
.pub-article pre code{background:none;border:0;padding:0;font-size:inherit}
div.highlight{position:relative;max-width:100%}
div.highlight pre{margin:0 0 1.1em}
.codebox{position:relative;max-width:100%}
.copybtn{position:absolute;top:.45rem;right:.45rem;min-height:44px;min-width:44px;
font-size:.8125rem;padding:.45rem .7rem;border-radius:var(--radius-s);
border:1px solid var(--border);background:var(--surface);color:var(--fg);cursor:pointer}
.copybtn:hover{border-color:var(--accent)}
.table-scroll{overflow-x:auto;max-width:100%;border:1px solid var(--border);
border-radius:var(--radius-m);background:var(--surface);margin:0 0 1.2em}
.table-scroll table{border-collapse:collapse;width:100%;font-size:.9rem;
font-family:var(--font-ui);line-height:1.5}
.table-scroll th,.table-scroll td{border-bottom:1px solid var(--border);
padding:.5rem .8rem;text-align:left;vertical-align:top}
.table-scroll thead th{background:var(--code-bg);font-weight:600}
.pub-article img{max-width:100%;height:auto;border-radius:var(--radius-s)}
figure.img-wrap{margin:1.5em 0}
figure.img-wrap img{display:block}
figure.img-wrap figcaption{color:var(--muted);font-size:.875rem;
font-family:var(--font-ui);margin-top:.4rem}
.callout{border-left:3px solid var(--link);background:var(--surface);
border-radius:0 var(--radius-m) var(--radius-m) 0;padding:.8rem 1rem;
margin:1.2em 0;box-shadow:var(--shadow-sm);font-family:var(--font-ui);font-size:.95rem}
.callout.attention{border-color:var(--danger)}
.callout.astuce{border-color:var(--ok)}
.callout-title{font-weight:700;font-size:.8rem;margin:0 0 .3rem;
text-transform:uppercase;letter-spacing:.03em}
.callout p{margin:0 0 .5em}
.callout p:last-child{margin-bottom:0}
.task-list{list-style:none;padding-left:.2rem}
.task-list-item{margin:.35em 0}
.task-list-control{display:inline-flex;align-items:center;margin-right:.5rem}
.task-list-control input{width:1.1rem;height:1.1rem;accent-color:var(--accent)}
.pub-foot{border-top:1px solid var(--border);margin:3rem 0 0;padding:1rem 0 3rem;
color:var(--muted);font-size:.85rem;display:flex;flex-wrap:wrap;gap:.6rem;align-items:center}
.pub-foot .sep{flex:1 1 auto}
button,.btn{font-family:var(--font-ui);font-size:1rem;min-height:44px;
padding:.55rem 1rem;border-radius:var(--radius-m);border:1px solid var(--border);
background:var(--surface);color:var(--fg);cursor:pointer}
.btn-primary{background:var(--accent);border-color:var(--accent);color:#fff}
.btn-primary:hover{filter:brightness(.94)}
.themebox{display:flex;gap:.5rem;align-items:center;font-size:.85rem}
.themebox select{font-size:1rem;min-height:44px;border:1px solid var(--border);
border-radius:var(--radius-m);background:var(--surface);color:var(--fg);padding:.3rem .6rem}
#totop{position:fixed;right:1rem;bottom:1rem;z-index:50;text-decoration:none;
background:var(--surface);border:1px solid var(--border);box-shadow:var(--shadow-sm)}
#totop[hidden]{display:none}
.pass-card{max-width:24rem;margin:2rem auto;text-align:center}
.pass-card form{display:flex;flex-direction:column;gap:.7rem;margin-top:1.2rem}
.pass-card label{text-align:left;font-size:.875rem;font-weight:600}
.pass-card input[type=password],.pass-card input[type=text]{font-size:1rem;
min-height:44px;padding:.6rem .8rem;border:1px solid var(--border);
border-radius:var(--radius-m);background:var(--surface);color:var(--fg);width:100%}
.pass-row{display:flex;gap:.6rem}
.pass-row input{flex:1 1 auto;min-width:0}
.form-error{color:var(--danger);font-size:.9rem;background:var(--surface);
border:1px solid var(--danger);border-radius:var(--radius-m);padding:.6rem .8rem}
.form-hint{color:var(--muted);font-size:.85rem}
.print-only{display:none}
.arithmatex{overflow-x:auto;max-width:100%}
@media print{
.topbar,.progress,#totop,.copybtn,#copylink,.themebox,form,details.toc{display:none !important}
body{background:#fff;color:#000;font-size:12pt}
.pub-wrap{max-width:none;padding:0}
.pub-article{font-size:12pt;max-width:none}
a[href^="http"]::after{content:" (" attr(href) ")";font-size:.85em}
@page{margin:2cm}
.print-only{display:block;border-top:1px solid #000;margin-top:2cm;
padding-top:.5cm;font-size:10pt;color:#000}
}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}
*{animation:none !important;transition:none !important}}
"""

THEME_HEAD_JS = """<script>try{var t=localStorage.getItem("zn-theme");document.documentElement.setAttribute("data-theme",(t==="light"||t==="dark")?t:"auto");}catch(e){}</script>"""

THEME_FOOT_JS = """<script>document.addEventListener("DOMContentLoaded",function(){var s=document.getElementById("theme");if(!s){return;}function cur(){try{return localStorage.getItem("zn-theme")||"auto";}catch(e){return "auto";}}s.value=cur();s.addEventListener("change",function(){var v=s.value;try{localStorage.setItem("zn-theme",v);}catch(e){}document.documentElement.setAttribute("data-theme",v);});});</script>"""

KATEX_HEAD = """<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.js" integrity="sha384-Rma6DA2IPUwhNxmrB/7S3Tno0YY7sFu9WSYMCuulLhIqYSGZ2gKCJWIqhBWqMQfh" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/contrib/auto-render.min.js" integrity="sha384-hCXGrW6PitJEwbkoStFjeJxv+fSOOQKOPbJxSfM6G5sWZjAyWhXiTIIAmQqnlLlh" crossorigin="anonymous"></script>"""

PUB_JS = """<script>document.addEventListener("DOMContentLoaded",function(){
var s=document.getElementById("theme");
function cur(){try{return localStorage.getItem("zn-theme")||"auto";}catch(e){return "auto";}}
if(s){s.value=cur();s.addEventListener("change",function(){var v=s.value;try{localStorage.setItem("zn-theme",v);}catch(e){}document.documentElement.setAttribute("data-theme",v);});}
var bar=document.getElementById("progressbar");
var totop=document.getElementById("totop");
function prog(){var h=document.documentElement;var max=h.scrollHeight-h.clientHeight;var r=max>0?h.scrollTop/max:0;if(bar){bar.style.width=(r*100).toFixed(1)+"%";}if(totop){totop.hidden=!(h.scrollTop>2*window.innerHeight);}}
document.addEventListener("scroll",function(){requestAnimationFrame(prog);},{passive:true});prog();
var toc=document.querySelector("details.toc");if(toc&&!toc.querySelector("a")){toc.hidden=true;}
var canCopy=!!(navigator.clipboard&&navigator.clipboard.writeText);
function copyText(t,btn,ok){if(!canCopy){if(btn){btn.style.display="none";}return;}navigator.clipboard.writeText(t).then(function(){if(!btn){return;}var o=btn.textContent;btn.textContent=ok;setTimeout(function(){btn.textContent=o;},1500);},function(){if(btn){btn.style.display="none";}});}
document.querySelectorAll(".pub-article div.highlight").forEach(function(box){box.style.position="relative";var b=document.createElement("button");b.type="button";b.className="copybtn";b.textContent="Copier";if(!canCopy){b.style.display="none";}b.addEventListener("click",function(){var c=box.querySelector("code");copyText(c?c.innerText:box.innerText,b,"Copie");});box.appendChild(b);});
document.querySelectorAll(".pub-article pre").forEach(function(pre){if(pre.closest("div.highlight")){return;}var w=document.createElement("div");w.className="codebox";pre.parentNode.insertBefore(w,pre);w.appendChild(pre);var b=document.createElement("button");b.type="button";b.className="copybtn";b.textContent="Copier";if(!canCopy){b.style.display="none";}b.addEventListener("click",function(){copyText(pre.innerText,b,"Copie");});w.appendChild(b);});
var cl=document.getElementById("copylink");if(cl){if(!canCopy){cl.style.display="none";}else{cl.hidden=false;cl.addEventListener("click",function(){copyText(location.href,cl,"Lien copie");});}}
var art=document.querySelector(".pub-article");
if(art&&window.renderMathInElement){try{window.renderMathInElement(art,{delimiters:[{left:"$$",right:"$$",display:true},{left:"$",right:"$",display:false},{left:"\\\\(",right:"\\\\)",display:false},{left:"\\\\[",right:"\\\\]",display:true}],trust:false,throwOnError:false,strict:"warn"});}catch(e){}}
});</script>"""

PASS_JS = """<script>document.addEventListener("DOMContentLoaded",function(){var s=document.getElementById("theme");function cur(){try{return localStorage.getItem("zn-theme")||"auto";}catch(e){return "auto";}}if(s){s.value=cur();s.addEventListener("change",function(){var v=s.value;try{localStorage.setItem("zn-theme",v);}catch(e){}document.documentElement.setAttribute("data-theme",v);});}var t=document.getElementById("togglepw");var f=document.getElementById("pw");if(t&&f){t.addEventListener("click",function(){var show=f.type==="password";f.type=show?"text":"password";t.textContent=show?"Masquer":"Afficher";t.setAttribute("aria-pressed",show?"true":"false");f.focus();});}});</script>"""

FONTS_LINK = """<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&amp;family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&amp;display=swap" rel="stylesheet" media="print" onload="this.media='all'"><noscript><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&amp;family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&amp;display=swap" rel="stylesheet"></noscript>"""

NOT_FOUND_HTML = """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>Lien indisponible</title>
""" + THEME_HEAD_JS + """
""" + FONTS_LINK + """
<style>""" + BASE_CSS + """</style></head>
<body><div class="progress" aria-hidden="true"><span></span></div>
<header class="topbar"><div class="topbar-in"><span class="brand"><span class="dot"></span>ZenNotes</span><span class="badge">Lecture partagee</span></div></header>
<main class="pub-wrap"><header class="hero"><h1>Lien indisponible</h1></header><hr class="filet">
<p>Ce lien est invalide ou expire.</p>
<p class="form-hint">Demande a l expediteur de generer un nouveau lien si besoin.</p>
</main>
<footer class="pub-wrap pub-foot"><span>Partage via ZenNotes</span><span class="sep"></span><label class="themebox">Theme <select id="theme"><option value="auto">Auto</option><option value="light">Clair</option><option value="dark">Sombre</option></select></label></footer>
""" + THEME_FOOT_JS + """</body></html>"""

PASSWORD_HTML = """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>Note protegee</title>
""" + THEME_HEAD_JS + """
""" + FONTS_LINK + """
<style>""" + BASE_CSS + """</style></head>
<body><div class="progress" aria-hidden="true"><span></span></div>
<header class="topbar"><div class="topbar-in"><span class="brand"><span class="dot"></span>ZenNotes</span><span class="badge">Lecture partagee</span></div></header>
<main class="pub-wrap"><header class="hero"><h1>Note protegee</h1><p class="meta">__TITLE__</p></header><hr class="filet">
<div class="pass-card">__ERROR__
<p>Cette note est protegee par un mot de passe. Saisis le pour continuer.</p>
<form method="get" action=""><label for="pw">Mot de passe</label>
<div class="pass-row"><input type="password" id="pw" name="p" autocomplete="current-password" enterkeyhint="go" autocorrect="off" autocapitalize="off" spellcheck="false" autofocus><button type="button" id="togglepw" aria-pressed="false">Afficher</button></div>
<button type="submit" class="btn-primary">Ouvrir</button></form>
<p class="form-hint">__EXPIRY__</p></div>
</main>
<footer class="pub-wrap pub-foot"><span>Partage via ZenNotes</span><span class="sep"></span><label class="themebox">Theme <select id="theme"><option value="auto">Auto</option><option value="light">Clair</option><option value="dark">Sombre</option></select></label></footer>
""" + PASS_JS + """</body></html>"""

PAGE_HTML = """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>__TITLE__</title>
""" + THEME_HEAD_JS + """
""" + FONTS_LINK + """
""" + KATEX_HEAD + """
<style>""" + BASE_CSS + """
__PYGMENTS__</style></head>
<body id="top"><div class="progress" aria-hidden="true"><span id="progressbar"></span></div>
<header class="topbar"><div class="topbar-in"><span class="brand"><span class="dot"></span>ZenNotes</span><span class="badge">Lecture partagee</span><span class="readtime">__READTIME__</span></div></header>
<main class="pub-wrap"><header class="hero"><h1>__TITLE__</h1><p class="meta">__META__</p></header><hr class="filet">
__TOC__
<article class="pub-article">__CONTENT__</article>
<div class="print-only">__PRINTONLY__</div>
</main>
<footer class="pub-wrap pub-foot"><span>Partage via ZenNotes</span><span>__EXPIRY__</span><span class="sep"></span><button id="copylink" hidden>Copier le lien</button><label class="themebox">Theme <select id="theme"><option value="auto">Auto</option><option value="light">Clair</option><option value="dark">Sombre</option></select></label></footer>
<a href="#top" id="totop" hidden>Haut de page</a>
""" + PUB_JS + """</body></html>"""


def _fill(template: str, mapping: dict) -> str:
    """Remplit les marqueurs __X__ sans str.format (accolades CSS/JS)."""
    out = template
    for key, value in mapping.items():
        out = out.replace(key, value)
    return out


def _fmt_dt(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%d/%m/%Y a %Hh%M")

ADMIN_HTML = """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>ZenNotes Share - Administration</title>
<script>try{var t=localStorage.getItem("zn-theme");document.documentElement.setAttribute("data-theme",(t==="light"||t==="dark")?t:"auto");}catch(e){}</script>
<style>""" + BASE_CSS + """
.admin-wrap{max-width:72rem;margin:0 auto;padding:1.25rem 1.25rem 5rem;width:100%}
.admin-top .topbar-in{max-width:72rem}
.key-status{color:var(--muted);font-size:.8125rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:9rem}
.spacer{flex:1 1 auto}
button.ghost{background:var(--surface);color:var(--fg);border:1px solid var(--border)}
button.ghost:hover{border-color:var(--accent)}
button.danger{background:var(--surface);color:var(--danger);border:1px solid var(--danger)}
button.danger:hover{background:var(--danger);color:#fff}
.hbtn{min-height:44px;min-width:44px;display:inline-flex;align-items:center;justify-content:center}
.admin-layout{display:grid;grid-template-columns:1fr;gap:1rem;align-items:start}
@media(min-width:800px){.admin-layout{grid-template-columns:22rem minmax(0,1fr);gap:1.2rem}}
@media(min-width:1100px){.admin-wrap{padding:1.5rem 1.5rem 5rem}.admin-layout{gap:1.5rem}}
.stack{display:grid;gap:1rem;align-items:start}
@media(min-width:800px){.stack{gap:1.2rem}}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-l);padding:1rem 1.1rem;box-shadow:var(--shadow-sm);min-width:0}
.card h2{margin:.1rem 0 .8rem;font-size:1.15rem;line-height:1.25}
.card label.flabel,.card span.flabel{display:block;font-size:.875rem;font-weight:600;margin:.7rem 0 .3rem}
.card input[type=text],.card input[type=number],.card input[type=password],.card input[type=search]{font-size:1rem;min-height:44px;padding:.55rem .7rem;border:1px solid var(--border);border-radius:var(--radius-m);background:var(--surface);color:var(--fg);width:100%}
.search-sticky{position:sticky;top:3.8rem;z-index:20;background:var(--surface);padding:.4rem 0 .6rem}
.search-row{display:flex;gap:.5rem}
.search-row input{flex:1 1 auto;min-width:0}
#clearQ{flex:0 0 44px}
#notelist{max-height:24rem;overflow:auto;border:1px solid var(--border);border-radius:var(--radius-m);margin-top:.6rem}
.note{padding:.6rem .75rem;border-bottom:1px solid var(--border);cursor:pointer;min-height:44px}
.note:last-child{border-bottom:0}
.note:hover{background:var(--code-bg)}
.note.sel{border-left:3px solid var(--accent);padding-left:calc(.75rem - 3px)}
.note .t{font-weight:600;font-size:.95rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.note .p{color:var(--muted);font-size:.8125rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.seg{display:flex;gap:.5rem;margin-top:.3rem}
.seg button{flex:1 1 0;min-height:44px;background:var(--surface);color:var(--fg);border:1px solid var(--border)}
.seg button[aria-pressed=true]{background:var(--accent);border-color:var(--accent);color:#fff}
details.opts{border:1px solid var(--border);border-radius:var(--radius-m);margin-top:.8rem}
details.opts summary{cursor:pointer;padding:.7rem .8rem;font-weight:600;min-height:44px;font-size:.9rem}
details.opts .opts-in{padding:0 .8rem .9rem}
.pass-line{display:flex;gap:.5rem}
.pass-line input{flex:1 1 auto;min-width:0}
.create-cta{position:sticky;bottom:0;background:var(--surface);padding:.7rem 0 .2rem;margin-top:.8rem}
.create-cta button{width:100%;min-height:48px}
@media(min-width:800px){.create-cta{position:static}}
.badge.warn{color:var(--danger);border-color:var(--danger)}
.link-badges{display:flex;gap:.4rem;flex-wrap:wrap}
#linkCards{display:grid;gap:.7rem}
.link-card{border:1px solid var(--border);border-radius:var(--radius-m);padding:.8rem;display:grid;gap:.55rem}
.link-card h3{margin:0;font-size:1rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.link-card .path{color:var(--muted);font-size:.8125rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.link-card.pending,.table-wrap tr.pending{opacity:.55}
.link-actions{display:flex;gap:.5rem}
.link-actions button{flex:1 1 0;min-height:44px}
.table-wrap{display:none}
@media(min-width:800px){.table-wrap{display:block;overflow-x:auto;border:1px solid var(--border);border-radius:var(--radius-m)}.table-wrap table{border-collapse:collapse;width:100%;font-size:.9rem;line-height:1.5}.table-wrap th,.table-wrap td{border-bottom:1px solid var(--border);padding:.55rem .6rem;text-align:left;vertical-align:top}.table-wrap thead th{background:var(--code-bg);font-size:.8rem}#linkCards{display:none}}
.outlink{overflow-wrap:break-word;word-break:break-all}
#toast{position:fixed;bottom:1.2rem;left:50%;transform:translateX(-50%);background:#22201b;color:#fff;padding:.7rem 1rem;border-radius:var(--radius-m);display:none;z-index:90;max-width:min(92vw,28rem);font-size:.95rem;line-height:1.4;text-align:center;box-shadow:0 4px 16px rgba(0,0,0,.25)}
#toast.show{display:flex;gap:.7rem;align-items:center;justify-content:center}
#toast button{flex:0 0 auto;min-height:44px;min-width:44px;background:#fff;color:#22201b;border:0}
.empty{border:1px dashed var(--border);border-radius:var(--radius-m);padding:1rem;text-align:center;color:var(--muted);font-size:.9rem}
.empty button{margin-top:.6rem;min-height:44px}
#login{margin:2.5rem auto}
#loginBtn{width:100%}
.login-help{color:var(--muted);font-size:.85rem}
.visually-hidden{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
</style></head>
<body>
<header class="topbar admin-top"><div class="topbar-in"><span class="brand"><span class="dot"></span>ZenNotes Share</span><span id="keyStatus" class="key-status">Non connecte</span><span class="spacer"></span><button id="themeBtn" class="ghost hbtn" type="button" aria-pressed="false">Theme : Auto</button><button id="logoutBtn" class="ghost hbtn" type="button" hidden>Deconnexion</button></div></header>
<main class="admin-wrap">
<section class="pass-card" id="login" aria-labelledby="loginTitle"><h1 id="loginTitle" style="font-size:1.25rem;margin:.2rem 0 .4rem">Connexion</h1>
<p class="login-help">Saisis ta cle admin. Elle est conservee dans cet onglet uniquement (sessionStorage), jamais dans l URL.</p>
<form id="loginForm" novalidate><label for="key">Cle admin</label>
<input type="password" id="key" name="key" autocomplete="current-password" autocorrect="off" autocapitalize="off" spellcheck="false" enterkeyhint="go" aria-describedby="loginError">
<p id="loginError" class="form-error" role="alert" hidden></p>
<div style="margin-top:.8rem"><button id="loginBtn" class="btn-primary" type="submit">Ouvrir</button></div></form></section>
<div id="app" hidden>
<div class="admin-layout">
<section class="card" aria-labelledby="notesTitle"><h2 id="notesTitle">Notes du vault</h2>
<div class="search-sticky"><label class="flabel" for="q">Filtrer les notes</label>
<div class="search-row"><input type="search" id="q" placeholder="Filtrer par titre ou chemin" autocomplete="off" aria-describedby="count"><button id="clearQ" class="ghost" type="button" aria-label="Effacer la recherche" hidden>X</button></div>
<p id="count" class="muted" role="status" aria-live="polite">Chargement...</p></div>
<div id="notelist" role="listbox" aria-label="Notes du vault" tabindex="0"><p class="muted" style="padding:.8rem">Chargement...</p></div>
<div id="notesEmpty" class="empty" hidden><p>Aucune note ici pour le moment (vault vide ou filtre trop strict).</p><button id="resetQ" class="ghost" type="button">Reinitialiser</button></div>
<div id="notesOffline" class="empty" hidden><p>Notes inaccessibles (hors ligne ou serveur injoignable).</p><button id="retryNotes" class="ghost" type="button">Reessayer</button></div>
</section>
<div class="stack">
<section class="card" aria-labelledby="newTitle"><h2 id="newTitle">Nouveau lien</h2>
<form id="createForm" novalidate>
<label class="flabel" for="f_path">Note (chemin vault)</label>
<input type="text" id="f_path" placeholder="Clique une note, ou saisis inbox/... ou quick/..." autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" enterkeyhint="next" aria-describedby="pathHelp createError">
<p id="pathHelp" class="muted">Exemple : quick/ma-note.md. Le clic sur une note remplit ce champ.</p>
<span class="flabel" id="ttlLabel">Duree du lien</span>
<div class="seg" role="group" aria-labelledby="ttlLabel"><button type="button" data-ttl="24" aria-pressed="true">24 h</button><button type="button" data-ttl="168" aria-pressed="false">7 j</button><button type="button" data-ttl="720" aria-pressed="false">30 j</button></div>
<label class="flabel" for="f_ttl">Duree personnalisee (heures, 1 a 720)</label>
<input type="number" id="f_ttl" value="24" min="1" max="720" inputmode="numeric" aria-describedby="createError">
<details class="opts"><summary>Options : vues max et mot de passe</summary><div class="opts-in">
<label class="flabel" for="f_views">Vues max (vide = illimite)</label>
<input type="number" id="f_views" placeholder="illimite" min="1" inputmode="numeric" aria-describedby="createError">
<label class="flabel" for="f_pw">Mot de passe (optionnel)</label>
<div class="pass-line"><input type="password" id="f_pw" placeholder="aucun" autocomplete="new-password" autocorrect="off" autocapitalize="off" spellcheck="false" aria-describedby="createError"><button id="togglePw" class="ghost" type="button" aria-pressed="false" aria-label="Afficher le mot de passe">Afficher</button></div>
</div></details>
<p id="createError" class="form-error" role="alert" hidden></p>
<div id="outWrap" hidden><p class="muted">Lien cree :</p><p><a id="outLink" class="outlink" href="#" target="_blank" rel="noopener"></a></p><p id="outMeta" class="muted"></p><div class="link-actions"><button id="copyOut" class="ghost" type="button">Copier</button></div></div>
<div class="create-cta"><button id="createBtn" class="btn-primary" type="submit">Creer le lien</button></div>
</form></section>
<section class="card" aria-labelledby="linksTitle"><h2 id="linksTitle">Liens actifs</h2>
<div class="table-wrap" tabindex="0"><table><thead><tr><th scope="col">Note</th><th scope="col">Expire</th><th scope="col">Vues</th><th scope="col">Actions</th></tr></thead><tbody id="rows"></tbody></table></div>
<div id="linkCards"></div>
<div id="linksEmpty" class="empty" hidden><p>Aucun lien pour le moment. Cree ton premier lien depuis une note.</p><button id="ctaFirst" class="ghost" type="button">Creer mon premier lien</button></div>
<div id="linksOffline" class="empty" hidden><p>Liste indisponible (hors ligne ?).</p><button id="retryLinks" class="ghost" type="button">Reessayer</button></div>
</section>
</div>
</div>
</div>
</main>
<div id="toast" role="status" aria-live="polite"></div>
<script>
(function(){"use strict";
var NOTES=[];var pendingRevoke={};var toastTimer=null;
function $(id){return document.getElementById(id);}
function auth(){var k="";try{k=sessionStorage.getItem("sk")||"";}catch(e){}return {Authorization:"Bearer "+k};}
function hideToast(){var t=$("toast");if(toastTimer){clearTimeout(toastTimer);toastTimer=null;}t.className="";t.innerHTML="";t.onclick=null;}
function toast(msg,opts){opts=opts||{};var dur=opts.duration||3000;var t=$("toast");if(toastTimer){clearTimeout(toastTimer);toastTimer=null;}t.innerHTML="";var s=document.createElement("span");s.textContent=msg;t.appendChild(s);if(opts.actionLabel){var b=document.createElement("button");b.type="button";b.textContent=opts.actionLabel;b.addEventListener("click",function(ev){ev.stopPropagation();hideToast();if(opts.onAction){opts.onAction();}});t.appendChild(b);}t.className="show";t.onclick=function(){hideToast();};toastTimer=setTimeout(hideToast,dur);}
function getTheme(){try{return localStorage.getItem("zn-theme")||"auto";}catch(e){return "auto";}}
function paintTheme(){var v=getTheme();var b=$("themeBtn");b.textContent="Theme : "+(v==="light"?"Clair":v==="dark"?"Sombre":"Auto");b.setAttribute("aria-pressed",v==="auto"?"false":"true");}
function setTheme(v){try{localStorage.setItem("zn-theme",v);}catch(e){}document.documentElement.setAttribute("data-theme",v);paintTheme();}
function setStatus(x){$("keyStatus").textContent=x;}
function showLogin(msg){$("login").hidden=false;$("app").hidden=true;$("logoutBtn").hidden=true;setStatus("Non connecte");var e=$("loginError");if(msg){e.textContent=msg;e.hidden=false;}else{e.textContent="";e.hidden=true;}}
function showApp(){$("login").hidden=true;$("app").hidden=false;$("logoutBtn").hidden=false;setStatus("Cle active");}
function onInvalidKey(){var k="";try{k=sessionStorage.getItem("sk")||"";}catch(e){}if(k&&!$("key").value){$("key").value=k;}showLogin("Cle invalide, verifie puis reessaie.");toast("Cle invalide.");try{$("key").focus();}catch(e){}}
function fmtDate(ts){try{return new Date(ts*1000).toLocaleString("fr-FR",{day:"2-digit",month:"2-digit",year:"numeric",hour:"2-digit",minute:"2-digit"});}catch(e){return String(ts);}}
function viewsLabel(l){return String(l.views)+"/"+(l.max_views?String(l.max_views):"infini");}
async function copyText(t){if(navigator.clipboard&&navigator.clipboard.writeText){try{await navigator.clipboard.writeText(t);toast("Lien copie.");return;}catch(e){}}var ta=document.createElement("textarea");ta.value=t;document.body.appendChild(ta);ta.select();try{document.execCommand("copy");toast("Lien copie.");}catch(e){toast("Copie impossible : selectionne le lien manuellement.");}try{document.body.removeChild(ta);}catch(e){}}
async function loadNotes(){var c=$("count");c.textContent="Chargement...";$("notesOffline").hidden=true;try{var r=await fetch("/api/notes",{headers:auth()});if(r.status===401){onInvalidKey();return;}if(!r.ok){throw new Error("http "+r.status);}NOTES=await r.json();renderNotes($("q").value||"");}catch(e){var box=$("notelist");box.innerHTML="";var p=document.createElement("p");p.className="muted";p.style.padding=".8rem";p.textContent="Notes inaccessibles.";box.appendChild(p);c.textContent="Hors ligne";$("notesEmpty").hidden=true;$("notesOffline").hidden=false;}}
function renderNotes(f){f=(f||"").toLowerCase();var box=$("notelist");box.innerHTML="";var sel=$("f_path").value;var n=0;for(var i=0;i<NOTES.length;i++){var x=NOTES[i];if(f&&(String(x.path).toLowerCase().indexOf(f)<0&&String(x.title).toLowerCase().indexOf(f)<0)){continue;}n++;(function(note){var d=document.createElement("div");d.className="note"+(sel&&sel===note.path?" sel":"");d.setAttribute("role","option");d.setAttribute("tabindex","0");d.setAttribute("aria-selected",sel===note.path?"true":"false");var t=document.createElement("div");t.className="t";t.textContent=note.title;var p=document.createElement("div");p.className="p";p.textContent=note.path;d.appendChild(t);d.appendChild(p);function pick(){$("f_path").value=note.path;var all=box.querySelectorAll(".note");for(var k=0;k<all.length;k++){all[k].classList.remove("sel");all[k].setAttribute("aria-selected","false");}d.classList.add("sel");d.setAttribute("aria-selected","true");}d.addEventListener("click",pick);d.addEventListener("keydown",function(ev){if(ev.key==="Enter"||ev.key===" "){ev.preventDefault();pick();}});box.appendChild(d);})(x);}var c=$("count");c.textContent=n===0?"0 note":n===1?"1 note":n+" notes";$("clearQ").hidden=!$("q").value;$("notesEmpty").hidden=!(n===0&&$("notesOffline").hidden);}
function setTtl(v){$("f_ttl").value=String(v);var btns=document.querySelectorAll(".seg button");for(var i=0;i<btns.length;i++){btns[i].setAttribute("aria-pressed",btns[i].getAttribute("data-ttl")===String(v)?"true":"false");}}
function syncSeg(){var v=$("f_ttl").value;var btns=document.querySelectorAll(".seg button");for(var i=0;i<btns.length;i++){btns[i].setAttribute("aria-pressed",btns[i].getAttribute("data-ttl")===String(v)?"true":"false");}}
async function doCreate(){var err=$("createError");err.hidden=true;err.textContent="";var path=$("f_path").value.trim();var ttl=parseInt($("f_ttl").value,10);var viewsRaw=$("f_views").value.trim();var pw=$("f_pw").value;var firstBad=null;function bad(msg,el){if(err.hidden){err.textContent=msg;err.hidden=false;}if(!firstBad){firstBad=el;}}if(!path){bad("Choisis une note : clique une note du vault ou saisis son chemin.",$("f_path"));}else if(path.toLowerCase().slice(-3)!==".md"){bad("Le chemin doit designer un fichier .md du vault.",$("f_path"));}if(!(ttl>=1&&ttl<=720)){bad("Duree invalide : saisis entre 1 et 720 heures.",$("f_ttl"));}var maxViews=null;if(viewsRaw){maxViews=parseInt(viewsRaw,10);if(!(maxViews>=1)){bad("Vues max invalide : saisis 1 ou plus, ou laisse vide.",$("f_views"));}}if(!err.hidden){if(firstBad){try{firstBad.focus();}catch(e){}}return;}var body={path:path,ttl_hours:ttl};if(maxViews!==null){body.max_views=maxViews;}if(pw){body.password=pw;}var btn=$("createBtn");btn.disabled=true;try{var r=await fetch("/api/links",{method:"POST",headers:Object.assign({"Content-Type":"application/json"},auth()),body:JSON.stringify(body)});var j=null;try{j=await r.json();}catch(e){j=null;}if(r.status===401){onInvalidKey();return;}if(!r.ok){err.textContent="Erreur : "+((j&&j.detail)||("serveur "+r.status));err.hidden=false;try{$("f_path").focus();}catch(e){}return;}var a=$("outLink");a.href=j.url;a.textContent=j.url;a.target="_blank";$("outMeta").textContent="Expire le "+fmtDate(j.expires_at)+".";$("outWrap").hidden=false;toast("Lien cree. Utilise Copier pour le partager.");}catch(e){err.textContent="Hors ligne : lien non cree. Reessaie.";err.hidden=false;}finally{btn.disabled=false;}await refresh();}
async function refresh(){var tb=$("rows");tb.innerHTML="";$("linkCards").innerHTML="";$("linksEmpty").hidden=true;$("linksOffline").hidden=true;try{var r=await fetch("/api/links",{headers:auth()});if(r.status===401){onInvalidKey();return;}if(!r.ok){throw new Error("http "+r.status);}var items=await r.json();if(!items.length){$("linksEmpty").hidden=false;return;}for(var i=0;i<items.length;i++){addLinkRow(items[i]);addLinkCard(items[i]);}}catch(e){$("linksOffline").hidden=false;}}
function linkUrl(t){return location.origin+"/s/"+t;}
function addLinkRow(l){var tb=$("rows");var tr=document.createElement("tr");tr.id="row-"+l.token;var u=linkUrl(l.token);var c0=document.createElement("td");var a=document.createElement("a");a.href=u;a.target="_blank";a.rel="noopener";a.textContent=l.title;c0.appendChild(a);var ps=document.createElement("div");ps.className="muted";ps.textContent=l.path;c0.appendChild(ps);if(l.has_password){var lk=document.createElement("span");lk.className="badge warn";lk.textContent=" Protege";c0.appendChild(lk);}var c1=document.createElement("td");c1.textContent=fmtDate(l.expires_at);var c2=document.createElement("td");c2.textContent=viewsLabel(l);var c3=document.createElement("td");var cp=document.createElement("button");cp.className="ghost";cp.type="button";cp.textContent="Copier";cp.addEventListener("click",function(){copyText(u);});var rv=document.createElement("button");rv.className="danger";rv.type="button";rv.textContent="Revoquer";rv.addEventListener("click",function(){askRevoke(l.token,l.title);});c3.appendChild(cp);c3.appendChild(document.createTextNode(" "));c3.appendChild(rv);tr.appendChild(c0);tr.appendChild(c1);tr.appendChild(c2);tr.appendChild(c3);tb.appendChild(tr);}
function addLinkCard(l){var box=$("linkCards");var d=document.createElement("div");d.className="link-card";d.id="card-"+l.token;var h=document.createElement("h3");h.textContent=l.title;d.appendChild(h);var p=document.createElement("div");p.className="path";p.textContent=l.path;d.appendChild(p);var bg=document.createElement("div");bg.className="link-badges";var b1=document.createElement("span");b1.className="badge";b1.textContent="Expire "+fmtDate(l.expires_at);bg.appendChild(b1);var b2=document.createElement("span");b2.className="badge";b2.textContent=viewsLabel(l)+" vues";bg.appendChild(b2);if(l.has_password){var b3=document.createElement("span");b3.className="badge warn";b3.textContent="Protege";bg.appendChild(b3);}d.appendChild(bg);var ac=document.createElement("div");ac.className="link-actions";var u=linkUrl(l.token);var cp=document.createElement("button");cp.className="ghost";cp.type="button";cp.textContent="Copier";cp.addEventListener("click",function(){copyText(u);});var rv=document.createElement("button");rv.className="danger";rv.type="button";rv.textContent="Revoquer";rv.addEventListener("click",function(){askRevoke(l.token,l.title);});ac.appendChild(cp);ac.appendChild(rv);d.appendChild(ac);box.appendChild(d);}
function markPending(token,on){var r=$("row-"+token);if(r){if(on){r.classList.add("pending");}else{r.classList.remove("pending");}}var c=$("card-"+token);if(c){if(on){c.classList.add("pending");}else{c.classList.remove("pending");}}}
function askRevoke(token,title){if(!window.confirm("Revoquer le lien "+title+" ? Le destinataire ne pourra plus l ouvrir.")){return;}markPending(token,true);toast("Revocation en attente.",{duration:5000,actionLabel:"Annuler",onAction:function(){cancelRevoke(token);}});if(pendingRevoke[token]){clearTimeout(pendingRevoke[token]);}pendingRevoke[token]=setTimeout(function(){doRevoke(token);},5000);}
function cancelRevoke(token){if(pendingRevoke[token]){clearTimeout(pendingRevoke[token]);delete pendingRevoke[token];}markPending(token,false);toast("Revocation annulee.");}
async function doRevoke(token){if(pendingRevoke[token]){clearTimeout(pendingRevoke[token]);delete pendingRevoke[token];}try{var r=await fetch("/api/links/"+encodeURIComponent(token),{method:"DELETE",headers:auth()});if(r.status===401){markPending(token,false);onInvalidKey();return;}await refresh();toast("Lien revoque.");}catch(e){markPending(token,false);toast("Hors ligne : revocation non envoyee. Reessaie.");}}
document.addEventListener("DOMContentLoaded",function(){
paintTheme();
$("themeBtn").addEventListener("click",function(){var v=getTheme();setTheme(v==="auto"?"light":v==="light"?"dark":"auto");});
$("logoutBtn").addEventListener("click",function(){try{sessionStorage.removeItem("sk");}catch(e){}$("key").value="";showLogin("");try{$("key").focus();}catch(e){}toast("Deconnecte.");});
$("loginForm").addEventListener("submit",async function(ev){ev.preventDefault();var k=$("key").value;var e=$("loginError");e.hidden=true;if(!k){e.textContent="Saisis ta cle admin.";e.hidden=false;try{$("key").focus();}catch(x){}return;}var btn=$("loginBtn");btn.disabled=true;try{var r=await fetch("/api/notes",{headers:{Authorization:"Bearer "+k}});if(r.status===401){showLogin("Cle invalide, verifie puis reessaie.");try{$("key").focus();}catch(x){}return;}if(!r.ok){e.textContent="Connexion impossible (serveur "+r.status+"). Reessaie.";e.hidden=false;return;}try{sessionStorage.setItem("sk",k);}catch(x){}NOTES=await r.json();showApp();renderNotes("");await refresh();toast("Connecte.");}catch(x){e.textContent="Hors ligne : verifie ta connexion puis reessaie.";e.hidden=false;}finally{btn.disabled=false;}});
$("q").addEventListener("input",function(){renderNotes($("q").value);});
$("q").addEventListener("keydown",function(ev){if(ev.key==="Enter"){ev.preventDefault();var f=$("notelist").querySelector(".note");if(f){f.focus();}}if(ev.key==="Escape"){if($("q").value){$("q").value="";renderNotes("");}else{try{$("q").blur();}catch(x){}}}});
$("clearQ").addEventListener("click",function(){$("q").value="";renderNotes("");try{$("q").focus();}catch(x){}});
$("resetQ").addEventListener("click",function(){$("q").value="";renderNotes("");try{$("q").focus();}catch(x){}});
$("retryNotes").addEventListener("click",loadNotes);
$("retryLinks").addEventListener("click",refresh);
var seg=document.querySelectorAll(".seg button");for(var i=0;i<seg.length;i++){seg[i].addEventListener("click",function(){setTtl(this.getAttribute("data-ttl"));});}
$("f_ttl").addEventListener("input",syncSeg);
$("togglePw").addEventListener("click",function(){var f=$("f_pw");var show=f.type==="password";f.type=show?"text":"password";this.textContent=show?"Masquer":"Afficher";this.setAttribute("aria-pressed",show?"true":"false");try{f.focus();}catch(x){}});
$("createForm").addEventListener("submit",function(ev){ev.preventDefault();doCreate();});
$("copyOut").addEventListener("click",function(){var a=$("outLink");if(a&&a.href){copyText(a.href);}});
$("ctaFirst").addEventListener("click",function(){try{$("newTitle").scrollIntoView();}catch(x){}try{$("f_path").focus();}catch(y){}});
document.addEventListener("keydown",function(ev){if(ev.key==="Escape"){hideToast();}});
window.addEventListener("offline",function(){toast("Tu es hors ligne.");});
window.addEventListener("online",function(){toast("Connexion retrouvee.");loadNotes();refresh();});
var k=null;try{k=sessionStorage.getItem("sk");}catch(x){}if(k){$("key").value=k;(async function(){try{var r=await fetch("/api/notes",{headers:{Authorization:"Bearer "+k}});if(!r.ok){if(r.status===401){showLogin("Cle invalide, verifie puis reessaie.");}return;}NOTES=await r.json();showApp();renderNotes("");await refresh();}catch(x){}})();}
});
})();
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
                err = ""
                if p is not None:
                    err = (
                        '<p class="form-error" role="alert">'
                        "Mot de passe incorrect, verifie puis reessaie.</p>"
                    )
                page = _fill(
                    PASSWORD_HTML,
                    {
                        "__TITLE__": html.escape(entry["title"], quote=True),
                        "__EXPIRY__": "Ce lien expire le "
                        + _fmt_dt(entry["expires_at"])
                        + ".",
                        "__ERROR__": err,
                    },
                )
                return HTMLResponse(
                    page,
                    status_code=401,
                    headers={"X-Robots-Tag": "noindex, nofollow"},
                )
            return HTMLResponse(NOT_FOUND_HTML, status_code=404)
        with open(abs_path, encoding="utf-8") as f:
            raw = f.read()
        try:
            updated = _fmt_dt(os.path.getmtime(abs_path))
        except OSError:
            updated = "date inconnue"
        article, toc = render_article(raw, vault_root)
        minutes = reading_time_minutes(raw)
        toc_block = ""
        if toc and count_h2(article) >= 3:
            toc_block = (
                '<details class="toc"><summary>Sommaire</summary>'
                + toc
                + "</details>"
            )
        title = html.escape(entry["title"], quote=True)
        expiry = _fmt_dt(entry["expires_at"])
        page = _fill(
            PAGE_HTML,
            {
                "__TITLE__": title,
                "__READTIME__": f"Lecture {minutes} min",
                "__META__": f"Mis a jour le {updated} | Lecture {minutes} min"
                f" | Expire le {expiry}",
                "__TOC__": toc_block,
                "__CONTENT__": article,
                "__EXPIRY__": f"Expire le {expiry}.",
                "__PRINTONLY__": f"{title} - /s/{token} - Imprime le "
                + datetime.now().strftime("%d/%m/%Y"),
                "__PYGMENTS__": PYGMENTS_CSS,
            },
        )
        record_view(store, token)
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
