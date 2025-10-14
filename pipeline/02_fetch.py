#!/usr/bin/env python3
"""
Phase 2: Fetch HTML pages for all discovered documentation.

Downloads raw HTML from each discovered page URL.
"""
import requests
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import config
from utils import (
    log, log_error, log_success, log_warning,
    load_json, ensure_dir, sanitize_filename,
    ProgressTracker
)


class HTMLFetcher:
    """Fetches HTML content for documentation pages."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': config.USER_AGENT})
        self.successful = 0
        self.failed = 0

    def fetch_page(self, page_info: dict) -> bool:
        """
        Fetch a single page and save its HTML.

        Args:
            page_info: Dictionary with 'url', 'slug', and 'title'

        Returns:
            True if successful, False otherwise
        """
        url = page_info['url']
        slug = page_info['slug']

        try:
            # Create filename from slug
            filename = sanitize_filename(slug) + ".html"
            output_path = config.RAW_HTML_DIR / filename

            # Skip if already downloaded
            if output_path.exists():
                log(f"Skipping (already exists): {slug}")
                return True

            # Fetch the page
            response = self.session.get(
                url,
                timeout=config.REQUEST_TIMEOUT_SECONDS
            )
            response.raise_for_status()

            # Save HTML content
            ensure_dir(config.RAW_HTML_DIR)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response.text)

            log(f"Downloaded: {slug} ({len(response.text)} bytes)")

            # Be respectful - add delay between requests
            time.sleep(config.FETCH_DELAY_SECONDS)

            return True

        except Exception as e:
            log_error(f"Failed to fetch {url}: {e}")
            return False

    def fetch_all(self, pages: dict, max_workers: int = None) -> dict:
        """
        Fetch all pages using parallel workers.

        Args:
            pages: Dictionary of page_url -> page_info
            max_workers: Number of parallel workers (default from config)

        Returns:
            Dictionary with 'successful' and 'failed' counts
        """
        if max_workers is None:
            max_workers = config.MAX_PARALLEL_WORKERS

        log(f"Starting to fetch {len(pages)} pages with {max_workers} workers...")

        ensure_dir(config.RAW_HTML_DIR)
        progress = ProgressTracker(len(pages), "Fetching HTML")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all fetch jobs
            future_to_page = {
                executor.submit(self.fetch_page, page_info): page_url
                for page_url, page_info in pages.items()
            }

            # Process completed jobs
            for future in as_completed(future_to_page):
                page_url = future_to_page[future]
                try:
                    success = future.result()
                    if success:
                        self.successful += 1
                    else:
                        self.failed += 1
                except Exception as e:
                    log_error(f"Exception fetching {page_url}: {e}")
                    self.failed += 1

                progress.update()

        progress.complete()

        return {
            "successful": self.successful,
            "failed": self.failed,
            "total": len(pages)
        }


def main():
    """Main entry point."""

    # Load discovered pages
    if not config.DISCOVERED_PAGES_FILE.exists():
        log_error(f"Discovered pages file not found: {config.DISCOVERED_PAGES_FILE}")
        log_error("Please run 01_discover.py first")
        sys.exit(1)

    pages = load_json(config.DISCOVERED_PAGES_FILE)
    log(f"Loaded {len(pages)} discovered pages")

    # Fetch all pages
    fetcher = HTMLFetcher()
    results = fetcher.fetch_all(pages)

    # Report results
    log_success(f"Fetch complete: {results['successful']} successful, {results['failed']} failed")

    if results['failed'] > 0:
        log_warning(f"{results['failed']} pages failed to download")

    if results['successful'] == 0:
        log_error("No pages were successfully downloaded")
        sys.exit(1)

    # Count downloaded files
    html_files = list(config.RAW_HTML_DIR.glob("*.html"))
    log_success(f"Total HTML files in {config.RAW_HTML_DIR}: {len(html_files)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
