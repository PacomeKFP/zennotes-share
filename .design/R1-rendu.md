# R1 - Pipeline de rendu markdown (zennotes-share)

Contexte : `src/zennotes_share/render.py` utilise `extra + codehilite + toc + sane_lists` puis `bleach`. Cible : tableaux, cases a cocher, code colore, maths KaTeX, zero XSS sur page publique.

## Pipeline recommande (serveur + client)

```python
extensions = ["tables", "sane_lists", "toc", "attr_list", "md_in_html",
    "pymdownx.superfences", "pymdownx.highlight", "pymdownx.tasklist",
    "pymdownx.arithmatex", "pymdownx.inlinehilite"]
config = {
  "pymdownx.superfences": {"disable_indented_code_blocks": True},
  "pymdownx.highlight": {"guess_lang": False, "pygments_lang_class": True,
      "use_pygments": True, "linenums": False},
  "pymdownx.tasklist": {"custom_checkbox": True},
  "pymdownx.arithmatex": {"generic": True, "smart_dollar": True},
  "toc": {"slugify": "pymdownx.slugs.slugify"},
}
html = markdown.markdown(text, extensions=extensions, extension_configs=config)
html = bleach.clean(html, tags=ALLOWED, attributes=ATTRS, strip=True)
# Client : KaTeX auto-render sur le HTML assaini, jamais de renderToString serveur.
```

## Recommandations actionnables

1. Epingler : `Markdown>=3.7`, `pymdown-extensions==11.0.2`, `Pygments>=2.19,<2.21`, `bleach>=6.1`, `KaTeX>=0.16.21` (CVE-2025-23207 sur `\htmlData`, fix a partir de 0.16.21).
2. Remplacer `extra + codehilite` par `pymdownx.superfences + pymdownx.highlight + pymdownx.inlinehilite` : `codehilite` est en maintenance, `highlight` est l'alternative active recommandee par Python-Markdown.
3. Activer `pymdownx.tasklist` avec `custom_checkbox: True` pour des cases GFM (`- [ ]`, `- [x]`) : ajouter `label` a `ALLOWED_TAGS` et `class` sur `label, li, ul`, sinon bleach casse le markup.
4. Activer `pymdownx.arithmatex` en `generic: True` : sort des `<span class="arithmatex">\(...\)</span>` et `<div class="arithmatex">\[...\]</div>` au lieu de `<script type="math/tex">` que bleach detruit.
5. Whitelister bleach minimal pour les maths : `span, div, pre` + attribut `class` sur `span, div, pre, code`. Ne jamais autoriser `script`, `style`, `on*`, ni `MathML/SVG` sauf si rendu KaTeX serveur (a eviter).
6. Configurer KaTeX auto-render dans cet ordre exact : `$$` display, puis `$` inline, puis `\( \)` et `\[ \]` : mettre `$` avant `$$` capture `$$` comme expression vide.
7. Garder `smart_dollar: True` et documenter que `$2.50 et $3` ne rend pas de maths (espace et chiffre colles exiges) : c'est voulu contre les faux positifs monetaire.
8. Choisir Pygments serveur par defaut (`use_pygments: True`, `guess_lang: False`, CSS genere par `HtmlFormatter().get_style_defs(".highlight")`) : premier affichage immediat, zero JS, HTML copiable.
9. Ne jamais cumuler Pygments + highlight.js : double coloration, flash, mauvaise detection auto (bug connu type Python detecte Kotlin). Si highlight.js : `use_pygments: False`, `hljs.highlightAll()`, et CSS hljs seul.
10. Figer la securite KaTeX : `trust: false`, `throwOnError: false`, `strict: "warn"`, CDN avec SRI + `crossorigin`, `defer` sur `katex.min.js` puis `auto-render.min.js`, appel sur `DOMContentLoaded`.
11. Eviter `pymdownx.b64` et `pymdownx.snippets` sur contenu non fiable (fuites de fichiers CVE-2026-61632 et CVE-2026-46338) et exiger `pymdown-extensions>=11.0.1` (fix ReDoS CVE-2026-67422 sur caret/tilde/betterem/magiclink).
12. Tester aux bornes : `$$` multiligne, `$` dans bloc `code` (auto-render ignore `pre/code`, OK), tableau + `attr_list` (`th,td[align]` deja OK), frontmatter, wikilinks, gros bloc de code inconnu (doit rester neutre si `guess_lang: False`).

Pieges verifies : pygments 2.20 casse superfences (rester <2.21), `toc` sans slugify genere des ids instables, `md_in_html` utile mais augmente la surface bleach a auditer.
