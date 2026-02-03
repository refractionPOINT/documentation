#!/usr/bin/env python3
"""
Documentation Reorganization Script

Migrates LimaCharlie documentation from the old structure to the new
user-journey-based organization.

Usage:
    python scripts/reorganize.py --dry-run     # Preview changes
    python scripts/reorganize.py --execute     # Apply changes
    python scripts/reorganize.py --validate    # Check for broken links
"""

import json
import os
import re
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple


# Project root (parent of scripts/)
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
MAPPING_FILE = PROJECT_ROOT / "content-mapping.json"


def load_mapping() -> Dict:
    """Load the content mapping configuration."""
    with open(MAPPING_FILE) as f:
        return json.load(f)


def get_all_markdown_files(docs_dir: Path) -> List[Path]:
    """Find all markdown files in the docs directory."""
    return list(docs_dir.rglob("*.md"))


def extract_internal_links(content: str) -> Set[str]:
    """Extract all internal markdown links from content."""
    # Match [text](path) and [text](path#anchor) patterns
    # Exclude external URLs (http/https)
    pattern = r'\[([^\]]+)\]\((?!https?://)([^)]+)\)'
    links = set()
    for match in re.finditer(pattern, content):
        link = match.group(2).split('#')[0]  # Remove anchor
        if link and not link.startswith('mailto:'):
            links.add(link)
    return links


def update_internal_links(content: str, old_path: Path, new_path: Path,
                          path_mapping: Dict[str, str]) -> str:
    """Update internal links in content to reflect new file locations."""

    def replace_link(match):
        text = match.group(1)
        link = match.group(2)

        # Skip external links and anchors
        if link.startswith(('http://', 'https://', 'mailto:', '#')):
            return match.group(0)

        # Split anchor if present
        anchor = ''
        if '#' in link:
            link, anchor = link.split('#', 1)
            anchor = '#' + anchor

        # Resolve the link relative to the old file location
        old_dir = old_path.parent
        resolved = (old_dir / link).resolve()
        resolved_str = str(resolved)

        # Check if we have a mapping for this file
        for old, new in path_mapping.items():
            if resolved_str.endswith(old) or old in resolved_str:
                # Calculate new relative path from new location
                new_file = Path(new)
                new_dir = new_path.parent
                try:
                    rel_path = os.path.relpath(new_file, new_dir)
                    return f'[{text}]({rel_path}{anchor})'
                except ValueError:
                    pass

        return match.group(0)

    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    return re.sub(pattern, replace_link, content)


def identify_duplicates(mapping: Dict) -> Dict[str, List[str]]:
    """Identify files that exist in multiple locations."""
    duplicates = {}

    for dup_group in mapping.get('duplicates', []):
        files = dup_group.get('files', [])
        if len(files) > 1:
            # Use filename as key
            key = Path(files[0]).name
            duplicates[key] = files

    return duplicates


def create_directory_structure(mapping: Dict, dry_run: bool = True) -> List[str]:
    """Create the new directory structure."""
    actions = []
    sections = mapping.get('metadata', {}).get('proposed_sections', [])

    for section in sections:
        new_dir = DOCS_DIR / section
        if not new_dir.exists():
            actions.append(f"CREATE DIR: {new_dir}")
            if not dry_run:
                new_dir.mkdir(parents=True, exist_ok=True)

    return actions


def migrate_files(mapping: Dict, dry_run: bool = True) -> Tuple[List[str], List[str]]:
    """Migrate files to new locations."""
    actions = []
    warnings = []

    # Build path mapping for link updates
    path_mapping = {}
    for item in mapping.get('mappings', []):
        old = item.get('current_path', '')
        new = item.get('new_path', '')
        if old and new:
            path_mapping[old] = new

    duplicates = identify_duplicates(mapping)

    for item in mapping.get('mappings', []):
        current = item.get('current_path', '')
        new_path = item.get('new_path', '')
        notes = item.get('notes', '')

        if not current or not new_path:
            continue

        current_file = PROJECT_ROOT / current
        new_file = PROJECT_ROOT / new_path

        # Check if this is a duplicate we should skip
        filename = current_file.name
        if filename in duplicates:
            dup_files = duplicates[filename]
            # Keep the first one, skip others
            if str(current_file) not in dup_files[0]:
                warnings.append(f"SKIP DUPLICATE: {current} (keeping {dup_files[0]})")
                continue

        if current_file.exists():
            actions.append(f"MOVE: {current} -> {new_path}")

            if not dry_run:
                # Create parent directory
                new_file.parent.mkdir(parents=True, exist_ok=True)

                # Read content and update links
                content = current_file.read_text(encoding='utf-8')
                updated_content = update_internal_links(
                    content, current_file, new_file, path_mapping
                )

                # Write to new location
                new_file.write_text(updated_content, encoding='utf-8')
        else:
            warnings.append(f"NOT FOUND: {current}")

    return actions, warnings


def validate_links(docs_dir: Path) -> List[str]:
    """Validate all internal links in the documentation."""
    broken_links = []

    for md_file in get_all_markdown_files(docs_dir):
        content = md_file.read_text(encoding='utf-8')
        links = extract_internal_links(content)

        for link in links:
            # Resolve relative to the file's directory
            target = (md_file.parent / link).resolve()

            if not target.exists():
                broken_links.append(f"{md_file}: broken link to '{link}'")

    return broken_links


def generate_redirects(mapping: Dict) -> str:
    """Generate redirect configuration for old URLs."""
    redirects = []

    for item in mapping.get('mappings', []):
        old = item.get('current_path', '').replace('docs/', '')
        new = item.get('new_path', '').replace('docs/', '')

        if old and new and old != new:
            # Convert to URL paths
            old_url = '/' + old.replace('.md', '/')
            new_url = '/' + new.replace('.md', '/')
            redirects.append(f'"{old_url}": "{new_url}"')

    return "redirects:\n  " + "\n  ".join(redirects[:50])  # Sample


def main():
    parser = argparse.ArgumentParser(
        description='Reorganize LimaCharlie documentation structure'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Apply the reorganization'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate internal links after reorganization'
    )
    parser.add_argument(
        '--redirects',
        action='store_true',
        help='Generate redirect configuration'
    )

    args = parser.parse_args()

    if not any([args.dry_run, args.execute, args.validate, args.redirects]):
        parser.print_help()
        return

    mapping = load_mapping()

    if args.redirects:
        print(generate_redirects(mapping))
        return

    if args.validate:
        print("Validating internal links...")
        broken = validate_links(DOCS_DIR)
        if broken:
            print(f"\nFound {len(broken)} broken links:")
            for link in broken[:20]:
                print(f"  - {link}")
            if len(broken) > 20:
                print(f"  ... and {len(broken) - 20} more")
        else:
            print("All internal links are valid!")
        return

    dry_run = not args.execute

    print("=" * 60)
    print("LimaCharlie Documentation Reorganization")
    print("=" * 60)
    print(f"Mode: {'DRY RUN (preview only)' if dry_run else 'EXECUTE (applying changes)'}")
    print()

    # Create directories
    print("Creating directory structure...")
    dir_actions = create_directory_structure(mapping, dry_run)
    for action in dir_actions:
        print(f"  {action}")

    print()

    # Migrate files
    print("Migrating files...")
    file_actions, warnings = migrate_files(mapping, dry_run)

    print(f"\nActions ({len(file_actions)}):")
    for action in file_actions[:30]:
        print(f"  {action}")
    if len(file_actions) > 30:
        print(f"  ... and {len(file_actions) - 30} more")

    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for warning in warnings[:10]:
            print(f"  {warning}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more")

    print()
    print("=" * 60)

    if dry_run:
        print("This was a dry run. Use --execute to apply changes.")
    else:
        print("Reorganization complete!")
        print("Next steps:")
        print("  1. Run --validate to check for broken links")
        print("  2. Update mkdocs.yml with the new navigation")
        print("  3. Test locally with 'mkdocs serve'")


if __name__ == '__main__':
    main()
