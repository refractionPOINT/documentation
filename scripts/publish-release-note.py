#!/usr/bin/env python3
"""Publish a release note entry to the documentation.

Called by the publish-release-notes GitHub Actions workflow. Inserts an entry
into docs/10-release-notes/index.md, under the ``## YYYY-MM-DD`` heading for the
release date, creating that date heading in the right chronological position
when it is the first release of the day.

That page is the single source the RSS/JSON feeds are generated from
(``hooks/release_feed.py``), so an entry written anywhere else would be
published but never announced. The ``--component`` slug is resolved to its
canonical display name through the same component registry the feeds use, which
is what keeps a machine-published entry in the same feed as a hand-written one
(``--component sensor`` and ``--component endpoint-agent`` both land under
``### Endpoint Agent``).

Usage:
    python scripts/publish-release-note.py \\
        --component "sensor" \\
        --version "v4.32.0" \\
        --date "2026-03-18T14:30:00Z" \\
        --url "https://github.com/refractionPOINT/example/releases/tag/v4.32.0" \\
        --body "Release note content in markdown"
"""

import argparse
import html
import os
import re
import sys
from datetime import datetime
from urllib.parse import urlparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hooks"))

from release_feed import (  # noqa: E402
    ALIAS_INDEX,
    COMPONENTS,
    COMPONENTS_BY_SLUG,
    DATE_RE,
    PLATFORM_SLUG,
    iter_markdown_headings,
    normalize_name,
)

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "10-release-notes")
INDEX_MD = os.path.join(DOCS_DIR, "index.md")

# Allowlisted hosts for the release URL. A URL is accepted only when its host is
# one of these exactly or a subdomain of one (e.g. docs.limacharlie.io). The
# dotted-boundary check ("." + domain) prevents look-alike hosts such as
# "evilgithub.com" or "limacharlie.io.attacker.example" from slipping through an
# endswith() match.
ALLOWED_URL_HOSTS = ("github.com", "limacharlie.io")

# Upper bound on the release-note body. Release notes are short; this simply
# caps how much untrusted, machine-fed content we will ever write into the docs.
MAX_BODY_LEN = 50000

# URL schemes that may appear in a Markdown link or image destination in the
# release URL or body. Anything else (javascript:, data:, vbscript:, file:, ...)
# is rejected: those render to a live href/src and would be a stored one-click
# XSS on the docs site. Scheme-less destinations (relative paths, "#anchors",
# "example.com/x") have no scheme and are always allowed.
ALLOWED_LINK_SCHEMES = ("http", "https", "mailto")

# Matches a leading URL scheme ("javascript:", "https:", ...) on a destination.
_SCHEME_RE = re.compile(r"^([a-zA-Z][a-zA-Z0-9+.\-]*):")

# Inline link/image destination: the text right after "](", up to the first
# whitespace, ">", or ")". Handles an optional leading "<".
_INLINE_DEST_RE = re.compile(r"\]\(\s*<?\s*([^)\s>]+)")

# Reference-style link definition at the start of a line: "[label]: dest".
_REF_DEST_RE = re.compile(r"(?m)^[ \t]{0,3}\[[^\]]+\]:\s*<?\s*([^\s>]+)")


def parse_date(date_str: str) -> datetime:
    """Parse ISO 8601 or YYYY-MM-DD date string."""
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str.replace("+00:00", "Z"), fmt)
        except ValueError:
            continue
    raise ValueError(f"Unable to parse date: {date_str}")


def canonical_component(component: str) -> str:
    """Resolve a component slug to the display name used in entry headings.

    Rejects anything the registry does not know rather than inventing a
    heading: an unrecognized name would produce an entry that lands in the
    catch-all feed and fails scripts/check-release-note-headings.py, which is
    worse than refusing the publish and having a human name the component.
    """
    slugs = ALIAS_INDEX.get(normalize_name(component))
    if slugs and len(slugs) == 1 and slugs[0] != PLATFORM_SLUG:
        return COMPONENTS_BY_SLUG[slugs[0]].name
    known = ", ".join(
        sorted(c.name for c in COMPONENTS if c.slug != PLATFORM_SLUG)
    )
    print(
        f"Unknown component: {component}. Expected one of: {known} "
        "(or any of their aliases in hooks/release_feed.py).",
        file=sys.stderr,
    )
    sys.exit(1)


def build_entry(component: str, version: str, url: str, body: str) -> list[str]:
    """Render the Markdown lines of one entry, heading included."""
    lines = [f"### {component} {version}", ""]
    if url:
        lines += [f"[GitHub Release]({url})", ""]
    if body and body.strip():
        lines += [body.strip(), ""]
    return lines


def insert_entry(filepath: str, component: str, version: str, dt: datetime,
                 url: str, body: str) -> None:
    """Insert an entry into the release notes page, newest first.

    The page is ordered newest date first, and entries within a date are
    ordered newest first too, so a new entry goes directly under its date
    heading. A date heading that does not exist yet is created in the position
    that keeps the page ordered, with the ``---`` rule that separates dates.
    """
    date_str = dt.strftime("%Y-%m-%d")
    entry = build_entry(component, version, url, body)

    with open(filepath, encoding="utf-8") as handle:
        lines = handle.read().splitlines()

    # Line indices are 0-based, iter_markdown_headings reports 1-based lines.
    # Fence-aware, so a "## 2020-01-01" inside a fenced example on the page is
    # never mistaken for a date group and used as an insertion point.
    date_headings = [
        (lineno - 1, title)
        for level, title, lineno in iter_markdown_headings("\n".join(lines))
        if level == 2 and DATE_RE.match(title)
    ]

    for index, heading_date in date_headings:
        if heading_date == date_str:
            # Existing date: the new entry becomes the first one of that day.
            insert_at = index + 1
            while insert_at < len(lines) and not lines[insert_at].strip():
                insert_at += 1
            lines[insert_at:insert_at] = entry
            break
    else:
        # First heading that is older than this release, so the page stays
        # newest first. ISO dates compare chronologically as strings.
        insert_at = len(lines)
        for index, heading_date in date_headings:
            if heading_date < date_str:
                insert_at = index
                break

        if insert_at == len(lines):
            # Oldest release on the page: the "---" rule leads the block so the
            # page does not end on a stray horizontal rule.
            block = ["", "---", "", f"## {date_str}", ""] + entry
        else:
            block = [f"## {date_str}", ""] + entry + ["---", ""]
        lines[insert_at:insert_at] = block

    with open(filepath, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines).rstrip() + "\n")


def validate_inputs(component: str, version: str) -> None:
    """Validate component and version to prevent path traversal or injection.

    Uses ``re.fullmatch`` so the whole string must match: ``re.match`` with a
    trailing ``$`` would also accept a single trailing newline, letting a caller
    smuggle a line break into the generated heading.
    """
    if not re.fullmatch(r'[\w][\w.-]*', component):
        print(f"Invalid component name: {component}", file=sys.stderr)
        sys.exit(1)
    if not re.fullmatch(r'v?[\d]+[\d.]*[\w.-]*', version):
        print(f"Invalid version: {version}", file=sys.stderr)
        sys.exit(1)


def validate_url(url: str) -> None:
    """Validate the optional release URL before it is embedded in the docs.

    An empty URL is allowed (the field is optional). A non-empty URL must use the
    https scheme and point at an allowlisted host (see ALLOWED_URL_HOSTS);
    anything else is rejected so a caller cannot inject a link to an arbitrary
    (e.g. javascript:, http:, or attacker-controlled) destination.
    """
    if not url:
        return
    parsed = urlparse(url)
    if parsed.scheme != "https":
        print(f"Invalid URL scheme (must be https): {url}", file=sys.stderr)
        sys.exit(1)
    host = (parsed.hostname or "").lower()
    if not any(host == d or host.endswith("." + d) for d in ALLOWED_URL_HOSTS):
        print(f"URL host not in allowlist ({', '.join(ALLOWED_URL_HOSTS)}): {url}", file=sys.stderr)
        sys.exit(1)
    # urlparse().hostname stops at the first "/", "?" or "#", so the host
    # allowlist alone does not vet the rest of the string - and the raw URL is
    # embedded verbatim inside a Markdown link destination ("[GitHub Release](URL)").
    # A ")" or whitespace would close/break that destination and let a caller
    # inject further Markdown (e.g. a javascript: link), which passes the host
    # check. None of these characters appear in a legitimate release URL, so
    # reject them.
    forbidden = set(' \t\r\n"`\\()<>')
    if any(c in forbidden or ord(c) < 0x20 for c in url):
        print(f"URL contains forbidden characters: {url}", file=sys.stderr)
        sys.exit(1)


def reject_dangerous_link_schemes(body: str) -> None:
    """Reject the publish if a Markdown link/image destination uses a bad scheme.

    ``html.escape`` neutralizes raw HTML and autolinks, but Markdown inline links
    (``[x](javascript:...)``) and reference definitions (``[x]: javascript:...``)
    still render to a live ``<a href>`` regardless of HTML escaping, so a
    ``javascript:`` or ``data:`` destination would be a stored one-click XSS on
    the docs site. A legitimate, machine-generated release note never uses those
    schemes, so we fail closed rather than trying to rewrite the body.
    """
    for pattern in (_INLINE_DEST_RE, _REF_DEST_RE):
        for match in pattern.finditer(body):
            dest = match.group(1)
            scheme = _SCHEME_RE.match(dest)
            if scheme and scheme.group(1).lower() not in ALLOWED_LINK_SCHEMES:
                print(f"Disallowed URL scheme in release body link: {dest}", file=sys.stderr)
                sys.exit(1)


def reject_structural_markdown(body: str) -> None:
    """Reject a body that would forge the page's own structure.

    The body is written verbatim under a ``### Component Version`` heading. A
    machine-fed body containing its own ``##`` or ``###`` heading would create a
    phantom date group or a phantom entry - a feed item with someone else's
    content, or a build failure from an entry with no date. Bodies legitimately
    use ``####`` sections ("New Features"), which are inside the entry and safe.
    """
    for line in body.splitlines():
        if re.match(r"^#{1,3}\s", line):
            print(
                f"Release body must not contain h1-h3 headings (found: {line!r}). "
                "Use '#### Section' inside an entry.",
                file=sys.stderr,
            )
            sys.exit(1)


def sanitize_body(body: str) -> str:
    """Bound and neutralize the release-note body before it is written to docs.

    The body is machine-fed via repository_dispatch and rendered by MkDocs with
    md_in_html enabled. Three classes of unsafe content must be defused:

    1. Raw HTML (e.g. <script>, <iframe>, event handlers). We HTML-escape the
       three structural characters (& < >), which turns any raw tag - and any
       Markdown autolink like <javascript:...> - into inert text. Quotes are
       intentionally left alone (quote=False) so prose is not mangled; with < and
       > escaped no HTML tag can form, so bare quotes are harmless.
    2. Markdown link/image destinations with a dangerous URL scheme, which
       html.escape does NOT touch (see reject_dangerous_link_schemes). These are
       vetted against a scheme allowlist and the publish is rejected on a hit.
    3. Headings that would forge the page structure the feeds are built from
       (see reject_structural_markdown).

    Normal Markdown - lists, http(s)/mailto links, emphasis, inline/fenced code,
    "####" sections - is left untouched.
    """
    if len(body) > MAX_BODY_LEN:
        print(f"Body too long ({len(body)} > {MAX_BODY_LEN} chars)", file=sys.stderr)
        sys.exit(1)
    reject_dangerous_link_schemes(body)
    reject_structural_markdown(body)
    return html.escape(body, quote=False)


def main():
    parser = argparse.ArgumentParser(description="Publish a release note entry")
    parser.add_argument("--component", required=True, help="Component name (e.g., sensor, web-app)")
    parser.add_argument("--version", required=True, help="Version tag (e.g., v4.32.0)")
    parser.add_argument("--date", required=True, help="Release date (ISO 8601 or YYYY-MM-DD)")
    parser.add_argument("--url", default="", help="URL to the GitHub Release")
    parser.add_argument("--body", default="", help="Release note body in markdown")
    args = parser.parse_args()

    validate_inputs(args.component, args.version)
    validate_url(args.url)
    # Neutralize any raw HTML in the untrusted body before it reaches the docs.
    body = sanitize_body(args.body)
    component = canonical_component(args.component)

    if not os.path.exists(INDEX_MD):
        print(f"Release notes page not found: {INDEX_MD}", file=sys.stderr)
        sys.exit(1)

    dt = parse_date(args.date)
    insert_entry(INDEX_MD, component, args.version, dt, args.url, body)

    print(f"Published: {component} {args.version} -> {INDEX_MD}")


if __name__ == "__main__":
    main()
