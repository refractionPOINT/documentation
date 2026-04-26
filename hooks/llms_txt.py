"""MkDocs hook: write a llmstxt.org-style index to <site>/llms.txt at build time.

Wired in via `hooks:` in mkdocs.yml. The generated file is purely derived from
mkdocs.yml's nav and each page's first H1, so it is never committed to git.
"""
from __future__ import annotations

import re
from pathlib import Path


def _first_h1(md_path: Path) -> str | None:
    if not md_path.exists():
        return None
    with md_path.open(encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^#\s+(.+?)\s*$", line)
            if m:
                return m.group(1).strip()
    return None


def _page_url(site_url: str, md_rel: str) -> str:
    base = site_url.rstrip("/")
    if md_rel == "index.md":
        path = ""
    elif md_rel.endswith("/index.md"):
        path = md_rel[: -len("index.md")]
    elif md_rel.endswith(".md"):
        path = md_rel[: -len(".md")] + "/"
    else:
        path = md_rel
    return f"{base}/{path}"


def _walk(node, out: list[tuple[str, str]]) -> None:
    """Collect (label, md_rel) leaves from a raw mkdocs nav structure."""
    if isinstance(node, list):
        for item in node:
            _walk(item, out)
    elif isinstance(node, dict):
        for label, value in node.items():
            if isinstance(value, str):
                out.append((label, value))
            else:
                _walk(value, out)


def render(site_name: str, site_url: str, site_description: str, nav: list, docs_dir: Path) -> str:
    lines: list[str] = [f"# {site_name}", ""]
    if site_description:
        lines += [f"> {site_description}", ""]
    lines += [
        "This file is a machine-readable index of the documentation, "
        "intended for LLMs and other automated consumers. "
        "Each link points to a single documentation page.",
        "",
    ]

    for entry in nav or []:
        if not isinstance(entry, dict):
            continue
        for section_label, section_value in entry.items():
            if isinstance(section_value, str):
                if "## Pages" not in lines:
                    lines += ["## Pages", ""]
                title = _first_h1(docs_dir / section_value) or section_label
                url = _page_url(site_url, section_value)
                lines.append(f"- [{title}]({url}): {section_label}")
                continue

            leaves: list[tuple[str, str]] = []
            _walk(section_value, leaves)
            if not leaves:
                continue
            lines += [f"## {section_label}", ""]
            for label, md_rel in leaves:
                title = _first_h1(docs_dir / md_rel) or label
                url = _page_url(site_url, md_rel)
                if title.lower() == label.lower():
                    lines.append(f"- [{label}]({url})")
                else:
                    lines.append(f"- [{label}]({url}): {title}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def on_post_build(config, **_kwargs):
    """MkDocs entry point — runs after the site is built."""
    docs_dir = Path(config["docs_dir"])
    site_dir = Path(config["site_dir"])

    # mkdocs config exposes the parsed nav under 'nav' as the raw YAML structure
    # (a list of dicts/strings). The Navigation object lives elsewhere; we want
    # the raw form so we can preserve labels.
    nav = config.get("nav") or []

    content = render(
        site_name=config.get("site_name", "Documentation"),
        site_url=config.get("site_url", ""),
        site_description=config.get("site_description", ""),
        nav=nav,
        docs_dir=docs_dir,
    )

    out = site_dir / "llms.txt"
    out.write_text(content, encoding="utf-8")
    print(f"  llms.txt: wrote {out} ({out.stat().st_size} bytes)")
