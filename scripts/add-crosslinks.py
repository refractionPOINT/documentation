#!/usr/bin/env python3
"""
Add Cross-Links to Documentation

Adds "See Also" sections and contextual hyperlinks to connect related content.
Analyzes content to suggest and add relevant cross-references.

Usage:
    python scripts/add-crosslinks.py --dry-run    # Preview changes
    python scripts/add-crosslinks.py --execute    # Apply changes
"""

import os
import re
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"

# Define related content clusters for cross-linking
CONTENT_CLUSTERS = {
    # Getting Started links
    "1-getting-started/quickstart.md": [
        ("Core Concepts", "1-getting-started/core-concepts.md"),
        ("Installation Keys", "2-sensors-deployment/installation-keys.md"),
        ("Your First Detection Rule", "3-detection-response/index.md"),
    ],
    "1-getting-started/core-concepts.md": [
        ("Quickstart Guide", "1-getting-started/quickstart.md"),
        ("Sensor Deployment", "2-sensors-deployment/index.md"),
        ("Detection & Response", "3-detection-response/index.md"),
        ("LCQL Queries", "4-data-queries/index.md"),
    ],
    "1-getting-started/what-is-limacharlie.md": [
        ("Quickstart Guide", "1-getting-started/quickstart.md"),
        ("Core Concepts", "1-getting-started/core-concepts.md"),
        ("Use Cases", "1-getting-started/use-cases/"),
    ],

    # Sensors links
    "2-sensors-deployment/index.md": [
        ("Installation Keys", "2-sensors-deployment/installation-keys.md"),
        ("Endpoint Agents", "2-sensors-deployment/endpoint-agent/"),
        ("Adapters", "2-sensors-deployment/adapters/index.md"),
        ("Sensor Tags", "2-sensors-deployment/sensor-tags.md"),
    ],
    "2-sensors-deployment/installation-keys.md": [
        ("Sensor Deployment Overview", "2-sensors-deployment/index.md"),
        ("Windows Installation", "2-sensors-deployment/endpoint-agent/windows/installation.md"),
        ("Linux Installation", "2-sensors-deployment/endpoint-agent/linux/installation.md"),
        ("macOS Installation", "2-sensors-deployment/endpoint-agent/macos/installation-latest.md"),
    ],
    "2-sensors-deployment/sensor-tags.md": [
        ("D&R Rules with Tags", "3-detection-response/index.md"),
        ("Sensor Selectors", "8-reference/sensor-selector-expressions.md"),
    ],
    "2-sensors-deployment/adapters/index.md": [
        ("Adapter Deployment", "2-sensors-deployment/adapters/deployment.md"),
        ("Adapters as a Service", "2-sensors-deployment/adapters/as-a-service.md"),
        ("Outputs", "5-integrations/outputs/index.md"),
    ],

    # Detection & Response links
    "3-detection-response/index.md": [
        ("Writing Rules", "3-detection-response/tutorials/writing-testing-rules.md"),
        ("Detection Examples", "3-detection-response/examples.md"),
        ("Response Actions", "8-reference/response-actions.md"),
        ("False Positive Rules", "3-detection-response/false-positives.md"),
        ("LCQL Queries", "4-data-queries/index.md"),
    ],
    "3-detection-response/examples.md": [
        ("D&R Rules Overview", "3-detection-response/index.md"),
        ("Detection Operators", "8-reference/detection-logic-operators.md"),
        ("Response Actions", "8-reference/response-actions.md"),
    ],
    "3-detection-response/false-positives.md": [
        ("D&R Rules Overview", "3-detection-response/index.md"),
        ("Writing Rules", "3-detection-response/tutorials/writing-testing-rules.md"),
    ],
    "3-detection-response/stateful-rules.md": [
        ("D&R Rules Overview", "3-detection-response/index.md"),
        ("Writing Rules", "3-detection-response/tutorials/writing-testing-rules.md"),
    ],

    # Data & Queries links
    "4-data-queries/index.md": [
        ("LCQL Examples", "4-data-queries/lcql-examples.md"),
        ("Query Console UI", "4-data-queries/query-console-ui.md"),
        ("Event Schemas", "4-data-queries/events/event-schemas.md"),
        ("D&R Rules", "3-detection-response/index.md"),
    ],
    "4-data-queries/lcql-examples.md": [
        ("LCQL Overview", "4-data-queries/index.md"),
        ("Query Console", "4-data-queries/query-console-ui.md"),
        ("EDR Events", "8-reference/edr-events.md"),
    ],

    # Integrations links
    "5-integrations/index.md": [
        ("Outputs Overview", "5-integrations/outputs/index.md"),
        ("Extensions", "5-integrations/extensions/index.md"),
        ("API Integrations", "5-integrations/api-integrations/index.md"),
    ],
    "5-integrations/outputs/index.md": [
        ("Stream Structures", "5-integrations/outputs/stream-structures.md"),
        ("Output Destinations", "5-integrations/outputs/destinations/"),
        ("D&R Response Actions", "8-reference/response-actions.md"),
    ],
    "5-integrations/extensions/index.md": [
        ("Using Extensions", "5-integrations/extensions/using-extensions.md"),
        ("Building Extensions", "6-developer-guide/extensions/building-extensions.md"),
        ("Git Sync (IaC)", "5-integrations/extensions/limacharlie/ext-git-sync.md"),
    ],

    # Developer Guide links
    "6-developer-guide/index.md": [
        ("Python SDK", "6-developer-guide/sdks/python-sdk.md"),
        ("Go SDK", "6-developer-guide/sdks/go-sdk.md"),
        ("Building Extensions", "6-developer-guide/extensions/building-extensions.md"),
        ("API Keys", "7-administration/access/api-keys.md"),
    ],
    "6-developer-guide/sdks/python-sdk.md": [
        ("SDK Overview", "6-developer-guide/sdks/index.md"),
        ("Go SDK", "6-developer-guide/sdks/go-sdk.md"),
        ("API Keys", "7-administration/access/api-keys.md"),
    ],
    "6-developer-guide/sdks/go-sdk.md": [
        ("SDK Overview", "6-developer-guide/sdks/index.md"),
        ("Python SDK", "6-developer-guide/sdks/python-sdk.md"),
        ("API Keys", "7-administration/access/api-keys.md"),
    ],

    # Administration links
    "7-administration/index.md": [
        ("User Access", "7-administration/access/"),
        ("API Keys", "7-administration/access/api-keys.md"),
        ("Billing", "7-administration/billing/"),
    ],
    "7-administration/access/api-keys.md": [
        ("User Access", "7-administration/access/users.md"),
        ("Permissions Reference", "7-administration/access/permissions.md"),
        ("SDKs", "6-developer-guide/sdks/index.md"),
    ],

    # Reference links
    "8-reference/index.md": [
        ("Detection Operators", "8-reference/detection-logic-operators.md"),
        ("Response Actions", "8-reference/response-actions.md"),
        ("EDR Events", "8-reference/edr-events.md"),
        ("FAQ", "8-reference/faq/index.md"),
    ],
    "8-reference/detection-logic-operators.md": [
        ("D&R Rules Overview", "3-detection-response/index.md"),
        ("Response Actions", "8-reference/response-actions.md"),
        ("Writing Rules", "3-detection-response/tutorials/writing-testing-rules.md"),
    ],
    "8-reference/response-actions.md": [
        ("D&R Rules Overview", "3-detection-response/index.md"),
        ("Detection Operators", "8-reference/detection-logic-operators.md"),
        ("Endpoint Commands", "8-reference/endpoint-agent-commands.md"),
    ],
}

# Keywords that should link to specific pages when found in content
KEYWORD_LINKS = {
    "D&R rule": "3-detection-response/index.md",
    "detection rule": "3-detection-response/index.md",
    "response action": "8-reference/response-actions.md",
    "LCQL": "4-data-queries/index.md",
    "sensor selector": "8-reference/sensor-selector-expressions.md",
    "installation key": "2-sensors-deployment/installation-keys.md",
    "API key": "7-administration/access/api-keys.md",
}


def get_relative_path(from_file: Path, to_file: str) -> str:
    """Calculate relative path from one file to another."""
    from_dir = from_file.parent
    to_path = DOCS_DIR / to_file
    try:
        return os.path.relpath(to_path, from_dir)
    except ValueError:
        return to_file


def has_see_also(content: str) -> bool:
    """Check if content already has a See Also section."""
    return bool(re.search(r'^##\s*(See Also|Related|Related Topics)', content, re.MULTILINE | re.IGNORECASE))


def generate_see_also_section(file_path: Path, links: List[Tuple[str, str]]) -> str:
    """Generate a See Also section with relative links."""
    lines = ["\n---\n", "## See Also\n"]

    for title, target in links:
        rel_path = get_relative_path(file_path, target)
        lines.append(f"- [{title}]({rel_path})")

    lines.append("")
    return "\n".join(lines)


def add_see_also_to_file(file_path: Path, dry_run: bool = True) -> Tuple[bool, str]:
    """Add See Also section to a file if it doesn't have one."""
    rel_path = str(file_path.relative_to(DOCS_DIR))

    if rel_path not in CONTENT_CLUSTERS:
        return False, "No cross-links defined"

    content = file_path.read_text(encoding='utf-8')

    if has_see_also(content):
        return False, "Already has See Also section"

    links = CONTENT_CLUSTERS[rel_path]

    # Filter out links to non-existent files
    valid_links = []
    for title, target in links:
        target_path = DOCS_DIR / target
        if target_path.exists() or target_path.is_dir():
            valid_links.append((title, target))

    if not valid_links:
        return False, "No valid link targets"

    see_also = generate_see_also_section(file_path, valid_links)
    new_content = content.rstrip() + "\n" + see_also

    if not dry_run:
        file_path.write_text(new_content, encoding='utf-8')

    return True, f"Added {len(valid_links)} links"


def find_files_needing_crosslinks() -> List[Path]:
    """Find all markdown files that could use cross-links."""
    files = []
    for pattern in CONTENT_CLUSTERS.keys():
        file_path = DOCS_DIR / pattern
        if file_path.exists():
            files.append(file_path)
    return files


def add_crosslinks_to_all(dry_run: bool = True) -> Dict[str, str]:
    """Add cross-links to all applicable files."""
    results = {}

    for rel_path in CONTENT_CLUSTERS.keys():
        file_path = DOCS_DIR / rel_path
        if file_path.exists():
            changed, message = add_see_also_to_file(file_path, dry_run)
            status = "ADDED" if changed else "SKIPPED"
            results[rel_path] = f"{status}: {message}"

    return results


def main():
    parser = argparse.ArgumentParser(description='Add cross-links to documentation')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes')
    parser.add_argument('--execute', action='store_true', help='Apply changes')

    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        parser.print_help()
        return

    dry_run = not args.execute

    print("=" * 60)
    print("Add Cross-Links to Documentation")
    print("=" * 60)
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print(f"Files to process: {len(CONTENT_CLUSTERS)}")
    print()

    results = add_crosslinks_to_all(dry_run)

    added = [k for k, v in results.items() if v.startswith("ADDED")]
    skipped = [k for k, v in results.items() if v.startswith("SKIPPED")]

    print("Results:")
    print(f"  Added See Also sections: {len(added)}")
    print(f"  Skipped (already has or no targets): {len(skipped)}")
    print()

    if added:
        print("Files updated:")
        for f in added:
            print(f"  + {f}")

    print()
    print("=" * 60)

    if dry_run:
        print("This was a dry run. Use --execute to apply changes.")
    else:
        print("Cross-links added!")


if __name__ == '__main__':
    main()
