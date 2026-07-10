#!/usr/bin/env python3
"""Publish a release note entry to the documentation.

Called by the publish-release-notes GitHub Actions workflow. Appends an entry
to the monthly release notes file (e.g., docs/10-release-notes/2026-03.md),
creating the file if it doesn't exist. Also updates mkdocs.yml nav if the
monthly file is new.

Usage:
    python scripts/publish-release-note.py \
        --component "sensor" \
        --version "v4.32.0" \
        --date "2026-03-18T14:30:00Z" \
        --url "https://github.com/refractionPOINT/lce/releases/tag/v4.32.0" \
        --body "Release note content in markdown"
"""

import argparse
import html
import os
import re
import sys
from datetime import datetime
from urllib.parse import urlparse


DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "10-release-notes")
MKDOCS_YML = os.path.join(os.path.dirname(__file__), "..", "mkdocs.yml")

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


def ensure_monthly_file(dt: datetime) -> str:
    """Create the monthly file if it doesn't exist. Returns the file path."""
    filename = dt.strftime("%Y-%m") + ".md"
    filepath = os.path.join(DOCS_DIR, filename)

    if not os.path.exists(filepath):
        month_label = dt.strftime("%B %Y")
        with open(filepath, "w") as f:
            f.write(f"# Release Notes - {month_label}\n")

    return filepath


def append_entry(filepath: str, component: str, version: str, dt: datetime,
                 url: str, body: str) -> None:
    """Append a release note entry to the monthly file."""
    date_str = dt.strftime("%Y-%m-%d")

    entry_lines = [
        "",
        f"## {component} {version}",
        "",
        f"**Date:** {date_str}",
        "",
    ]

    if url:
        entry_lines.append(f"[GitHub Release]({url})")
        entry_lines.append("")

    if body and body.strip():
        entry_lines.append(body.strip())
        entry_lines.append("")

    entry_lines.append("---")
    entry_lines.append("")

    with open(filepath, "a") as f:
        f.write("\n".join(entry_lines))


def update_mkdocs_nav(dt: datetime) -> None:
    """Add the monthly file to mkdocs.yml nav if not already present.

    Inserts in reverse chronological order so the newest month appears first
    after the Overview entry.
    """
    filename = dt.strftime("%Y-%m") + ".md"
    month_label = dt.strftime("%B %Y")
    nav_entry = f"10-release-notes/{filename}"

    with open(MKDOCS_YML, "r") as f:
        lines = f.readlines()

    # Check if already present
    if any(nav_entry in line for line in lines):
        return

    # Find the "- Overview: 10-release-notes/index.md" line
    overview_idx = None
    for i, line in enumerate(lines):
        if "10-release-notes/index.md" in line:
            overview_idx = i
            break

    if overview_idx is None:
        print("Warning: Could not find Release Notes overview in mkdocs.yml nav", file=sys.stderr)
        return

    insert_line = f"      - {month_label}: {nav_entry}\n"

    # Find the correct position among existing monthly entries (reverse chronological).
    # Monthly entries follow the overview line and match the pattern YYYY-MM.md.
    insert_idx = overview_idx + 1
    for i in range(overview_idx + 1, len(lines)):
        m = re.search(r'10-release-notes/(\d{4}-\d{2})\.md', lines[i])
        if not m:
            break
        # If the existing entry is for a newer or same month, insert after it
        if m.group(1) >= dt.strftime("%Y-%m"):
            insert_idx = i + 1
        else:
            break

    lines.insert(insert_idx, insert_line)

    with open(MKDOCS_YML, "w") as f:
        f.writelines(lines)

    print(f"Added {month_label} to mkdocs.yml nav")


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


def sanitize_body(body: str) -> str:
    """Bound and neutralize the release-note body before it is written to docs.

    The body is machine-fed via repository_dispatch and rendered by MkDocs with
    md_in_html enabled. Two classes of active content must be defused:

    1. Raw HTML (e.g. <script>, <iframe>, event handlers). We HTML-escape the
       three structural characters (& < >), which turns any raw tag - and any
       Markdown autolink like <javascript:...> - into inert text. Quotes are
       intentionally left alone (quote=False) so prose is not mangled; with < and
       > escaped no HTML tag can form, so bare quotes are harmless.
    2. Markdown link/image destinations with a dangerous URL scheme, which
       html.escape does NOT touch (see reject_dangerous_link_schemes). These are
       vetted against a scheme allowlist and the publish is rejected on a hit.

    Normal Markdown - headings, lists, http(s)/mailto links, emphasis,
    inline/fenced code - is left untouched.
    """
    if len(body) > MAX_BODY_LEN:
        print(f"Body too long ({len(body)} > {MAX_BODY_LEN} chars)", file=sys.stderr)
        sys.exit(1)
    reject_dangerous_link_schemes(body)
    return html.escape(body, quote=False)


def main():
    parser = argparse.ArgumentParser(description="Publish a release note entry")
    parser.add_argument("--component", required=True, help="Component name (e.g., sensor, python-sdk)")
    parser.add_argument("--version", required=True, help="Version tag (e.g., v4.32.0)")
    parser.add_argument("--date", required=True, help="Release date (ISO 8601 or YYYY-MM-DD)")
    parser.add_argument("--url", default="", help="URL to the GitHub Release")
    parser.add_argument("--body", default="", help="Release note body in markdown")
    args = parser.parse_args()

    validate_inputs(args.component, args.version)
    validate_url(args.url)
    # Neutralize any raw HTML in the untrusted body before it reaches the docs.
    body = sanitize_body(args.body)

    os.makedirs(DOCS_DIR, exist_ok=True)

    dt = parse_date(args.date)
    filepath = ensure_monthly_file(dt)
    append_entry(filepath, args.component, args.version, dt, args.url, body)
    update_mkdocs_nav(dt)

    print(f"Published: {args.component} {args.version} -> {filepath}")


if __name__ == "__main__":
    main()
