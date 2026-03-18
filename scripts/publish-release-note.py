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
import os
import re
import sys
from datetime import datetime


DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "10-release-notes")
MKDOCS_YML = os.path.join(os.path.dirname(__file__), "..", "mkdocs.yml")


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
            f.write(f"# Release Notes — {month_label}\n")

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
    """Add the monthly file to mkdocs.yml nav if not already present."""
    filename = dt.strftime("%Y-%m") + ".md"
    month_label = dt.strftime("%B %Y")
    nav_entry = f"10-release-notes/{filename}"

    with open(MKDOCS_YML, "r") as f:
        content = f.read()

    if nav_entry in content:
        return

    # Find the Release Notes section and add the new month
    # Insert after the index line, keeping months in reverse chronological order
    release_notes_pattern = r"(  - Release Notes:\n(?:.*\n)*?)(      - Overview: 10-release-notes/index\.md\n)"
    match = re.search(release_notes_pattern, content)

    if not match:
        print(f"Warning: Could not find Release Notes nav section in mkdocs.yml", file=sys.stderr)
        return

    # Find all existing monthly entries to insert in the right position
    section_end = match.end()
    insert_line = f"      - {month_label}: {nav_entry}\n"

    # Insert right after the index line
    content = content[:section_end] + insert_line + content[section_end:]

    with open(MKDOCS_YML, "w") as f:
        f.write(content)

    print(f"Added {month_label} to mkdocs.yml nav")


def main():
    parser = argparse.ArgumentParser(description="Publish a release note entry")
    parser.add_argument("--component", required=True, help="Component name (e.g., sensor, python-sdk)")
    parser.add_argument("--version", required=True, help="Version tag (e.g., v4.32.0)")
    parser.add_argument("--date", required=True, help="Release date (ISO 8601 or YYYY-MM-DD)")
    parser.add_argument("--url", default="", help="URL to the GitHub Release")
    parser.add_argument("--body", default="", help="Release note body in markdown")
    args = parser.parse_args()

    os.makedirs(DOCS_DIR, exist_ok=True)

    dt = parse_date(args.date)
    filepath = ensure_monthly_file(dt)
    append_entry(filepath, args.component, args.version, dt, args.url, args.body)
    update_mkdocs_nav(dt)

    print(f"Published: {args.component} {args.version} -> {filepath}")


if __name__ == "__main__":
    main()
