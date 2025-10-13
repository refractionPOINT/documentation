"""Documentation fetching and discovery."""
import time
import hashlib
import re
import json
from typing import Dict, List, Tuple, Optional
import requests
from bs4 import BeautifulSoup

# Import from parent package
try:
    from ..models import Page, DocumentStructure
    from ..config import Config
except ImportError:
    # Fallback for direct execution or testing
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from models import Page, DocumentStructure
    from config import Config


def _extract_algolia_credentials(config: Config) -> Optional[Tuple[str, str, str, str]]:
    """
    Extract Algolia credentials from the documentation page source.

    Document360 embeds these credentials in the page's layoutData JavaScript object.
    They are public, read-only keys that expire periodically.

    Returns tuple of (app_id, index_name, api_key, language_version_id) or None if extraction fails.
    """
    try:
        docs_url = f"{config.base_url}{config.docs_path}"
        headers = {'User-Agent': 'Mozilla/5.0 (LimaCharlie Documentation Bot)'}

        response = requests.get(docs_url, headers=headers, timeout=config.request_timeout)
        response.raise_for_status()

        # Find the layoutData JavaScript object in the page source
        match = re.search(r'var layoutData=(\{[^;]+\});', response.text)
        if not match:
            print("  Could not find layoutData in page source")
            return None

        # Parse the JavaScript object as JSON
        layout_data_str = match.group(1)
        # Fix JavaScript boolean/null to JSON
        layout_data_str = layout_data_str.replace("'", '"')
        layout_data_str = re.sub(r':\s*True', ': true', layout_data_str)
        layout_data_str = re.sub(r':\s*False', ': false', layout_data_str)
        layout_data_str = re.sub(r":\s*'([^']*)'", r': "\1"', layout_data_str)

        try:
            layout_data = json.loads(layout_data_str)
        except json.JSONDecodeError:
            # If JSON parsing fails, try regex extraction
            app_id_match = re.search(r'algoliaAppId["\']?\s*:\s*["\']([^"\']+)["\']', response.text)
            index_match = re.search(r'algoliaArticlesIndexId["\']?\s*:\s*["\']([^"\']+)["\']', response.text)
            key_match = re.search(r'algoliaSearchKey["\']?\s*:\s*["\']([^"\']+)["\']', response.text)

            if app_id_match and index_match and key_match:
                app_id = app_id_match.group(1)
                index_name = index_match.group(1)

                # Try to extract languageVersionId
                lang_version_match = re.search(r'languageVersionId["\']?\s*:\s*["\']([^"\']+)["\']', response.text)
                lang_version_id = lang_version_match.group(1) if lang_version_match else ""

                print(f"  Extracted Algolia credentials (via regex): {app_id}/{index_name} (lang: {lang_version_id})")
                return (app_id, index_name, key_match.group(1), lang_version_id)

            print("  Could not parse layoutData as JSON or extract via regex")
            return None

        # Extract Algolia credentials and language version
        app_id = layout_data.get('algoliaAppId')
        index_name = layout_data.get('algoliaArticlesIndexId')
        api_key = layout_data.get('algoliaSearchKey')
        lang_version_id = layout_data.get('languageVersionId', '')

        if not all([app_id, index_name, api_key]):
            print(f"  Missing Algolia credentials: app_id={bool(app_id)}, index={bool(index_name)}, key={bool(api_key)}")
            return None

        print(f"  Extracted Algolia credentials: {app_id}/{index_name} (lang: {lang_version_id})")
        return (app_id, index_name, api_key, lang_version_id)

    except Exception as e:
        print(f"  Error extracting Algolia credentials: {e}")
        return None


def _discover_via_algolia(config: Config) -> List[Page]:
    """
    Discover documentation using Algolia search API.

    Document360 sites use Algolia for search, which provides access to all articles.
    This bypasses the need to scrape JavaScript-rendered navigation.

    Credentials are automatically extracted from the page source.
    """
    # Extract credentials from page source (they expire periodically)
    credentials = _extract_algolia_credentials(config)
    if not credentials:
        print("  Could not extract Algolia credentials, discovery will fail")
        return []

    ALGOLIA_APP_ID, ALGOLIA_INDEX, ALGOLIA_API_KEY, LANGUAGE_VERSION_ID = credentials

    url = f"https://{ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/{ALGOLIA_INDEX}/query"

    headers = {
        'Content-Type': 'application/json',
        'X-Algolia-Application-Id': ALGOLIA_APP_ID,
        'X-Algolia-API-Key': ALGOLIA_API_KEY,
    }

    pages = []
    page_num = 0
    total_pages = 1  # Will be updated from first response

    while page_num < total_pages:
        payload = {
            'query': '',  # Empty query returns all articles
            'hitsPerPage': 100,
            'page': page_num
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=config.request_timeout)
            response.raise_for_status()
            data = response.json()

            hits = data.get('hits', [])
            total_pages = data.get('nbPages', 1)

            print(f"  Algolia page {page_num + 1}/{total_pages}: {len(hits)} articles")

            for hit in hits:
                # Filter out articles not from current version or that are deleted/draft/hidden
                article_lang_id = hit.get('languageId', '')
                if LANGUAGE_VERSION_ID and article_lang_id != LANGUAGE_VERSION_ID:
                    continue  # Skip articles from other versions

                # Skip deleted, draft, hidden, or unpublished articles
                if hit.get('isDeleted', False):
                    continue
                if hit.get('isDraft', False):
                    continue
                if hit.get('isHidden', False):
                    continue
                if hit.get('isUnpublished', False):
                    continue

                # Extract article details
                slug = hit.get('slug', '').strip('/')
                title = hit.get('title', 'Untitled')

                if not slug:
                    continue  # Skip articles without slugs

                # Build full URL
                url_path = f"/docs/{slug}"
                full_url = f"{config.base_url}{url_path}"

                page = Page(
                    url=full_url,
                    slug=slug,
                    title=title,
                    category=""  # Will be categorized later
                )
                pages.append(page)

            page_num += 1
            time.sleep(0.2)  # Be respectful between pagination requests

        except Exception as e:
            print(f"  Error fetching Algolia page {page_num}: {e}")
            break

    print(f"Found {len(pages)} pages via Algolia search (filtered to current version)")
    return pages


def discover_documentation_structure(config: Config, claude_client=None) -> DocumentStructure:
    """
    Dynamically discover all documentation pages from the website.

    Uses Algolia search API for Document360 sites (JavaScript-rendered navigation).

    Returns DocumentStructure with discovered pages organized by category.

    Args:
        config: Configuration
        claude_client: Optional Claude client for smart categorization
    """
    print("Discovering documentation structure...")

    structure = DocumentStructure()

    # Try Algolia discovery first (works for Document360 sites)
    try:
        algolia_pages = _discover_via_algolia(config)
        if algolia_pages:
            # Use Claude for smart categorization if available
            if claude_client:
                print("\nUsing Claude for semantic categorization...")
                try:
                    from . import categorize
                    structure.categories = categorize.categorize_pages_batch(
                        algolia_pages, claude_client, batch_size=100
                    )
                    print(f"✓ Categorized into {len(structure.categories)} categories")
                except Exception as e:
                    print(f"Warning: Claude categorization failed: {e}")
                    print("Falling back to rule-based categorization")
                    # Fallback to rule-based
                    for page in algolia_pages:
                        category = _categorize_page(page.slug)
                        if category not in structure.categories:
                            structure.categories[category] = []
                        structure.categories[category].append(page)
            else:
                # No Claude client, use rule-based
                for page in algolia_pages:
                    category = _categorize_page(page.slug)
                    if category not in structure.categories:
                        structure.categories[category] = []
                    structure.categories[category].append(page)

            from datetime import datetime
            structure.discovered_at = datetime.now()
            return structure
    except Exception as e:
        print(f"Algolia discovery failed: {e}")

    # Fallback to HTML scraping
    print("Falling back to HTML scraping...")
    docs_url = f"{config.base_url}{config.docs_path}"
    headers = {'User-Agent': 'Mozilla/5.0 (LimaCharlie Documentation Bot)'}

    try:
        response = requests.get(docs_url, headers=headers, timeout=config.request_timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Try multiple selectors for navigation links
        nav_selectors = [
            'nav a[href^="/docs"]',
            'aside a[href^="/docs"]',
            '.sidebar a[href^="/docs"]',
            '.navigation a[href^="/docs"]',
            'a[href^="/docs"]'
        ]

        all_links = set()
        for selector in nav_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href and '/docs/' in href:
                    # Normalize URL
                    if href.startswith('/'):
                        href = f"{config.base_url}{href}"
                    all_links.add(href)

        print(f"Found {len(all_links)} documentation links")

        # Process each link
        for link in all_links:
            page = _create_page_from_url(link, config)
            if page:
                category = _categorize_page(page.slug)
                if category not in structure.categories:
                    structure.categories[category] = []
                structure.categories[category].append(page)
                print(f"  Discovered: {category}/{page.slug}")
                time.sleep(0.1)  # Be respectful

    except Exception as e:
        print(f"Error discovering structure: {e}")
        # Fallback to common pages
        structure = _fallback_discovery(config)

    from datetime import datetime
    structure.discovered_at = datetime.now()
    return structure


def _create_page_from_url(url: str, config: Config) -> Optional[Page]:
    """Create a Page object from a URL by fetching its title."""
    try:
        # Extract slug from URL
        slug = url.replace(f"{config.base_url}{config.docs_path}/", "")
        slug = slug.rstrip('/')

        # Skip version-specific URLs
        if '/v1/' in slug:
            return None
        if '/v2/' in slug:
            slug = slug.replace('/v2/', '/')

        # Fetch page to get title
        headers = {'User-Agent': 'Mozilla/5.0 (LimaCharlie Documentation Bot)'}
        response = requests.get(url, headers=headers, timeout=config.request_timeout)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('h1')
        title = title_tag.get_text().strip() if title_tag else slug.replace('-', ' ').title()

        return Page(
            url=url,
            slug=slug,
            title=title,
            category="",  # Will be set by categorization
        )
    except Exception as e:
        print(f"  Error creating page from {url}: {e}")
        return None


def _categorize_page(slug: str) -> str:
    """
    Categorize a page based on its slug.

    DEPRECATED: Use categorize.categorize_pages_with_claude() for better results.
    This is kept as a fallback only.
    """
    slug_lower = slug.lower()

    # Priority 1: Exact prefix patterns
    if slug_lower.startswith('adapter-types-') or slug_lower.startswith('adapter-examples-'):
        return "adapters"
    elif slug_lower.startswith('outputs-destinations-') or slug_lower.startswith('output-destinations-'):
        return "outputs"
    elif slug_lower.startswith('ext-'):
        return "add-ons"
    elif slug_lower.startswith('api-integrations-'):
        return "integrations"
    elif slug_lower.startswith('reference-'):
        return "reference"

    # Priority 2: Broad keyword matching
    categories = {
        "getting-started": ["quickstart", "what-is", "use-case", "introduction"],
        "sensors": ["sensor", "installation", "agent", "endpoint"],
        "events": ["event-schema", "edr-event", "telemetry"],
        "query": ["lcql", "query-console"],
        "detection-response": ["detection", "response", "replay", "d-r", "rule"],
        "platform": ["platform", "sdk", "organization"],
        "tutorials": ["tutorial", "guide", "walkthrough"],
        "faq": ["faq", "question"],
    }

    for category, keywords in categories.items():
        if any(keyword in slug_lower for keyword in keywords):
            return category

    return "other"


def _fallback_discovery(config: Config) -> DocumentStructure:
    """Fallback discovery using common page names."""
    print("Using fallback discovery...")
    structure = DocumentStructure()

    common_pages = [
        'what-is-limacharlie', 'quickstart', 'use-cases',
        'installation-keys', 'sensors', 'events', 'lcql',
        'detection-and-response', 'outputs', 'add-ons'
    ]

    headers = {'User-Agent': 'Mozilla/5.0 (LimaCharlie Documentation Bot)'}

    for slug in common_pages:
        url = f"{config.base_url}{config.docs_path}/{slug}"
        try:
            response = requests.get(url, headers=headers, timeout=config.request_timeout)
            if response.status_code == 200:
                page = Page(
                    url=url,
                    slug=slug,
                    title=slug.replace('-', ' ').title(),
                    category="00-general",
                )
                if "00-general" not in structure.categories:
                    structure.categories["00-general"] = []
                structure.categories["00-general"].append(page)
        except:
            continue

    from datetime import datetime
    structure.discovered_at = datetime.now()
    return structure


def download_page(page: Page, config: Config) -> bool:
    """
    Download HTML content for a page.

    Updates page.raw_html and page.content_hash.
    Returns True on success.
    """
    try:
        print(f"Downloading: {page.url}")
        headers = {'User-Agent': 'Mozilla/5.0 (LimaCharlie Documentation Bot)'}

        for attempt in range(config.retry_attempts):
            try:
                response = requests.get(
                    page.url,
                    headers=headers,
                    timeout=config.request_timeout
                )
                response.raise_for_status()

                page.raw_html = response.text
                page.content_hash = hashlib.sha256(response.text.encode()).hexdigest()

                print(f"✓ Downloaded: {page.slug}")
                return True

            except requests.RequestException as e:
                if attempt < config.retry_attempts - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    print(f"  Retry {attempt + 1}/{config.retry_attempts} after {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise

    except Exception as e:
        print(f"✗ Error downloading {page.url}: {e}")
        return False


def download_all_pages(structure: DocumentStructure, config: Config) -> int:
    """
    Download all pages in the structure.

    Returns number of successfully downloaded pages.
    """
    total = sum(len(pages) for pages in structure.categories.values())
    downloaded = 0

    print(f"\nDownloading {total} pages...")

    for category, pages in sorted(structure.categories.items()):
        print(f"\nCategory: {category}")
        for page in pages:
            if download_page(page, config):
                downloaded += 1
            time.sleep(config.rate_limit_delay)

    print(f"\n✓ Downloaded {downloaded}/{total} pages")
    return downloaded
