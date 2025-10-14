#!/usr/bin/env python3
"""
Phase 3: Convert HTML to raw Markdown using markitdown.

This phase does NO cleaning - just raw HTML to Markdown conversion.
Cleaning is done by LLMs in phase 4.
"""
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

import config
from utils import (
    log, log_error, log_success, log_warning,
    ensure_dir, ProgressTracker
)


class MarkdownConverter:
    """Converts HTML files to raw Markdown using markitdown."""

    def __init__(self):
        self.successful = 0
        self.failed = 0

        # Check if markitdown is available
        try:
            result = subprocess.run(
                ['markitdown', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            log(f"Using markitdown: {result.stdout.strip()}")
        except Exception as e:
            log_error(f"markitdown not found or not working: {e}")
            log_error("Install with: pip install markitdown")
            sys.exit(1)

    def convert_file(self, html_path: Path) -> bool:
        """
        Convert a single HTML file to Markdown.

        Args:
            html_path: Path to HTML file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine output path
            relative_name = html_path.stem  # filename without extension
            md_path = config.RAW_MARKDOWN_DIR / f"{relative_name}.md"

            # Skip if already converted
            if md_path.exists():
                log(f"Skipping (already exists): {relative_name}")
                return True

            # Run markitdown
            result = subprocess.run(
                ['markitdown', str(html_path)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                log_error(f"markitdown failed for {html_path}: {result.stderr}")
                return False

            # Save the converted markdown
            ensure_dir(config.RAW_MARKDOWN_DIR)
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(result.stdout)

            log(f"Converted: {relative_name} ({len(result.stdout)} bytes)")
            return True

        except subprocess.TimeoutExpired:
            log_error(f"Timeout converting {html_path}")
            return False
        except Exception as e:
            log_error(f"Error converting {html_path}: {e}")
            return False

    def convert_all(self, html_files: list, max_workers: int = None) -> dict:
        """
        Convert all HTML files to Markdown in parallel.

        Args:
            html_files: List of HTML file paths
            max_workers: Number of parallel workers

        Returns:
            Dictionary with conversion statistics
        """
        if max_workers is None:
            max_workers = config.MAX_PARALLEL_WORKERS

        log(f"Converting {len(html_files)} HTML files to Markdown with {max_workers} workers...")

        ensure_dir(config.RAW_MARKDOWN_DIR)
        progress = ProgressTracker(len(html_files), "Converting HTML→MD")

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all conversion jobs
            future_to_file = {
                executor.submit(self.convert_file, html_path): html_path
                for html_path in html_files
            }

            # Process completed jobs
            for future in as_completed(future_to_file):
                html_path = future_to_file[future]
                try:
                    success = future.result()
                    if success:
                        self.successful += 1
                    else:
                        self.failed += 1
                except Exception as e:
                    log_error(f"Exception converting {html_path}: {e}")
                    self.failed += 1

                progress.update()

        progress.complete()

        return {
            "successful": self.successful,
            "failed": self.failed,
            "total": len(html_files)
        }


def main():
    """Main entry point."""

    # Find all HTML files
    if not config.RAW_HTML_DIR.exists():
        log_error(f"HTML directory not found: {config.RAW_HTML_DIR}")
        log_error("Please run 02_fetch.py first")
        sys.exit(1)

    html_files = list(config.RAW_HTML_DIR.glob("*.html"))

    if not html_files:
        log_error(f"No HTML files found in {config.RAW_HTML_DIR}")
        sys.exit(1)

    log(f"Found {len(html_files)} HTML files to convert")

    # Convert all files
    converter = MarkdownConverter()
    results = converter.convert_all(html_files)

    # Report results
    log_success(f"Conversion complete: {results['successful']} successful, {results['failed']} failed")

    if results['failed'] > 0:
        log_warning(f"{results['failed']} files failed to convert")

    if results['successful'] == 0:
        log_error("No files were successfully converted")
        sys.exit(1)

    # Count converted files
    md_files = list(config.RAW_MARKDOWN_DIR.glob("*.md"))
    log_success(f"Total Markdown files in {config.RAW_MARKDOWN_DIR}: {len(md_files)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
