#!/usr/bin/env python3
"""
Fix Broken Internal Links

Automatically updates internal markdown links from old paths to new paths
based on the content mapping.

Usage:
    python scripts/fix-links.py --dry-run    # Preview changes
    python scripts/fix-links.py --execute    # Apply fixes
"""

import json
import os
import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"

# Map old path patterns to new paths
PATH_MAPPINGS = {
    # Getting Started
    'Getting_Started/index.md': '1-getting-started/index.md',
    'Getting_Started/quickstart.md': '1-getting-started/quickstart.md',
    'Getting_Started/what-is-limacharlie.md': '1-getting-started/what-is-limacharlie.md',
    'Getting_Started/limacharlie-core-concepts.md': '1-getting-started/core-concepts.md',
    'Getting_Started/Use_Cases/sleeper-mode.md': '1-getting-started/use-cases/sleeper-mode.md',

    # Sensors
    'Sensors/index.md': '2-sensors-deployment/index.md',
    'Sensors/installation-keys.md': '2-sensors-deployment/installation-keys.md',
    'Sensors/sensor-connectivity.md': '2-sensors-deployment/connectivity.md',
    'Sensors/sensor-tags.md': '2-sensors-deployment/sensor-tags.md',
    'Sensors/Endpoint_Agent/endpoint-agent-commands.md': '8-reference/endpoint-commands.md',
    'Sensors/Endpoint_Agent/Endpoint_Agent_Commands/reference-endpoint-agent-commands.md': '8-reference/endpoint-commands.md',
    'Sensors/Endpoint_Agent/endpoint-agent-uninstallation.md': '2-sensors-deployment/endpoint-agent/uninstallation.md',
    'Sensors/Adapters/adapters.md': '2-sensors-deployment/adapters/index.md',
    'Sensors/Reference/logcollectionguide.md': '2-sensors-deployment/log-collection-guide.md',
    'Sensors/Endpoint_Agent/payloads.md': '2-sensors-deployment/endpoint-agent/payloads.md',
    'Sensors/Adapters/Adapter_Tutorials/tutorial-creating-a-webhook-adapter.md': '2-sensors-deployment/adapters/tutorials/webhook-adapter.md',
    'Sensors/Reference/reference-sensor-selector-expressions.md': '8-reference/sensor-selector-expressions.md',

    # Additional sensor mappings
    'adapters.md': '2-sensors-deployment/adapters/index.md',
    'Adapters/adapters.md': '2-sensors-deployment/adapters/index.md',
    'endpoint-agent-commands.md': '8-reference/endpoint-commands.md',
    'Endpoint_Agent_Commands/endpoint-agent-commands.md': '8-reference/endpoint-commands.md',
    'Endpoint_Agent_Commands/reference-endpoint-agent-commands.md': '8-reference/endpoint-commands.md',
    'endpoint-agent-uninstallation.md': '2-sensors-deployment/endpoint-agent/uninstallation.md',
    'endpoint-agent-installation.md': '2-sensors-deployment/endpoint-agent/index.md',
    'manage_keys.md': '2-sensors-deployment/installation-keys.md',
    'reference-platform-events.md': '8-reference/platform-events.md',
    'reference-edr-events.md': '8-reference/edr-events.md',

    # Administration
    'Administration/api-keys.md': '7-administration/access/api-keys.md',
    'api-keys.md': '7-administration/access/api-keys.md',

    # Detection & Response
    'Detection_and_Response/index.md': '3-detection-response/index.md',
    'Detection_and_Response/detection-and-response.md': '3-detection-response/index.md',
    'Detection_and_Response/detection-and-response-rules.md': '3-detection-response/index.md',
    'Detection_and_Response/writing-and-testing-rules.md': '3-detection-response/tutorials/writing-testing-rules.md',
    'Detection_and_Response/detection-and-response-examples.md': '3-detection-response/examples.md',
    'Detection_and_Response/Reference/detection-logic-operators.md': '8-reference/detection-logic-operators.md',
    'Detection_and_Response/Reference/response-actions.md': '8-reference/response-actions.md',

    # Additional D&R mappings
    'detection-and-response.md': '3-detection-response/index.md',
    'detection-and-response-rules.md': '3-detection-response/index.md',
    'detection-and-response-examples.md': '3-detection-response/examples.md',
    'writing-and-testing-rules.md': '3-detection-response/tutorials/writing-testing-rules.md',
    'writing-testing-rules.md': '3-detection-response/tutorials/writing-testing-rules.md',
    'replay.md': '5-integrations/services/replay.md',
    'detection-logic-operators.md': '8-reference/detection-logic-operators.md',
    'response-actions.md': '8-reference/response-actions.md',

    # Events
    'Events/index.md': '4-data-queries/events/index.md',
    'Events/artifacts.md': '4-data-queries/events/index.md',
    'Events/event-schemas.md': '4-data-queries/events/event-schemas.md',
    'Events/template-strings-and-transforms.md': '4-data-queries/template-strings.md',
    'Events/Endpoint_Agent_Events_Overview/reference-edr-events.md': '8-reference/edr-events.md',
    'Events/Platform_Events_Overview/reference-platform-events.md': '8-reference/platform-events.md',
    'Events/Platform_Events_Overview/reference-schedule-events.md': '8-reference/schedule-events.md',

    # Outputs
    'Outputs/index.md': '5-integrations/outputs/index.md',
    'Outputs/outputs.md': '5-integrations/outputs/index.md',
    'Destinations/outputs-destinations-webhook.md': '5-integrations/outputs/destinations/webhook.md',
    'output-allowlisting.md': '5-integrations/outputs/allowlisting.md',

    # Add-Ons / Extensions - LimaCharlie Extensions (new structure)
    'Add-Ons/index.md': '5-integrations/extensions/index.md',
    'Add-Ons/Extensions/index.md': '5-integrations/extensions/index.md',
    'Add-Ons/Extensions/LimaCharlie_Extensions/ext-usage-alerts.md': '5-integrations/extensions/limacharlie/usage-alerts.md',
    'Add-Ons/Extensions/LimaCharlie_Extensions/ext-infrastructure.md': '5-integrations/extensions/limacharlie/infrastructure.md',
    'Add-Ons/Extensions/LimaCharlie_Extensions/ext-git-sync.md': '5-integrations/extensions/limacharlie/git-sync.md',
    'Add-Ons/Extensions/LimaCharlie_Extensions/ext-yara-manager.md': '5-integrations/extensions/limacharlie/yara-manager.md',
    'Add-Ons/Extensions/Third-Party_Extensions/ext-yara.md': '5-integrations/extensions/third-party/yara.md',
    'Add-Ons/API_Integrations/index.md': '5-integrations/api-integrations/index.md',
    'Add-Ons/Reference/reference-authentication-resource-locator.md': '8-reference/authentication-resource-locator.md',

    # Extension shortcuts (for relative links without full path)
    'ext-usage-alerts.md': '5-integrations/extensions/limacharlie/usage-alerts.md',
    'ext-infrastructure.md': '5-integrations/extensions/limacharlie/infrastructure.md',
    'ext-git-sync.md': '5-integrations/extensions/limacharlie/git-sync.md',
    'ext-yara-manager.md': '5-integrations/extensions/limacharlie/yara-manager.md',
    'ext-yara.md': '5-integrations/extensions/third-party/yara.md',
    'Third-Party_Extensions/ext-yara.md': '5-integrations/extensions/third-party/yara.md',

    # Platform Management
    'Platform_Management/index.md': '7-administration/index.md',
    'Platform_Management/Config_Hive/config-hive-secrets.md': '7-administration/config-hive/secrets.md',
    'Platform_Management/Access_and_Permissions/api-keys.md': '7-administration/access/api-keys.md',
    'Platform_Management/Access_and_Permissions/reference-permissions.md': '7-administration/access/permissions.md',

    # Query Console
    'Query_Console/index.md': '4-data-queries/index.md',
    'Query_Console/lcql-examples.md': '4-data-queries/lcql-examples.md',

    # FAQ
    'FAQ/index.md': '8-reference/faq/index.md',

    # SDKs
    'go-sdk/README.md': '6-developer-guide/sdks/go-sdk.md',
    'python-sdk/README.md': '6-developer-guide/sdks/python-sdk.md',
    'sdk/index.md': '6-developer-guide/sdks/index.md',

    # Reference file name corrections
    'auth-resource-locator.md': '8-reference/authentication-resource-locator.md',
    'detection-operators.md': '8-reference/detection-logic-operators.md',
    'sensor-selectors.md': '8-reference/sensor-selector-expressions.md',
    'template-strings.md': '4-data-queries/template-strings.md',

    # Artifacts
    'artifacts.md': '5-integrations/extensions/limacharlie/artifact.md',

    # Developer guide extensions
    'extensions/building-the-user-interface.md': '6-developer-guide/extensions/building-the-user-interface.md',
    'extensions/developer-grant-program.md': '6-developer-guide/grant-program.md',
}

# Additional patterns for absolute-style links
ABSOLUTE_PATTERNS = {
    '/v2/docs/events': '4-data-queries/events/index.md',
    '/v2/docs/config-hive': '7-administration/config-hive/index.md',
    '/docs/detection-and-response': '3-detection-response/index.md',
    '/Platform_Management/': '7-administration/',
}


def find_markdown_files(docs_dir: Path) -> List[Path]:
    """Find all markdown files."""
    return list(docs_dir.rglob("*.md"))


def fix_link(link: str, file_path: Path) -> Tuple[str, bool]:
    """
    Attempt to fix a broken link.
    Returns (fixed_link, was_changed).
    """
    original = link

    # Handle absolute-style links
    for pattern, replacement in ABSOLUTE_PATTERNS.items():
        if pattern in link:
            # Convert to relative path from current file
            return replacement, True

    # Normalize the link path
    normalized = link.replace('../', '').replace('./', '')

    # Remove limacharlie/doc/ prefix if present
    if 'limacharlie/doc/' in normalized:
        normalized = normalized.split('limacharlie/doc/')[-1]

    # Check against mappings
    for old_pattern, new_path in PATH_MAPPINGS.items():
        if old_pattern in normalized or normalized.endswith(old_pattern):
            # Calculate relative path from current file to new location
            current_dir = file_path.parent
            target = DOCS_DIR / new_path

            try:
                rel_path = os.path.relpath(target, current_dir)
                return rel_path, True
            except ValueError:
                return new_path, True

    return link, False


def fix_links_in_file(file_path: Path, dry_run: bool = True) -> List[Tuple[str, str]]:
    """
    Fix broken links in a single file.
    Returns list of (old_link, new_link) changes.
    """
    changes = []
    content = file_path.read_text(encoding='utf-8')
    new_content = content

    # Find all markdown links
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'

    def replace_link(match):
        text = match.group(1)
        link = match.group(2)

        # Skip external links, anchors, mailto
        if link.startswith(('http://', 'https://', 'mailto:', '#')):
            return match.group(0)

        # Split anchor if present
        anchor = ''
        if '#' in link:
            link, anchor = link.split('#', 1)
            anchor = '#' + anchor

        fixed_link, changed = fix_link(link, file_path)

        if changed:
            changes.append((link, fixed_link))
            return f'[{text}]({fixed_link}{anchor})'

        return match.group(0)

    new_content = re.sub(pattern, replace_link, content)

    if changes and not dry_run:
        file_path.write_text(new_content, encoding='utf-8')

    return changes


def main():
    parser = argparse.ArgumentParser(description='Fix broken internal links')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes')
    parser.add_argument('--execute', action='store_true', help='Apply fixes')

    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        parser.print_help()
        return

    dry_run = not args.execute

    print("=" * 60)
    print("Fix Broken Internal Links")
    print("=" * 60)
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print()

    all_changes = []
    files_changed = 0

    for md_file in find_markdown_files(DOCS_DIR):
        changes = fix_links_in_file(md_file, dry_run)
        if changes:
            files_changed += 1
            rel_path = md_file.relative_to(DOCS_DIR)
            print(f"\n{rel_path}:")
            for old, new in changes[:5]:  # Show first 5 per file
                print(f"  {old}")
                print(f"    → {new}")
            if len(changes) > 5:
                print(f"  ... and {len(changes) - 5} more")
            all_changes.extend(changes)

    print()
    print("=" * 60)
    print(f"Files with changes: {files_changed}")
    print(f"Total links fixed: {len(all_changes)}")

    if dry_run:
        print("\nThis was a dry run. Use --execute to apply changes.")
    else:
        print("\nChanges applied!")


if __name__ == '__main__':
    main()
