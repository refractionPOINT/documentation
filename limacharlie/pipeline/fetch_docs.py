#!/usr/bin/env python3
"""
Script to fetch all LimaCharlie documentation from docs.limacharlie.io
and convert it to markdown format.

This script:
1. Extracts API credentials from the documentation page source
2. Fetches all public articles via the Algolia API
3. Downloads each article's HTML content
4. Converts to markdown using markdownify
5. Saves in a directory structure based on breadcrumbs

Dependencies:
- requests
- beautifulsoup4
- markdownify
"""

import os
import re
import sys
import json
import time
import random
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from markdownify import markdownify
from pathlib import Path
from bs4 import BeautifulSoup

# Configuration
BASE_URL = "https://docs.limacharlie.io"
DOCS_URL = f"{BASE_URL}/docs"
OUTPUT_DIR = "./limacharlie/raw_markdown"
RATE_LIMIT_DELAY = 0.05  # seconds between requests (reduced for concurrent fetching)
MAX_WORKERS = 10  # number of concurrent download threads
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
MAX_RETRIES_RATE_LIMIT = 7  # higher retry limit specifically for 429 rate limit errors
MAX_BACKOFF_TIME = 60  # maximum backoff time in seconds (cap for exponential backoff)


class LimaCharlieFetcher:
    """Fetches and converts LimaCharlie documentation"""

    def __init__(self):
        self.algolia_app_id = None
        self.algolia_api_key = None
        self.algolia_index = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        # markdownify doesn't need configuration - it's just a function

        # Thread-safe counters for concurrent processing
        self.lock = threading.Lock()
        self.success_count = 0
        self.fail_count = 0

    def extract_api_credentials(self):
        """Extract Algolia API credentials from the docs page source"""
        print("Extracting API credentials from docs page...")

        try:
            response = self.session.get(DOCS_URL, timeout=30)
            response.raise_for_status()
            content = response.text

            # Extract algoliaAppId
            app_id_match = re.search(r"algoliaAppId\s*:\s*['\"]([^'\"]+)['\"]", content)
            if app_id_match:
                self.algolia_app_id = app_id_match.group(1)

            # Extract algoliaSearchKey (with filters)
            api_key_match = re.search(r"algoliaSearchKey\s*:\s*['\"]([^'\"]+)['\"]", content)
            if api_key_match:
                self.algolia_api_key = api_key_match.group(1)

            # Extract algoliaArticlesIndexId
            index_match = re.search(r"algoliaArticlesIndexId\s*:\s*['\"]([^'\"]+)['\"]", content)
            if index_match:
                self.algolia_index = index_match.group(1)

            if not all([self.algolia_app_id, self.algolia_api_key, self.algolia_index]):
                raise ValueError("Failed to extract all required API credentials")

            print(f"  App ID: {self.algolia_app_id}")
            print(f"  Index: {self.algolia_index}")
            print(f"  API Key: {self.algolia_api_key[:20]}... (truncated)")

            return True

        except Exception as e:
            print(f"Error extracting API credentials: {e}")
            return False

    def fetch_all_articles(self):
        """Fetch all article metadata from Algolia API"""
        print("\nFetching all articles from Algolia API...")

        url = f"https://{self.algolia_app_id}-dsn.algolia.net/1/indexes/{self.algolia_index}/query"

        headers = {
            'Content-Type': 'application/json',
            'X-Algolia-Application-Id': self.algolia_app_id,
            'X-Algolia-API-Key': self.algolia_api_key
        }

        payload = {
            'query': '',
            'hitsPerPage': 1000,  # Get all articles at once
            'attributesToRetrieve': ['title', 'slug', 'breadcrumb', 'articleId', 'isCategory']
        }

        try:
            response = self.session.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            articles = [hit for hit in data.get('hits', []) if not hit.get('isCategory', False)]

            print(f"  Found {len(articles)} articles (filtered out categories)")
            print(f"  Total hits: {data.get('nbHits', 0)}")

            return articles

        except Exception as e:
            print(f"Error fetching articles: {e}")
            return []

    def sanitize_path(self, path_str):
        """Sanitize a path string to be filesystem-safe"""
        # Replace problematic characters
        path_str = re.sub(r'[<>:"|?*]', '', path_str)
        # Replace forward/back slashes with dashes (except for path separators)
        path_str = path_str.replace('\\', '-')
        # Replace spaces with underscores
        path_str = path_str.replace(' ', '_')
        return path_str.strip()

    def create_directory_structure(self, breadcrumb):
        """Create directory structure from breadcrumb string"""
        if not breadcrumb:
            return OUTPUT_DIR

        # Split breadcrumb by ' > ' separator
        parts = [self.sanitize_path(part.strip()) for part in breadcrumb.split(' > ')]

        # Build full path
        full_path = os.path.join(OUTPUT_DIR, *parts)
        os.makedirs(full_path, exist_ok=True)

        return full_path

    def fetch_article_html(self, slug, retry_count=0):
        """Fetch the HTML content for a specific article"""
        url = f"{BASE_URL}/docs/{slug}"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text

        except requests.exceptions.HTTPError as e:
            # Handle 404s specially - don't retry, just skip silently
            if e.response.status_code == 404:
                print(f"    Article not found (404), skipping")
                return None

            # Handle 429 (Too Many Requests) with exponential backoff and jitter
            if e.response.status_code == 429:
                if retry_count < MAX_RETRIES_RATE_LIMIT:
                    # Exponential backoff: base_delay * (2 ^ retry_count)
                    base_delay = RETRY_DELAY
                    backoff_time = base_delay * (2 ** retry_count)

                    # Add jitter (randomization) to prevent thundering herd
                    # Jitter is up to 50% of the backoff time
                    jitter = random.uniform(0, backoff_time * 0.5)

                    # Calculate total wait time and cap at maximum
                    wait_time = min(backoff_time + jitter, MAX_BACKOFF_TIME)

                    print(f"    Rate limited (429), waiting {wait_time:.2f}s before retry {retry_count + 1}/{MAX_RETRIES_RATE_LIMIT}")
                    time.sleep(wait_time)
                    return self.fetch_article_html(slug, retry_count + 1)
                else:
                    print(f"    Failed after {MAX_RETRIES_RATE_LIMIT} retries (rate limited)")
                    return None

            # For other HTTP errors, retry as usual
            if retry_count < MAX_RETRIES:
                print(f"    Retry {retry_count + 1}/{MAX_RETRIES} after HTTP error: {e}")
                time.sleep(RETRY_DELAY)
                return self.fetch_article_html(slug, retry_count + 1)
            else:
                print(f"    Failed after {MAX_RETRIES} retries: {e}")
                return None

        except Exception as e:
            # For non-HTTP errors (timeouts, connection errors, etc.), retry as usual
            if retry_count < MAX_RETRIES:
                print(f"    Retry {retry_count + 1}/{MAX_RETRIES} after error: {e}")
                time.sleep(RETRY_DELAY)
                return self.fetch_article_html(slug, retry_count + 1)
            else:
                print(f"    Failed after {MAX_RETRIES} retries: {e}")
                return None

    def extract_article_content(self, html_content):
        """Extract the main article content from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Try to find the main content area
        # Based on the structure: .content_block_text
        content = soup.find(class_='content_block_text')

        if not content:
            # Fallback to other possible selectors
            content = soup.find('article') or soup.find('main')

        if not content:
            return html_content  # Return full HTML as fallback

        return str(content)

    def convert_html_to_markdown(self, html_content, article_metadata):
        """Convert HTML page content to markdown"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract the content_block div which contains the article
            content_block = soup.find('div', class_='content_block')

            if not content_block:
                print(f"    Warning: content_block not found, trying fallbacks...")
                content_block = soup.find('article') or soup.find('main')

            if not content_block:
                print(f"    Error: Could not find article content")
                return None

            # Use markdownify to convert HTML to Markdown
            # heading_style='ATX' uses # style headers instead of underlines
            markdown = markdownify(str(content_block), heading_style='ATX')

            # Add metadata header
            header = f"""---
title: {article_metadata.get('title', 'Unknown')}
slug: {article_metadata.get('slug', 'unknown')}
breadcrumb: {article_metadata.get('breadcrumb', '')}
source: {BASE_URL}/docs/{article_metadata.get('slug', '')}
articleId: {article_metadata.get('articleId', '')}
---

"""
            return header + markdown

        except Exception as e:
            print(f"    Error converting to markdown: {e}")
            import traceback
            traceback.print_exc()
            return None

    def process_article(self, article, index, total):
        """Process a single article: fetch HTML, convert to markdown, and save"""
        slug = article.get('slug', '')
        title = article.get('title', 'Unknown')
        breadcrumb = article.get('breadcrumb', '')

        print(f"[{index}/{total}] Processing: {title}")
        print(f"  Slug: {slug}")
        print(f"  Path: {breadcrumb}")

        # Create directory structure
        dir_path = self.create_directory_structure(breadcrumb)

        # Determine output filename
        safe_slug = self.sanitize_path(slug)
        output_file = os.path.join(dir_path, f"{safe_slug}.md")

        # Skip if already exists (for resume capability)
        if os.path.exists(output_file):
            print(f"  ✓ Already exists, skipping")
            return True

        # Fetch HTML content from the actual page
        html_content = self.fetch_article_html(slug)
        if not html_content:
            print(f"  ✗ Failed to fetch HTML")
            return False

        # Convert HTML to markdown
        try:
            markdown = self.convert_html_to_markdown(html_content, article)

            if not markdown or len(markdown.strip()) < 50:
                print(f"  ⚠ No meaningful content extracted, skipping")
                return False

            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"  ✓ Saved to: {output_file}")
            return True

        except Exception as e:
            print(f"  ✗ Error creating/saving file: {e}")
            import traceback
            traceback.print_exc()
            return False

    def process_article_threadsafe(self, article_with_index):
        """Thread-safe wrapper for process_article with rate limiting"""
        article, idx, total = article_with_index
        try:
            # Rate limiting (spread out requests)
            if RATE_LIMIT_DELAY > 0:
                time.sleep(RATE_LIMIT_DELAY)

            success = self.process_article(article, idx, total)

            # Update counters thread-safely
            with self.lock:
                if success:
                    self.success_count += 1
                else:
                    self.fail_count += 1

            return success
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            with self.lock:
                self.fail_count += 1
            return False

    def enhance_formatting(self, content):
        """Enhance plain text content with basic markdown formatting"""
        import html

        # Unescape HTML entities
        content = html.unescape(content)

        lines = content.split('\n')
        enhanced_lines = []
        in_code_block = False
        code_block_lines = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            indent = len(line) - len(line.lstrip())

            # Detect code blocks (lines that start with 2+ spaces)
            is_code_line = indent >= 2 and stripped

            if is_code_line:
                if not in_code_block:
                    in_code_block = True
                    code_block_lines = [line]
                else:
                    code_block_lines.append(line)
            else:
                # End of code block
                if in_code_block:
                    # Only wrap in ``` if we have multiple lines
                    if len(code_block_lines) > 1:
                        enhanced_lines.append('```')
                        enhanced_lines.extend(code_block_lines)
                        enhanced_lines.append('```')
                    else:
                        enhanced_lines.extend(code_block_lines)
                    in_code_block = False
                    code_block_lines = []

                # Detect section headers: short standalone lines ending with space
                # and NOT starting with special chars, and followed by content
                is_likely_header = (stripped and
                                   line.endswith(' ') and
                                   3 < len(stripped) < 60 and
                                   not stripped.startswith(('  ', '-', '*', '>', '[', '{')) and
                                   i + 1 < len(lines) and
                                   lines[i + 1].strip() and
                                   not lines[i + 1].startswith('  '))

                if is_likely_header:
                    enhanced_lines.append(f'\n## {stripped}\n')
                else:
                    enhanced_lines.append(line)

        # Close any open code block
        if in_code_block and code_block_lines:
            if len(code_block_lines) > 1:
                enhanced_lines.append('```')
                enhanced_lines.extend(code_block_lines)
                enhanced_lines.append('```')
            else:
                enhanced_lines.extend(code_block_lines)

        return '\n'.join(enhanced_lines)

    def create_markdown_document(self, article_metadata):
        """Create a markdown document from article metadata and content"""
        title = article_metadata.get('title', 'Unknown')
        slug = article_metadata.get('slug', 'unknown')
        breadcrumb = article_metadata.get('breadcrumb', '')
        content = article_metadata.get('content', '')
        article_id = article_metadata.get('articleId', '')

        # Build metadata header
        header = f"""---
title: {title}
slug: {slug}
breadcrumb: {breadcrumb}
source: {BASE_URL}/docs/{slug}
articleId: {article_id}
---

"""

        # Enhance the plain text content with basic markdown formatting
        enhanced_content = self.enhance_formatting(content)

        return header + enhanced_content

    def run(self):
        """Main execution flow"""
        print("=" * 80)
        print("LimaCharlie Documentation Fetcher")
        print("=" * 80)

        # Step 1: Extract API credentials
        if not self.extract_api_credentials():
            print("\nFailed to extract API credentials. Exiting.")
            return 1

        # Step 2: Fetch all articles
        articles = self.fetch_all_articles()
        if not articles:
            print("\nNo articles found. Exiting.")
            return 1

        # Step 3: Process each article
        print(f"\nProcessing {len(articles)} articles...")
        print(f"Output directory: {os.path.abspath(OUTPUT_DIR)}")
        print("=" * 80)

        # Create output directory
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Reset counters
        self.success_count = 0
        self.fail_count = 0

        # Prepare articles with indices for parallel processing
        articles_with_indices = [(article, idx, len(articles)) for idx, article in enumerate(articles, 1)]

        # Process articles concurrently
        print(f"Using {MAX_WORKERS} concurrent workers for faster fetching...")
        print()

        try:
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                # Submit all tasks
                futures = {executor.submit(self.process_article_threadsafe, item): item for item in articles_with_indices}

                # Process completed tasks
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"  ✗ Thread exception: {e}")

        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Exiting...")

        # Summary
        print("\n" + "=" * 80)
        print("Summary:")
        print(f"  Total articles: {len(articles)}")
        print(f"  Successfully processed: {self.success_count}")
        print(f"  Failed: {self.fail_count}")
        print(f"  Output directory: {os.path.abspath(OUTPUT_DIR)}")
        print("=" * 80)

        return 0 if self.fail_count == 0 else 1


def main():
    fetcher = LimaCharlieFetcher()
    return fetcher.run()


if __name__ == "__main__":
    sys.exit(main())
