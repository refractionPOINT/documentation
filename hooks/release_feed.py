"""MkDocs hook: publish RSS and JSON feeds for the release notes at build time.

Wired in via `hooks:` in mkdocs.yml. Everything it writes is derived from
`docs/10-release-notes/`, so no feed file is ever committed to git.

What it produces
----------------
Into `<site>/10-release-notes/`:

* `feed.xml`             - RSS 2.0, every release entry
* `feed.json`            - JSON Feed 1.1, every release entry
* `<component>.xml`      - RSS 2.0, one per component that has at least one
                           entry (`endpoint-agent.xml`, `web-app.xml`, ...)
* `breaking-changes.xml` - RSS 2.0, only entries carrying a "Breaking Changes"
                           or "Schema Changes" section

Source shape
------------
The release notes are one page of stacked entries, not one page per release:

    ## 2026-08-11                 <- date group (YYYY-MM-DD)
    ### Endpoint Agent 5.3.5      <- one feed item
    #### New Features             <- body
    #### Breaking Changes         <- marks the item as breaking

Item bodies are taken from the RENDERED HTML (via `on_page_content`) rather
than re-rendered from Markdown, which means the anchors in feed links are the
exact ids MkDocs put on the page - they cannot drift.

Identity and why links are not identities
-----------------------------------------
A feed reader dedupes on `<guid>`. Anchors are NOT usable as identities here:
Python-Markdown disambiguates two headings with the same text by appending
`_1`, `_2` in DOCUMENT order, and new entries are prepended at the top of the
page, so adding a second `### Endpoint Agent` would renumber the older one and
re-notify every subscriber. Items therefore carry a synthetic, position-free
`tag:` URI built from (date, heading text):

    tag:docs.limacharlie.io,2026-08-11:release/endpoint-agent-5-3-5

`guid_slug` is part of that contract - changing how it slugifies re-notifies
every subscriber, so it must not be "improved". Editing an existing heading has
the same effect; fix typos in the body instead where possible.
`scripts/check-release-note-headings.py` enforces that new headings are
unique-by-slug, which keeps anchors stable as a side effect.

Component normalization
-----------------------
Historical headings name the same component several ways ("EDR Sensor", "EDR
Agent", "Endpoint Agent"). `COMPONENTS` maps every spelling onto one canonical
slug so `endpoint-agent.xml` carries the whole history, without editing a
single historical heading (which would break existing deep links). New entries
are held to the canonical spelling by the heading lint, not by this hook.

Where feed links point
----------------------
The subscribe callout on the page and the footer icon in mkdocs.yml spell their
feed URLs out in full, because a relative link to a generated file does not
survive `strict: true` (the file does not exist when links are validated). On
any build whose site_url is not production - a `mkdocs serve` preview above all
- `on_config` and `on_page_markdown` retarget that base at the build's own, so
a local preview links to its own feeds instead of 404ing against production. A
production build changes nothing.

Failure behavior
----------------
A structural regression (the page renders but yields no entries, a `###`
outside any date group, two entries colliding on one guid) raises and fails the
build. Under `strict: true` that is the point: an empty or duplicated feed is
worse than a red build. A build that never rendered the release notes page at
all - `mkdocs serve --dirtyreload` after editing an unrelated page - is not an
error; the feeds are simply left alone.

Cost: one regex pass over a ~60 KB page plus ~90 KB of XML written at
`on_post_build`. Negligible against a full site build.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from xml.sax.saxutils import escape as xml_escape

try:  # MkDocs is absent when the parsing helpers are imported by tests/scripts.
    from mkdocs.exceptions import PluginError
except ImportError:  # pragma: no cover - exercised only outside a MkDocs build
    class PluginError(Exception):
        """Stand-in so this module stays importable without MkDocs installed."""


log = logging.getLogger("mkdocs.hooks.release_feed")

# Source directory (relative to docs_dir) and the page that holds the entries.
RELEASE_NOTES_DIR = "10-release-notes"
RELEASE_NOTES_SRC = f"{RELEASE_NOTES_DIR}/index.md"

# Feed URLs are written out in full in the documentation source and in
# mkdocs.yml, because a relative link to a generated (non-page) file does not
# survive MkDocs' strict link validation - the file does not exist until the
# build has already finished. On any build that is not production (a
# `mkdocs serve` preview, a fork with a different site_url) this base is
# rewritten to the one the build actually serves from, so the links resolve
# where the reader is rather than 404ing against production.
CANONICAL_FEED_BASE = "https://docs.limacharlie.io/10-release-notes/"

# A date group heading: "## 2026-08-11".
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Trailing version on an entry heading. Accepts "5.3.5", "v3.8.10" and the
# occasional dual release ("4.33.13 and 4.33.10.3").
VERSION_RE = re.compile(
    r"^(?P<name>.+?)\s+(?P<version>v?\d[\d.]*(?:\s+and\s+v?\d[\d.]*)*)\s*$"
)

# Sections that mark an entry as breaking for the dedicated feed.
BREAKING_HEADINGS = ("breaking changes", "schema changes")


@dataclass(frozen=True)
class Component:
    """One canonical component that readers can subscribe to on its own.

    `aliases` are normalized spellings (see `normalize_name`) that have been
    used in a heading at some point. They exist so historical entries land in
    the right feed without rewriting the headings that anchors are built from.
    """

    slug: str
    name: str
    description: str
    aliases: tuple[str, ...] = ()


# Catch-all for cross-cutting announcements that do not name a component
# ("New MITRE Report API", "LimaCharlie Labs").
PLATFORM_SLUG = "platform"

COMPONENTS: tuple[Component, ...] = (
    Component(
        slug="endpoint-agent",
        name="Endpoint Agent",
        description="Releases of the LimaCharlie endpoint agent (EDR sensor).",
        aliases=(
            "endpoint agent",
            "edr endpoint agent",
            "edr agent",
            "edr sensor",
            "endpoint sensor",
            "sensor",
        ),
    ),
    Component(
        slug="web-app",
        name="Web App",
        description="Releases of the LimaCharlie web application.",
        aliases=("web app", "webapp", "web application"),
    ),
    Component(
        slug="adapters",
        name="Adapters",
        description="Releases of the LimaCharlie adapters (USP).",
        aliases=("adapters", "adapter", "lc adapters", "lc adapter", "usp adapters"),
    ),
    Component(
        slug="extensions",
        name="Extensions",
        description="Releases of LimaCharlie extensions.",
        aliases=("extensions", "extension", "add ons", "addons"),
    ),
    Component(
        slug="cli",
        name="CLI",
        description="Releases of the LimaCharlie command line interface.",
        aliases=("cli", "limacharlie cli"),
    ),
    Component(
        slug="sdk",
        name="SDKs",
        description="Releases of the LimaCharlie SDKs.",
        aliases=("sdk", "sdks", "python sdk", "go sdk"),
    ),
    Component(
        slug=PLATFORM_SLUG,
        name="Platform",
        description="Platform announcements that are not tied to one component.",
        aliases=("platform",),
    ),
)

COMPONENTS_BY_SLUG = {c.slug: c for c in COMPONENTS}

# Headings that legitimately name more than one component. Keys are normalized
# spellings, values are canonical slugs.
MULTI_COMPONENT_ALIASES: dict[str, tuple[str, ...]] = {
    "extensions and adapters": ("extensions", "adapters"),
    "add ons and adapters": ("extensions", "adapters"),
    "add ons and extensions": ("extensions",),
    "cli and sdk": ("cli", "sdk"),
    "cli and sdks": ("cli", "sdk"),
}


def _build_alias_index() -> dict[str, tuple[str, ...]]:
    index: dict[str, tuple[str, ...]] = {}
    for component in COMPONENTS:
        for alias in component.aliases:
            if alias in index:
                raise ValueError(f"duplicate component alias: {alias!r}")
            index[alias] = (component.slug,)
    for alias, slugs in MULTI_COMPONENT_ALIASES.items():
        if alias in index:
            raise ValueError(f"duplicate component alias: {alias!r}")
        index[alias] = slugs
    return index


ALIAS_INDEX = _build_alias_index()


def normalize_name(text: str) -> str:
    """Fold a heading's component part to the key used in `ALIAS_INDEX`.

    Lowercases and reduces every run of non-alphanumerics to one space, so
    "Add-Ons and Adapters", "add ons and adapters" and "ADD_ONS AND ADAPTERS"
    all collapse to the same key.
    """
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def guid_slug(text: str) -> str:
    """Slugify for guid construction. Stable by contract - see module docstring.

    Deliberately independent of Python-Markdown's `toc` slugify: this feeds
    identities, not links, and must never change even if the theme's anchor
    scheme does.
    """
    return re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")


@dataclass(frozen=True)
class Heading:
    """The parsed form of a `### ...` release entry heading."""

    title: str
    name: str
    version: str | None
    components: tuple[str, ...]
    announcement: str | None = None

    @property
    def primary_component(self) -> str:
        return self.components[0]

    @property
    def is_canonical(self) -> bool:
        """True when the heading follows one of the two supported forms.

        A versioned release:      `### Endpoint Agent 5.3.5`
        A versionless announcement: `### Platform: New MITRE Report API`

        `Platform` is the catch-all bucket for cross-cutting news, so it can
        only head the announcement form - there is no such thing as a Platform
        version. The heading lint holds new entries to these forms; historical
        entries that predate the convention are grandfathered by a baseline.
        """
        if len(self.components) != 1:
            return False
        component = COMPONENTS_BY_SLUG.get(self.components[0])
        if component is None or self.name != component.name:
            return False
        if self.announcement:
            return True
        return self.version is not None and component.slug != PLATFORM_SLUG


def classify_heading(title: str) -> Heading:
    """Split an entry heading into component(s), version and announcement text.

    Falls back to the `platform` component for one-off announcements that name
    a feature rather than a component ("New MITRE Report API"), so nothing is
    ever dropped from the all-entries feed.
    """
    title = title.strip()
    announcement = None
    match = VERSION_RE.match(title)
    if match:
        name = match.group("name").strip()
        version = match.group("version").strip()
    elif ": " in title:
        name, _, rest = title.partition(": ")
        name, version = name.strip(), None
        announcement = rest.strip() or None
    else:
        name = title
        version = None

    key = normalize_name(name)
    components = ALIAS_INDEX.get(key)
    if components is None and key.startswith("ext "):
        # Extension entries are titled by their extension id ("ext-usage-alerts").
        components = ("extensions",)
    if components is None:
        components = (PLATFORM_SLUG,)
    return Heading(
        title=title,
        name=name,
        version=version,
        components=components,
        announcement=announcement,
    )


@dataclass
class Entry:
    """One feed item: a single `### ...` release entry."""

    date: str
    heading: Heading
    body_html: str = ""
    body_markdown: str = ""
    anchor: str = ""
    is_breaking: bool = False
    source_line: int = 0
    categories: tuple[str, ...] = field(default_factory=tuple)

    @property
    def title(self) -> str:
        return self.heading.title

    def guid(self, host: str) -> str:
        return f"tag:{host},{self.date}:release/{guid_slug(self.title)}"

    def link(self, page_url: str) -> str:
        return f"{page_url}#{self.anchor}" if self.anchor else page_url


# --------------------------------------------------------------------------
# Markdown parsing (used by the heading lint and the notifier; the hook itself
# reads the rendered HTML so its links carry MkDocs' own anchors)
# --------------------------------------------------------------------------

_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
_MD_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")

# The "---" rule that separates date groups on the page belongs to the page
# layout, not to the entry it happens to follow, so it is cut from the last
# entry of each group rather than shipped as a trailing horizontal rule.
_TRAILING_RULE_MD_RE = re.compile(r"\n\s*(?:-{3,}|\*{3,}|_{3,})\s*$")
_TRAILING_RULE_HTML_RE = re.compile(r"(?:<hr\s*/?>\s*)+$", re.IGNORECASE)


def iter_markdown_headings(text: str):
    """Yield `(level, title, line_number)` for each heading outside a code fence.

    Shared by everything that has to agree on what a heading is - the entry
    parser, the heading lint, and the publisher that inserts new entries - so a
    `## 2026-01-01` inside a fenced example is page content everywhere rather
    than a date group in one place and not another.
    """
    fence: str | None = None
    for lineno, line in enumerate(text.splitlines(), start=1):
        fence_match = _FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = marker
            elif line.strip().startswith(fence):
                fence = None
            continue
        if fence is not None:
            continue
        heading = _MD_HEADING_RE.match(line)
        if heading:
            yield len(heading.group(1)), heading.group(2), lineno


def parse_markdown_entries(text: str) -> list[Entry]:
    """Parse `docs/10-release-notes/index.md` into entries, bodies included."""
    lines = text.splitlines()
    headings = list(iter_markdown_headings(text))
    entries: list[Entry] = []
    current_date: str | None = None

    for index, (level, title, lineno) in enumerate(headings):
        if level == 2:
            current_date = title if DATE_RE.match(title) else None
            continue
        if level != 3:
            continue
        if current_date is None:
            raise PluginError(
                f"release feed: entry '{title}' on line {lineno} is not under "
                "a '## YYYY-MM-DD' date heading"
            )

        # The body runs to the next heading that closes the entry. The
        # "#### Section" headings inside it are part of the entry.
        end = len(lines)
        for next_level, _next_title, next_lineno in headings[index + 1:]:
            if next_level <= 3:
                end = next_lineno - 1
                break

        body = _TRAILING_RULE_MD_RE.sub("", "\n".join(lines[lineno:end]).strip())
        heading = classify_heading(title)
        entries.append(
            Entry(
                date=current_date,
                heading=heading,
                body_markdown=body,
                is_breaking=_markdown_is_breaking(body),
                source_line=lineno,
                categories=heading.components,
            )
        )

    return entries


def _markdown_is_breaking(body_markdown: str) -> bool:
    return any(
        level == 4 and normalize_name(title) in BREAKING_HEADINGS
        for level, title, _lineno in iter_markdown_headings(body_markdown)
    )


# --------------------------------------------------------------------------
# Rendered-HTML parsing
# --------------------------------------------------------------------------

# A rendered h2/h3 with the id MkDocs assigned to it.
_HTML_HEADING_RE = re.compile(
    r"<h(?P<level>[23])\b[^>]*\sid=\"(?P<id>[^\"]+)\"[^>]*>(?P<inner>.*?)</h(?P=level)>",
    re.DOTALL,
)
_HEADERLINK_RE = re.compile(
    r"<a\b[^>]*class=\"[^\"]*headerlink[^\"]*\"[^>]*>.*?</a>", re.DOTALL
)
_TAG_RE = re.compile(r"<[^>]+>")
_URL_ATTR_RE = re.compile(r"\b(href|src)=\"([^\"]*)\"")
_H4_RE = re.compile(r"<h4\b[^>]*>(?P<inner>.*?)</h4>", re.DOTALL)

# XML 1.0 cannot carry these code points at all - not raw, not escaped, not
# inside CDATA - so one of them reaching a body (a copy-paste artifact in a
# release note) would make the whole feed unparseable for every subscriber.
# Dropping the character costs nothing; publishing an invalid feed costs the
# entire delivery.
_INVALID_XML_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _heading_text(inner_html: str) -> str:
    """Recover a heading's plain text from its rendered markup."""
    text = _HEADERLINK_RE.sub("", inner_html)
    text = _TAG_RE.sub("", text)
    text = (
        text.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
    )
    return text.strip()


def absolutize_html_urls(fragment: str, base_url: str) -> str:
    """Rewrite every href/src in a body fragment to an absolute URL.

    Feed readers render items detached from the page, so MkDocs' relative links
    ("../2-sensors-deployment/asset-tags/") and bare fragments ("#foo") resolve
    against the reader's own origin unless they are absolutized here.
    """

    def replace(match: re.Match[str]) -> str:
        attr, value = match.group(1), match.group(2)
        if not value:
            return match.group(0)
        return f'{attr}="{urljoin(base_url, value)}"'

    return _URL_ATTR_RE.sub(replace, fragment)


_MD_INLINE_DEST_RE = re.compile(r"(\]\(\s*<?)([^)\s>]+)")
_MD_REF_DEST_RE = re.compile(r"(?m)^([ \t]{0,3}\[[^\]]+\]:\s*<?)([^\s>]+)")


def _markdown_dest_to_url(dest: str, base_url: str) -> str:
    """Resolve one Markdown link destination to an absolute documentation URL.

    Source links point at `.md` files ("../2-sensors-deployment/asset-tags.md");
    the published site serves them as directory URLs, which is what MkDocs
    rewrites them to at render time and what a reader outside the site needs.
    """
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]*:", dest) or dest.startswith("//"):
        return dest
    path, sep, fragment = dest.partition("#")
    if path.endswith("/index.md"):
        path = path[: -len("index.md")]
    elif path.endswith(".md"):
        path = path[: -len(".md")] + "/"
    return urljoin(base_url, path + sep + fragment)


def absolutize_markdown_links(text: str, base_url: str) -> str:
    """Absolutize every link destination in a Markdown body.

    Used when a release note body is republished off-site (the community forum
    post), where a relative `.md` path resolves to nothing.
    """

    def replace(match: re.Match[str]) -> str:
        return match.group(1) + _markdown_dest_to_url(match.group(2), base_url)

    text = _MD_INLINE_DEST_RE.sub(replace, text)
    return _MD_REF_DEST_RE.sub(replace, text)


def _html_is_breaking(body_html: str) -> bool:
    for match in _H4_RE.finditer(body_html):
        if normalize_name(_heading_text(match.group("inner"))) in BREAKING_HEADINGS:
            return True
    return False


def extract_html_entries(page_html: str, base_url: str) -> list[Entry]:
    """Build entries from a rendered release-notes page.

    The body of an entry is every byte between its `</h3>` and the next h2/h3,
    with the theme's `¶` permalinks stripped and all URLs absolutized.
    """
    entries: list[Entry] = []
    current_date: str | None = None
    matches = list(_HTML_HEADING_RE.finditer(page_html))

    for index, match in enumerate(matches):
        title = _heading_text(match.group("inner"))
        if match.group("level") == "2":
            current_date = title if DATE_RE.match(title) else None
            continue

        if current_date is None:
            raise PluginError(
                f"release feed: rendered entry '{title}' is not under a date heading"
            )

        end = matches[index + 1].start() if index + 1 < len(matches) else len(page_html)
        body = page_html[match.end():end]
        body = _HEADERLINK_RE.sub("", body)
        body = _INVALID_XML_CHARS_RE.sub("", body)
        body = absolutize_html_urls(body, base_url).strip()
        body = _TRAILING_RULE_HTML_RE.sub("", body).strip()

        heading = classify_heading(title)
        entries.append(
            Entry(
                date=current_date,
                heading=heading,
                body_html=body,
                anchor=match.group("id"),
                is_breaking=_html_is_breaking(body),
                categories=heading.components,
            )
        )

    return entries


# --------------------------------------------------------------------------
# Feed rendering
# --------------------------------------------------------------------------

_WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
_MONTHS = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
)


def rfc822(date: str) -> str:
    """Format a YYYY-MM-DD release date as an RFC 822 timestamp at midnight UTC.

    Built by hand rather than with `strftime` so the weekday and month names
    cannot follow the build machine's locale.
    """
    day = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return (
        f"{_WEEKDAYS[day.weekday()]}, {day.day:02d} {_MONTHS[day.month - 1]} "
        f"{day.year} 00:00:00 GMT"
    )


def rfc3339(date: str) -> str:
    return f"{date}T00:00:00+00:00"


def _cdata(text: str) -> str:
    """Wrap item HTML in CDATA, splitting any literal `]]>` that would end it."""
    return "<![CDATA[" + text.replace("]]>", "]]]]><![CDATA[>") + "]]>"


def _xml_attr(value: str) -> str:
    """Escape a value for use inside a double-quoted XML attribute."""
    return xml_escape(value, {'"': "&quot;"})


def sort_entries(entries: list[Entry]) -> list[Entry]:
    """Newest first. Python's sort is stable, so same-day entries keep page order."""
    return sorted(entries, key=lambda entry: entry.date, reverse=True)


def render_rss(
    *,
    title: str,
    description: str,
    page_url: str,
    feed_url: str,
    entries: list[Entry],
    generator: str,
) -> str:
    host = urlsplit(page_url).hostname or "docs.limacharlie.io"
    entries = sort_entries(entries)
    last_build = rfc822(entries[0].date) if entries else rfc822("1970-01-01")

    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "  <channel>",
        f"    <title>{xml_escape(title)}</title>",
        f"    <link>{xml_escape(page_url)}</link>",
        f"    <description>{xml_escape(description)}</description>",
        "    <language>en</language>",
        f"    <generator>{xml_escape(generator)}</generator>",
        f"    <lastBuildDate>{last_build}</lastBuildDate>",
        f'    <atom:link href="{_xml_attr(feed_url)}" rel="self" '
        'type="application/rss+xml"/>',
    ]

    for entry in entries:
        lines += [
            "    <item>",
            f"      <title>{xml_escape(entry.title)}</title>",
            f"      <link>{xml_escape(entry.link(page_url))}</link>",
            f'      <guid isPermaLink="false">{xml_escape(entry.guid(host))}</guid>',
            f"      <pubDate>{rfc822(entry.date)}</pubDate>",
        ]
        for category in entry.categories:
            lines.append(f"      <category>{xml_escape(category)}</category>")
        if entry.is_breaking:
            lines.append("      <category>breaking-changes</category>")
        lines += [
            f"      <description>{_cdata(entry.body_html)}</description>",
            "    </item>",
        ]

    lines += ["  </channel>", "</rss>", ""]
    return "\n".join(lines)


def render_json_feed(
    *,
    title: str,
    description: str,
    page_url: str,
    feed_url: str,
    entries: list[Entry],
) -> str:
    host = urlsplit(page_url).hostname or "docs.limacharlie.io"
    entries = sort_entries(entries)
    feed = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": title,
        "description": description,
        "home_page_url": page_url,
        "feed_url": feed_url,
        "language": "en",
        "items": [
            {
                "id": entry.guid(host),
                "url": entry.link(page_url),
                "title": entry.title,
                "content_html": entry.body_html,
                "date_published": rfc3339(entry.date),
                "tags": list(entry.categories)
                + (["breaking-changes"] if entry.is_breaking else []),
            }
            for entry in entries
        ],
    }
    return json.dumps(feed, indent=2, ensure_ascii=False) + "\n"


# --------------------------------------------------------------------------
# MkDocs events
# --------------------------------------------------------------------------

_STATE: dict[str, object] = {"entries": [], "rendered": False, "feed_base": ""}


def on_config(config, **_kwargs):
    """Retarget every published feed link at the base this build serves from.

    Production is the no-op case: its site_url already is the canonical base,
    so the deployed HTML is byte-for-byte what the source says. Runs before
    anything is rendered, so both the footer social link (mkdocs.yml) and the
    in-page links (see `on_page_markdown`) are covered.
    """
    site_url = config.get("site_url") or ""
    feed_base = urljoin(site_url, f"{RELEASE_NOTES_DIR}/") if site_url else ""
    _STATE["feed_base"] = feed_base
    if not feed_base or feed_base == CANONICAL_FEED_BASE:
        return config

    for link in (config.get("extra") or {}).get("social") or []:
        url = link.get("link", "")
        if url.startswith(CANONICAL_FEED_BASE):
            link["link"] = feed_base + url[len(CANONICAL_FEED_BASE):]
    return config


def on_page_markdown(markdown, page, config, **_kwargs):
    """Retarget in-page feed links on a non-production build. See `on_config`."""
    feed_base = _STATE.get("feed_base") or ""
    if not feed_base or feed_base == CANONICAL_FEED_BASE:
        return None
    if CANONICAL_FEED_BASE not in markdown:
        return None
    return markdown.replace(CANONICAL_FEED_BASE, feed_base)


def on_pre_build(config, **_kwargs):
    """Reset per-build state (`mkdocs serve` reuses the process across builds)."""
    _STATE["entries"] = []
    _STATE["rendered"] = False


def on_page_content(html, page, config, **_kwargs):
    """Collect entries from every rendered release-notes page. Modifies nothing.

    Scoped to the whole `10-release-notes/` directory rather than just the
    canonical page, so a page added there is published rather than silently
    left out of the feeds. Links are resolved against each page's own URL.
    """
    if not page.file.src_uri.startswith(f"{RELEASE_NOTES_DIR}/"):
        return None

    site_url = config.get("site_url")
    if not site_url:
        raise PluginError("release feed: site_url must be set in mkdocs.yml")

    page_url = urljoin(site_url, page.url)
    _STATE["entries"].extend(extract_html_entries(html, page_url))
    _STATE["rendered"] = True
    return None


def on_post_build(config, **_kwargs):
    """Write every feed. Fails the build on a structural regression."""
    entries: list[Entry] = _STATE["entries"]  # type: ignore[assignment]

    if not _STATE["rendered"]:
        # A partial rebuild (`mkdocs serve --dirtyreload`) that did not touch the
        # release notes. Leaving the previous feeds in place beats writing empty ones.
        log.info("release feed: release notes page not rendered, feeds left unchanged")
        return

    if not entries:
        raise PluginError(
            f"release feed: no entries parsed from {RELEASE_NOTES_SRC}. The page "
            "structure ('## YYYY-MM-DD' then '### Component Version') has changed."
        )

    site_url = config["site_url"]
    page_url = urljoin(site_url, f"{RELEASE_NOTES_DIR}/")
    host = urlsplit(page_url).hostname or "docs.limacharlie.io"
    site_name = config.get("site_name", "LimaCharlie Documentation")
    generator = f"{site_name} release feed hook"

    seen: dict[str, Entry] = {}
    for entry in entries:
        guid = entry.guid(host)
        if guid in seen:
            raise PluginError(
                f"release feed: two entries share the guid {guid} "
                f"('{seen[guid].title}' and '{entry.title}'). Two entries with the "
                "same heading on the same date cannot be told apart by a reader."
            )
        seen[guid] = entry

    out_dir = Path(config["site_dir"]) / RELEASE_NOTES_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    def feed_url(filename: str) -> str:
        return urljoin(page_url, filename)

    written: list[str] = []

    def write(filename: str, content: str) -> None:
        (out_dir / filename).write_text(content, encoding="utf-8")
        written.append(filename)

    write(
        "feed.xml",
        render_rss(
            title="LimaCharlie Release Notes",
            description="Releases and platform updates for LimaCharlie.",
            page_url=page_url,
            feed_url=feed_url("feed.xml"),
            entries=entries,
            generator=generator,
        ),
    )
    write(
        "feed.json",
        render_json_feed(
            title="LimaCharlie Release Notes",
            description="Releases and platform updates for LimaCharlie.",
            page_url=page_url,
            feed_url=feed_url("feed.json"),
            entries=entries,
        ),
    )

    for component in COMPONENTS:
        subset = [e for e in entries if component.slug in e.categories]
        if not subset:
            continue
        filename = f"{component.slug}.xml"
        write(
            filename,
            render_rss(
                title=f"LimaCharlie Release Notes: {component.name}",
                description=component.description,
                page_url=page_url,
                feed_url=feed_url(filename),
                entries=subset,
                generator=generator,
            ),
        )

    # Always published, even while empty, so the subscribe link on the page is
    # never dead and readers can subscribe ahead of the first breaking release.
    write(
        "breaking-changes.xml",
        render_rss(
            title="LimaCharlie Release Notes: Breaking Changes",
            description=(
                "Releases carrying a breaking change or an event schema change."
            ),
            page_url=page_url,
            feed_url=feed_url("breaking-changes.xml"),
            entries=[e for e in entries if e.is_breaking],
            generator=generator,
        ),
    )

    log.info(
        "release feed: wrote %d feeds covering %d entries (%s)",
        len(written),
        len(entries),
        ", ".join(sorted(written)),
    )
