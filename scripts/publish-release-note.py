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
    """Validate component and version to prevent path traversal or injection."""
    if not re.match(r'^[\w][\w.-]*$', component):
        print(f"Invalid component name: {component}", file=sys.stderr)
        sys.exit(1)
    if not re.match(r'^v?[\d]+[\d.]*[\w.-]*$', version):
        print(f"Invalid version: {version}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Publish a release note entry")
    parser.add_argument("--component", required=True, help="Component name (e.g., sensor, python-sdk)")
    parser.add_argument("--version", required=True, help="Version tag (e.g., v4.32.0)")
    parser.add_argument("--date", required=True, help="Release date (ISO 8601 or YYYY-MM-DD)")
    parser.add_argument("--url", default="", help="URL to the GitHub Release")
    parser.add_argument("--body", default="", help="Release note body in markdown")
    args = parser.parse_args()

    validate_inputs(args.component, args.version)

    os.makedirs(DOCS_DIR, exist_ok=True)

    dt = parse_date(args.date)
    filepath = ensure_monthly_file(dt)
    append_entry(filepath, args.component, args.version, dt, args.url, args.body)
    update_mkdocs_nav(dt)

    print(f"Published: {args.component} {args.version} -> {filepath}")


if __name__ == "__main__":
    main()
