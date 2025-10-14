#!/usr/bin/env python3
"""
Phase 5: Verify completeness and generate final output files.

Ensures all discovered pages were processed and creates:
- INDEX.md: Navigation file organized by category
- COMBINED.md: All documentation in a single file
- verification_report.json: Detailed processing report
"""
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

import config
from utils import (
    log, log_error, log_success, log_warning,
    load_json, save_json, sanitize_filename
)


class DocumentationVerifier:
    """Verifies completeness and generates final outputs."""

    def __init__(self):
        self.discovered_pages = {}
        self.processed_files = set()
        self.missing_pages = []
        self.verification_report = {}

    def load_discovered_pages(self):
        """Load the list of discovered pages."""
        if not config.DISCOVERED_PAGES_FILE.exists():
            log_error(f"Discovered pages file not found: {config.DISCOVERED_PAGES_FILE}")
            sys.exit(1)

        self.discovered_pages = load_json(config.DISCOVERED_PAGES_FILE)
        log(f"Loaded {len(self.discovered_pages)} discovered pages")

    def check_processed_files(self):
        """Check which pages were successfully processed."""
        if not config.CLEANED_MARKDOWN_DIR.exists():
            log_error(f"Cleaned markdown directory not found: {config.CLEANED_MARKDOWN_DIR}")
            sys.exit(1)

        # Get all processed files
        cleaned_files = list(config.CLEANED_MARKDOWN_DIR.glob("*.md"))
        self.processed_files = {f.stem for f in cleaned_files}

        log(f"Found {len(self.processed_files)} processed files")

        # Check for missing pages
        for url, info in self.discovered_pages.items():
            slug = info['slug']
            expected_filename = sanitize_filename(slug)

            if expected_filename not in self.processed_files:
                self.missing_pages.append({
                    "url": url,
                    "slug": slug,
                    "title": info['title']
                })

        if self.missing_pages:
            log_warning(f"Found {len(self.missing_pages)} missing pages:")
            for missing in self.missing_pages[:10]:  # Show first 10
                log(f"  - {missing['title']} ({missing['slug']})")
            if len(self.missing_pages) > 10:
                log(f"  ... and {len(self.missing_pages) - 10} more")
        else:
            log_success("All discovered pages were processed!")

    def categorize_pages(self) -> Dict[str, List[Dict]]:
        """
        Categorize pages based on their slugs.
        Returns a dictionary of category -> list of pages.
        """
        categories = defaultdict(list)

        for filename in sorted(self.processed_files):
            # Find corresponding page info
            page_info = None
            for url, info in self.discovered_pages.items():
                if sanitize_filename(info['slug']) == filename:
                    page_info = info
                    break

            if not page_info:
                # Unknown page, put in "other"
                page_info = {
                    "title": filename.replace('-', ' ').title(),
                    "slug": filename,
                    "url": "unknown"
                }

            # Categorize based on keywords in slug
            slug = filename.lower()
            category = "Other"

            if any(x in slug for x in ['quickstart', 'getting-started', 'what-is', 'use-case']):
                category = "Getting Started"
            elif any(x in slug for x in ['sensor', 'agent', 'install', 'deploy']):
                category = "Sensors & Agents"
            elif any(x in slug for x in ['event', 'telemetry', 'edr']):
                category = "Events & Telemetry"
            elif any(x in slug for x in ['query', 'lcql', 'search']):
                category = "Query & Search"
            elif any(x in slug for x in ['detection', 'rule', 'response', 'replay']):
                category = "Detection & Response"
            elif any(x in slug for x in ['platform', 'api', 'sdk', 'adapter']):
                category = "Platform & API"
            elif any(x in slug for x in ['output', 'siem', 'export']):
                category = "Outputs & Integrations"
            elif any(x in slug for x in ['add-on', 'extension', 'integration']):
                category = "Add-ons & Extensions"
            elif any(x in slug for x in ['tutorial', 'guide', 'how-to']):
                category = "Tutorials & Guides"
            elif 'faq' in slug:
                category = "FAQ"
            elif 'release' in slug:
                category = "Release Notes"

            categories[category].append({
                "filename": filename,
                "title": page_info.get('title', filename),
                "slug": page_info.get('slug', filename),
                "url": page_info.get('url', '')
            })

        return dict(categories)

    def generate_index(self, categories: Dict[str, List[Dict]]):
        """Generate INDEX.md with organized navigation."""
        log("Generating INDEX.md...")

        with open(config.INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write("# LimaCharlie Documentation Index\n\n")
            f.write("Complete documentation for LimaCharlie, organized by category.\n\n")
            f.write(f"**Total Pages:** {len(self.processed_files)}\n\n")
            f.write("---\n\n")

            # Table of contents
            f.write("## Categories\n\n")
            for category in sorted(categories.keys()):
                anchor = category.lower().replace(' ', '-').replace('&', 'and')
                count = len(categories[category])
                f.write(f"- [{category}](#{anchor}) ({count} pages)\n")
            f.write("\n---\n\n")

            # Detailed sections
            for category in sorted(categories.keys()):
                f.write(f"## {category}\n\n")

                for page in sorted(categories[category], key=lambda x: x['title']):
                    f.write(f"### {page['title']}\n\n")
                    f.write(f"- **File:** `{page['filename']}.md`\n")
                    if page['url'] and page['url'] != 'unknown':
                        f.write(f"- **Source:** {page['url']}\n")
                    f.write("\n")

                f.write("---\n\n")

        log_success(f"Generated INDEX.md: {config.INDEX_FILE}")

    def generate_combined(self, categories: Dict[str, List[Dict]]):
        """Generate COMBINED.md with all documentation."""
        log("Generating COMBINED.md...")

        with open(config.COMBINED_FILE, 'w', encoding='utf-8') as f:
            f.write("# LimaCharlie Complete Documentation\n\n")
            f.write("This file contains all LimaCharlie documentation in a single document.\n\n")
            f.write(f"**Generated from {len(self.processed_files)} documentation pages**\n\n")
            f.write("---\n\n")

            # Write all pages organized by category
            for category in sorted(categories.keys()):
                f.write(f"# {category}\n\n")

                for page in sorted(categories[category], key=lambda x: x['title']):
                    # Read the cleaned markdown file
                    md_path = config.CLEANED_MARKDOWN_DIR / f"{page['filename']}.md"

                    if not md_path.exists():
                        log_warning(f"Missing file for {page['filename']}")
                        continue

                    with open(md_path, 'r', encoding='utf-8') as md_file:
                        content = md_file.read().strip()

                    f.write(f"{content}\n\n")
                    f.write("---\n\n")

        log_success(f"Generated COMBINED.md: {config.COMBINED_FILE}")

    def generate_verification_report(self):
        """Generate detailed verification report."""
        self.verification_report = {
            "total_discovered": len(self.discovered_pages),
            "total_processed": len(self.processed_files),
            "missing_count": len(self.missing_pages),
            "missing_pages": self.missing_pages,
            "completion_rate": f"{(len(self.processed_files) / len(self.discovered_pages) * 100):.1f}%"
                if self.discovered_pages else "0%",
            "output_files": {
                "index": str(config.INDEX_FILE),
                "combined": str(config.COMBINED_FILE),
                "cleaned_markdown_dir": str(config.CLEANED_MARKDOWN_DIR)
            }
        }

        save_json(self.verification_report, config.VERIFICATION_REPORT_FILE)
        log_success(f"Generated verification report: {config.VERIFICATION_REPORT_FILE}")

    def verify_all(self):
        """Run complete verification process."""
        log("Starting verification...")

        self.load_discovered_pages()
        self.check_processed_files()

        categories = self.categorize_pages()
        log(f"Organized into {len(categories)} categories")

        self.generate_index(categories)
        self.generate_combined(categories)
        self.generate_verification_report()

        # Final summary
        log("\n" + "="*60)
        log("VERIFICATION SUMMARY")
        log("="*60)
        log(f"Discovered pages: {self.verification_report['total_discovered']}")
        log(f"Processed pages:  {self.verification_report['total_processed']}")
        log(f"Missing pages:    {self.verification_report['missing_count']}")
        log(f"Completion rate:  {self.verification_report['completion_rate']}")
        log("="*60)

        if self.missing_pages:
            log_warning(f"{len(self.missing_pages)} pages were not processed")
            return False
        else:
            log_success("All discovered pages were successfully processed!")
            return True


def main():
    """Main entry point."""

    verifier = DocumentationVerifier()
    success = verifier.verify_all()

    if not success:
        log_warning("Verification found issues - check the report")
        return 1

    log_success("\nPipeline complete! Output files:")
    log(f"  - Index:    {config.INDEX_FILE}")
    log(f"  - Combined: {config.COMBINED_FILE}")
    log(f"  - Cleaned:  {config.CLEANED_MARKDOWN_DIR}")
    log(f"  - Report:   {config.VERIFICATION_REPORT_FILE}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
