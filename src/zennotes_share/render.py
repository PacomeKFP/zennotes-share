"""Rendu markdown -> HTML assaini pour les pages publiques."""

from __future__ import annotations

import os
import re

import bleach
import markdown

ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS) | {
    "h1", "h2", "h3", "h4", "h5", "h6",
    "pre", "img", "table", "thead", "tbody", "tr", "th", "td",
    "hr", "div", "span", "input",
}
ALLOWED_ATTRS = {
    "a": ["href", "title"],
    "img": ["src", "alt", "title"],
    "code": ["class"],
    "pre": ["class"],
    "span": ["class"],
    "div": ["class"],
    "input": ["type", "checked", "disabled"],
    "th": ["align"],
    "td": ["align"],
}

FRONTMATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)
WIKILINK_EMBED_RE = re.compile(r"!\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1)


def _asset_exists(vault_root: str, target: str) -> bool:
    target = target.strip().replace("\\", "/").lstrip("/")
    if not target or ".." in target.split("/"):
        return False
    return os.path.isfile(os.path.join(vault_root, target))


def resolve_wikilinks(text: str, vault_root: str) -> str:
    """![[x]] -> image locale si asset connu sinon texte. [[y]] -> gras."""

    def _embed(m: re.Match) -> str:
        target = m.group(1).strip()
        if _asset_exists(vault_root, target):
            return f"![](./a/{target})"
        return m.group(1).strip().rsplit("/", 1)[-1]

    def _link(m: re.Match) -> str:
        label = (m.group(2) or m.group(1)).strip()
        return f"**{label}**"

    text = WIKILINK_EMBED_RE.sub(_embed, text)
    return WIKILINK_RE.sub(_link, text)


def rewrite_relative_images(html: str) -> str:
    """Reecrit src="assets/..." vers ./a/assets/... (laisse http et ./a)."""

    def _rw(m: re.Match) -> str:
        src = m.group(1)
        if src.startswith(("http://", "https://", "./a/", "data:", "#")):
            return m.group(0)
        return f'src="./a/{src.lstrip("/")}"'

    return re.sub(r'src="([^"]+)"', _rw, html)


def render_markdown(text: str, vault_root: str) -> str:
    body = resolve_wikilinks(strip_frontmatter(text), vault_root)
    html = markdown.markdown(
        body, extensions=["extra", "codehilite", "toc", "sane_lists"]
    )
    html = rewrite_relative_images(html)
    return bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)
