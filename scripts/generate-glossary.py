#!/usr/bin/env python3
"""
Generate MkDocs abbreviations file from glossary CSV.

Converts glossary CSV export to MkDocs abbreviation format for tooltips.
The abbr extension shows definitions on hover when terms appear in docs.

Usage:
    python scripts/generate-glossary.py input.csv
"""

import csv
import re
import sys
import html
from pathlib import Path


def strip_html(text: str) -> str:
    """Remove HTML tags and decode entities."""
    # Decode HTML entities
    text = html.unescape(text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Clean up whitespace
    text = ' '.join(text.split())
    return text.strip()


def truncate_definition(text: str, max_length: int = 300) -> str:
    """Truncate definition to reasonable tooltip length."""
    if len(text) <= max_length:
        return text
    # Truncate at word boundary
    truncated = text[:max_length].rsplit(' ', 1)[0]
    return truncated + '...'


def generate_abbreviations(csv_path: str) -> str:
    """Generate MkDocs abbreviation definitions from CSV."""
    lines = [
        "<!-- Glossary definitions for tooltip abbreviations -->",
        "<!-- Auto-generated from glossary CSV - do not edit manually -->",
        "",
    ]

    seen_terms = set()

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            term = row.get('Glossary Name', '').strip()
            description = row.get('Glossary Description', '').strip()

            if not term or not description:
                continue

            # Skip duplicates (keep first occurrence)
            term_lower = term.lower()
            if term_lower in seen_terms:
                continue
            seen_terms.add(term_lower)

            # Clean and truncate description
            clean_desc = strip_html(description)
            clean_desc = truncate_definition(clean_desc)

            # Escape any special characters
            clean_desc = clean_desc.replace('"', "'")

            # MkDocs abbreviation format
            lines.append(f"*[{term}]: {clean_desc}")

    lines.append("")  # Trailing newline
    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate-glossary.py <input.csv>")
        print("Output goes to docs/includes/glossary.md")
        sys.exit(1)

    csv_path = sys.argv[1]
    output_path = Path(__file__).parent.parent / "docs" / "includes" / "glossary.md"

    print(f"Reading: {csv_path}")
    content = generate_abbreviations(csv_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding='utf-8')

    # Count terms
    term_count = len([l for l in content.split('\n') if l.startswith('*[')])
    print(f"Generated {term_count} glossary terms")
    print(f"Output: {output_path}")


if __name__ == '__main__':
    main()
