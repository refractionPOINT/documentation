#!/usr/bin/env python3
"""
Phase 1: Discover all documentation pages from docs.limacharlie.io

Uses Algolia search API (Document360's search backend) with fallback to web crawling.
This ensures we discover ALL pages, not just the ones we know about.
"""
import requests
import sys
from typing import Dict, List, Set
from urllib.parse import urljoin
from bs4 import BeautifulSoup

import config
from utils import log, log_error, log_success, log_warning, save_json, ensure_dir


class DocumentationDiscoverer:
    """Discovers all documentation pages using multiple strategies."""

    def __init__(self):
        self.discovered_pages: Dict[str, Dict] = {}
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': config.USER_AGENT})

    def discover_via_algolia(self) -> int:
        """
        Discover pages via Algolia search API.
        Document360 uses Algolia for search, so we can query it to get all indexed pages.
        """
        log("Discovering documentation via Algolia API...")

        try:
            # Algolia browse endpoint to get all documents
            url = f"https://{config.ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/{config.ALGOLIA_INDEX_NAME}/browse"

            headers = {
                "X-Algolia-Application-Id": config.ALGOLIA_APP_ID,
                "X-Algolia-API-Key": config.ALGOLIA_API_KEY,
                "Content-Type": "application/json",
            }

            # Start with empty cursor to get first batch
            cursor = None
            total_found = 0

            while True:
                params = {
                    "hitsPerPage": 1000,
                }
                if cursor:
                    params["cursor"] = cursor

                response = self.session.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=config.REQUEST_TIMEOUT_SECONDS
                )

                if response.status_code != 200:
                    log_warning(f"Algolia API returned status {response.status_code}")
                    return total_found

                data = response.json()
                hits = data.get("hits", [])

                for hit in hits:
                    # Extract page information from Algolia document
                    page_url = hit.get("url", "")
                    title = hit.get("title", "") or hit.get("pageTitle", "")

                    # Only include actual documentation pages
                    if "/docs/" in page_url and config.DOCS_BASE_URL in page_url:
                        # Normalize URL
                        if not page_url.startswith("http"):
                            page_url = urljoin(config.DOCS_BASE_URL, page_url)

                        # Remove URL fragments and query params
                        clean_url = page_url.split('#')[0].split('?')[0]

                        if clean_url not in self.discovered_pages:
                            self.discovered_pages[clean_url] = {
                                "url": clean_url,
                                "title": title,
                                "discovered_via": "algolia",
                                "slug": self._extract_slug(clean_url),
                            }
                            total_found += 1

                # Check if there are more results
                cursor = data.get("cursor")
                if not cursor:
                    break

                log(f"Algolia: Found {total_found} pages so far...")

            log_success(f"Discovered {total_found} pages via Algolia")
            return total_found

        except Exception as e:
            log_error(f"Algolia discovery failed: {e}")
            return 0

    def discover_via_crawl(self) -> int:
        """
        Fallback: Discover pages by crawling the documentation site.
        Starts from the main docs page and follows all internal /docs/ links.
        """
        log("Discovering documentation via web crawling (fallback)...")

        visited: Set[str] = set()
        to_visit: Set[str] = {config.DOCS_URL}
        total_found = 0

        while to_visit and len(visited) < 500:  # Safety limit
            url = to_visit.pop()

            if url in visited:
                continue

            visited.add(url)

            try:
                response = self.session.get(
                    url,
                    timeout=config.REQUEST_TIMEOUT_SECONDS
                )

                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract title
                title_tag = soup.find('h1') or soup.find('title')
                title = title_tag.get_text().strip() if title_tag else ""

                # Store this page if it's a docs page
                clean_url = url.split('#')[0].split('?')[0]
                if "/docs/" in clean_url and clean_url not in self.discovered_pages:
                    self.discovered_pages[clean_url] = {
                        "url": clean_url,
                        "title": title,
                        "discovered_via": "crawl",
                        "slug": self._extract_slug(clean_url),
                    }
                    total_found += 1

                # Find all links to other documentation pages
                for link in soup.find_all('a', href=True):
                    href = link['href']

                    # Convert relative URLs to absolute
                    absolute_url = urljoin(url, href)

                    # Only follow documentation links on the same domain
                    if (config.DOCS_BASE_URL in absolute_url and
                        "/docs/" in absolute_url and
                        absolute_url not in visited):
                        # Clean the URL
                        clean_link = absolute_url.split('#')[0].split('?')[0]
                        to_visit.add(clean_link)

                if total_found % 10 == 0:
                    log(f"Crawl: Found {total_found} pages, visited {len(visited)}")

            except Exception as e:
                log_warning(f"Error crawling {url}: {e}")
                continue

        log_success(f"Discovered {total_found} pages via crawling")
        return total_found

    def _extract_slug(self, url: str) -> str:
        """Extract a clean slug from the URL."""
        if "/docs/" in url:
            slug = url.split("/docs/")[-1].rstrip('/')
            return slug if slug else "index"
        return "unknown"

    def discover_all(self) -> Dict[str, Dict]:
        """
        Run all discovery methods and return combined results.
        """
        log("Starting documentation discovery...")

        # Try Algolia first (most reliable)
        algolia_count = self.discover_via_algolia()

        # If Algolia didn't find many pages, try crawling
        if algolia_count < 10:
            log_warning("Algolia found few pages, trying crawl fallback...")
            self.discover_via_crawl()

        total_pages = len(self.discovered_pages)

        if total_pages == 0:
            log_error("No documentation pages discovered!")
            return {}

        log_success(f"Discovery complete: {total_pages} unique pages found")

        return self.discovered_pages


def main():
    """Main entry point."""
    ensure_dir(config.METADATA_DIR)

    discoverer = DocumentationDiscoverer()
    pages = discoverer.discover_all()

    if not pages:
        log_error("Failed to discover any documentation pages")
        sys.exit(1)

    # Save results
    save_json(pages, config.DISCOVERED_PAGES_FILE)

    # Print summary
    log_success(f"Saved {len(pages)} discovered pages to {config.DISCOVERED_PAGES_FILE}")

    # Show some examples
    log("\nExample discovered pages:")
    for i, (url, info) in enumerate(list(pages.items())[:5]):
        log(f"  {i+1}. {info['title']}")
        log(f"     URL: {url}")
        log(f"     Slug: {info['slug']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
