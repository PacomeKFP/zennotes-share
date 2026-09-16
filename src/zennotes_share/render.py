"""Rendu markdown -> HTML assaini pour les pages publiques.

Pipeline : frontmatter et wikilinks resolus AVANT markdown, conversion
avec pymdown-extensions (superfences, highlight Pygments, tasklist,
arithmatex generique, inlinehilite, tables, toc), assainissement bleach
strict, puis enrichissements post-sanitization (tableaux scrollables,
images lazy avec legende, callouts, code clavier).
"""

from __future__ import annotations

import os
import re

import bleach
import markdown
from urllib.parse import quote
from pygments.formatters import HtmlFormatter
from pymdownx import slugs

ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS) | {
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "br",
    "pre", "img", "table", "thead", "tbody", "tr", "th", "td",
    "hr", "div", "span", "label", "input",
}
ALLOWED_ATTRS = {
    "a": ["href", "title"],
    "img": ["src", "alt", "title", "loading"],
    "code": ["class"],
    "pre": ["class"],
    "span": ["class"],
    "div": ["class"],
    "li": ["class"],
    "ul": ["class"],
    "ol": ["class"],
    "label": ["class"],
    "input": ["type", "checked", "disabled"],
    "th": ["align"],
    "td": ["align"],
    "h1": ["id"],
    "h2": ["id"],
    "h3": ["id"],
    "h4": ["id"],
    "h5": ["id"],
    "h6": ["id"],
}

FRONTMATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)
WIKILINK_EMBED_RE = re.compile(r"!\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
H2_RE = re.compile(r"<h2[\s>]")
TABLE_OPEN_RE = re.compile(r"<table(\s[^>]*)?>")
PRE_OPEN_RE = re.compile(r"<pre(\s[^>]*)?>")
IMG_RE = re.compile(r"<img\b[^>]*>")
BLOCKQUOTE_RE = re.compile(r"<blockquote>(.*?)</blockquote>", re.DOTALL)
CALLOUT_MARK_RE = re.compile(
    r"\A\s*(?:<p>)?\s*\[!\s*(INFO|NOTE|ATTENTION|WARNING|ASTUCE|TIP)\s*\]",
    re.IGNORECASE,
)
CALLOUT_KIND = {
    "INFO": ("info", "Info"),
    "NOTE": ("info", "Info"),
    "ATTENTION": ("attention", "Attention"),
    "WARNING": ("attention", "Attention"),
    "ASTUCE": ("astuce", "Astuce"),
    "TIP": ("astuce", "Astuce"),
}
MAX_CALLOUTS = 3

_MD_EXTENSIONS = [
    "tables",
    "sane_lists",
    "toc",
    "attr_list",
    "md_in_html",
    "pymdownx.superfences",
    "pymdownx.highlight",
    "pymdownx.tasklist",
    "pymdownx.arithmatex",
    "pymdownx.inlinehilite",
]
_MD_CONFIGS = {
    "pymdownx.superfences": {"disable_indented_code_blocks": True},
    "pymdownx.highlight": {"use_pygments": True, "guess_lang": False},
    "pymdownx.tasklist": {"custom_checkbox": True},
    "pymdownx.arithmatex": {"generic": True, "smart_dollar": True},
    "toc": {"slugify": slugs.slugify(case="lower")},
}


def _pygments_css() -> str:
    light = HtmlFormatter(style="default").get_style_defs(".highlight")
    scoped = (
        "@media (prefers-color-scheme: dark) {\n"
        ".highlight pre, .highlight code, div.highlight {\n"
        "background: var(--code-bg);\ncolor: var(--fg);\n}\n}\n"
        'html[data-theme="dark"] .highlight pre,\n'
        'html[data-theme="dark"] .highlight code,\n'
        'html[data-theme="dark"] div.highlight {\n'
        "background: var(--code-bg);\ncolor: var(--fg);\n}\n"
    )
    return light + "\n" + scoped


PYGMENTS_CSS = _pygments_css()


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1)


def _asset_exists(vault_root: str, target: str) -> bool:
    target = target.strip().replace("\\", "/").lstrip("/")
    if not target or ".." in target.split("/"):
        return False
    return os.path.isfile(os.path.join(vault_root, target))


def _asset_url(target: str, token: str | None) -> str:
    target = target.strip().replace("\\", "/").lstrip("/")
    if token:
        quoted = "/".join(quote(seg) for seg in target.split("/"))
        return f"/s/{token}/a/{quoted}"
    return f"./a/{target}"


def resolve_wikilinks(
    text: str, vault_root: str, token: str | None = None
) -> str:
    """![[x]] -> image locale si asset connu sinon texte. [[y]] -> gras."""

    def _embed(m: re.Match) -> str:
        target = m.group(1).strip()
        if _asset_exists(vault_root, target):
            alt = target.rsplit("/", 1)[-1]
            return f"![{alt}]({_asset_url(target, token)})"
        return m.group(1).strip().rsplit("/", 1)[-1]

    def _link(m: re.Match) -> str:
        label = (m.group(2) or m.group(1)).strip()
        return f"**{label}**"

    text = WIKILINK_EMBED_RE.sub(_embed, text)
    return WIKILINK_RE.sub(_link, text)


def rewrite_relative_images(html: str, token: str | None = None) -> str:
    """Reecrit src="assets/..." vers l'URL absolue du lien (laisse http et /s/)."""

    def _rw(m: re.Match) -> str:
        src = m.group(1)
        if src.startswith(("http://", "https://", "/s/", "data:", "#")):
            return m.group(0)
        if src.startswith("./a/"):
            src = src[len("./a/"):]
        base = f"/s/{token}/a/" if token else "./a/"
        return f'src="{base + quote(src.lstrip("/"), safe="/%")}"'

    return re.sub(r'src="([^"]+)"', _rw, html)


def _external_new_tab(html: str) -> str:
    """Les liens externes s'ouvrent dans un nouvel onglet securise."""

    def _rw(m: re.Match) -> str:
        return f'<a href="{m.group(1)}"{m.group(2)} target="_blank" rel="noopener">'

    return re.sub(r'<a href="(https?://[^"]+)"((?: title="[^"]*")?)>', _rw, html)


def reading_time_minutes(text: str) -> int:
    """Duree de lecture estimee, 200 mots par minute, 1 minute minimum."""
    plain = strip_frontmatter(text)
    words = len(re.findall(r"\w+", plain))
    return max(1, round(words / 200))


def _sanitize(html: str) -> str:
    return bleach.clean(
        html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True
    )


def _wrap_tables(html: str) -> str:
    """Enveloppe chaque table pour le scroll-x interne accessible au clavier."""
    html = TABLE_OPEN_RE.sub(
        r'<div class="table-scroll" tabindex="0"><table\1>', html
    )
    return html.replace("</table>", "</table></div>")


def _enhance_images(html: str) -> str:
    """Ajoute loading lazy, encapsule en figure avec legende si title."""

    def _one(m: re.Match) -> str:
        tag = m.group(0)
        if "loading=" not in tag:
            tag = tag.replace("<img", '<img loading="lazy"', 1)
        title_m = re.search(r'title="([^"]*)"', tag)
        if title_m and title_m.group(1).strip():
            caption = (
                title_m.group(1)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            return (
                '<figure class="img-wrap">'
                + tag
                + "<figcaption>"
                + caption
                + "</figcaption></figure>"
            )
        return tag

    return IMG_RE.sub(_one, html)


def _enhance_pres(html: str) -> str:
    """Rend les blocs de code atteignables au clavier (scroll-x)."""

    def _one(m: re.Match) -> str:
        attrs = m.group(1) or ""
        if "tabindex" in attrs:
            return m.group(0)
        return f"<pre tabindex=\"0\"{attrs}>"

    return PRE_OPEN_RE.sub(_one, html)


def _callouts(html: str) -> str:
    """Convertit les 3 premiers blockquotes [!INFO] etc. en callouts."""
    converted = 0

    def _one(m: re.Match) -> str:
        nonlocal converted
        inner = m.group(1)
        if converted >= MAX_CALLOUTS:
            return m.group(0)
        mark = CALLOUT_MARK_RE.match(inner)
        if not mark:
            return m.group(0)
        kind, label = CALLOUT_KIND[mark.group(1).upper()]
        converted += 1
        body = CALLOUT_MARK_RE.sub("", inner, count=1)
        body = re.sub(r"\A\s*<p>", "<p>", body)
        return (
            f'<div class="callout {kind}">'
            f'<p class="callout-title">{label}</p>'
            + body
            + "</div>"
        )

    return BLOCKQUOTE_RE.sub(_one, html)


def count_h2(html: str) -> int:
    return len(H2_RE.findall(html))


def _convert(
    text: str, vault_root: str, token: str | None = None
) -> tuple[str, str]:
    """Convertit le markdown, retourne (corps HTML brut, sommaire brut)."""
    body = resolve_wikilinks(strip_frontmatter(text), vault_root, token)
    md = markdown.Markdown(
        extensions=_MD_EXTENSIONS, extension_configs=_MD_CONFIGS
    )
    raw_html = md.convert(body)
    raw_html = rewrite_relative_images(raw_html, token)
    toc_html = md.toc or ""
    if "<a " not in toc_html:
        toc_html = ""
    return raw_html, toc_html


def render_article(
    text: str, vault_root: str, token: str | None = None
) -> tuple[str, str]:
    """Rend (article assaini et enrichi, sommaire assaini)."""
    raw_html, raw_toc = _convert(text, vault_root, token)
    article = _sanitize(raw_html)
    article = _external_new_tab(article)
    article = _callouts(article)
    article = _wrap_tables(article)
    article = _enhance_images(article)
    article = _enhance_pres(article)
    toc = _sanitize(raw_toc) if raw_toc else ""
    return article, toc


def render_markdown(
    text: str, vault_root: str, token: str | None = None
) -> str:
    """Compatibilite : rend le corps HTML seul (sans le sommaire)."""
    article, _ = render_article(text, vault_root, token)
    return article
