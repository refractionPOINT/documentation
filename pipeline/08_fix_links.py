#!/usr/bin/env python3
"""
Phase 8: Fix Documentation Links

Replaces all Document360 URL references with relative local markdown file paths.
This makes the documentation self-contained and suitable for AI consumption.
"""

import sys
from pathlib import Path

import config
from utils import (
    log, log_error, log_success, log_warning,
    save_json, ProgressTracker
)
from link_replacer import LinkReplacer


def main():
    """Main entry point for Phase 8."""

    log("=" * 80)
    log("PHASE 8: Fix Documentation Links")
    log("=" * 80)

    # Check that topics directory exists
    if not config.TOPICS_DIR.exists():
        log_error(f"Topics directory not found: {config.TOPICS_DIR}")
        log_error("Please run Phase 6 (synthesis) first")
        sys.exit(1)

    # Find all markdown files in topics directory
    topic_files = list(config.TOPICS_DIR.rglob("*.md"))

    if not topic_files:
        log_error(f"No markdown files found in {config.TOPICS_DIR}")
        sys.exit(1)

    log(f"Found {len(topic_files)} topic files to process")

    # Initialize link replacer
    log("Initializing link replacer...")
    replacer = LinkReplacer()

    # Process all files
    log("Processing files...")
    progress = ProgressTracker(len(topic_files), "Fixing links")

    for file_path in topic_files:
        replacer.process_file(file_path)
        progress.update()

    progress.complete()

    # Get statistics
    stats = replacer.get_stats()

    # Save report
    report_file = config.METADATA_DIR / "link_replacement_report.json"
    save_json(stats, report_file)

    # Report results
    log_success(f"Link replacement complete!")
    log(f"Total replacements made: {stats['total_replacements']}")
    log(f"URL mappings used: {stats['url_mappings']}")
    log(f"Slug mappings used: {stats['slug_mappings']}")

    if stats['unresolved_count'] > 0:
        log_warning(f"Unresolved links: {stats['unresolved_count']}")
        log("Unresolved links saved to report file")

        # Show first few unresolved links
        if stats['unresolved_links']:
            log("Sample unresolved links:")
            for link in list(stats['unresolved_links'])[:10]:
                log(f"  - {link}")

    log(f"Detailed report saved to: {report_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
