"""Tests de la logique pure (sans Modal, sans reseau). Usage : python tests/test_links.py."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from zennotes_share import links
from zennotes_share import render

passed = []


def check(name, cond):
    assert cond, f"ECHEC: {name}"
    passed.append(name)


# --- liens ---
store = {}
c = links.create_link(store, "quick/ma-note.md", ttl_hours=24, max_views=2, password="s3cret")
check("creation", c["token"] in store and c["views"] == 0)
check("titre defaut", c["title"] == "ma-note.md")

ok, reason = links.check_link(store[c["token"]])
check("verrou sans mot de passe", (not ok) and reason == "locked")
ok, reason = links.check_link(store[c["token"]], password="mauvais")
check("mauvais mot de passe", (not ok) and reason == "locked")
ok, reason = links.check_link(store[c["token"]], password="s3cret")
check("bon mot de passe", ok and reason == "ok")

links.record_view(store, c["token"])
links.record_view(store, c["token"])
ok, reason = links.check_link(store[c["token"]], password="s3cret")
check("quota epuise", (not ok) and reason == "exhausted")

c2 = links.create_link(store, "inbox/x.md", ttl_hours=1)
ok, _ = links.check_link(store[c2["token"]], now=c2["expires_at"] + 1)
check("expiration", not ok)
ok, _ = links.check_link(store[c2["token"]], now=c2["expires_at"] - 1)
check("avant expiration", ok)

for bad in ["", "../secret.md", "a/../../b.md", "/absolu/../x.md"]:
    try:
        links.normalize_path(bad)
        check(f"traversee refusee {bad!r}", False)
    except ValueError:
        passed.append(f"traversee refusee {bad!r}")
check("normalisation", links.normalize_path("/quick//a.md") == "quick/a.md")

try:
    links.create_link({}, "x.md", ttl_hours=0)
    check("ttl bas refuse", False)
except ValueError:
    passed.append("ttl bas refuse")
try:
    links.create_link({}, "x.md", ttl_hours=721)
    check("ttl haut refuse", False)
except ValueError:
    passed.append("ttl haut refuse")
try:
    links.create_link({}, "x.md", max_views=0)
    check("vues refuse", False)
except ValueError:
    passed.append("vues refuse")

check("revocation", links.revoke(store, c["token"]) and c["token"] not in store)
check("revocation idempotente", links.revoke(store, "nope") is False)
check("liste triee", isinstance(links.list_links(store), list))

# --- rendu ---
check("frontmatter", render.strip_frontmatter("---\ntags: [a]\n---\n# T\ncorps") == "# T\ncorps")
check("wikilink", render.resolve_wikilinks("voir [[ma note]]", "/nimporte") == "voir **ma note**")
check(
    "wikilink alias",
    render.resolve_wikilinks("voir [[ma note|ici]]", "/x") == "voir **ici**",
)
html = render.render_markdown("# Titre\n\n<script>alert(1)</script>\n\n- [ ] tache", "/x")
check("pas de script", "<script" not in html)
check("titre rendu", "<h1" in html and "Titre" in html)
# tasklist custom emet <li class="..."> au lieu de <li> : assoupli en "<li".
check("liste rendue", "<li" in html)
check(
    "liste simple garde des li nus",
    "<li>" in render.render_markdown("- simple\n", "/x"),
)
check(
    "paragraphes conserves",
    "<p>" in render.render_markdown("simple texte", "/x"),
)
check(
    "prix non rendu en maths",
    "$2.50" in render.render_markdown("prix $2.50 ici", "/x"),
)
check(
    "dollar en code intact",
    "$x" in render.render_markdown("voici `$x` fin", "/x"),
)
check(
    "bornes display multiligne lisibles",
    "mc^2" in render.render_markdown("$$\nE = mc^2\n$$\n", "/x"),
)
aligned = render.render_markdown("| a | b |\n|:--|--:|\n| 1 | 2 |\n", "/x")
check("tableau rendu", "<table" in aligned and "table-scroll" in aligned)

print(f"OK: {len(passed)} assertions")
