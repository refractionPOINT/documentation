"""Documentation fetching and discovery."""
import time
import hashlib
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


def discover_documentation_structure(config: Config) -> DocumentStructure:
    """
    Dynamically discover all documentation pages from the website.

    Returns DocumentStructure with discovered pages organized by category.
    """
    print("Discovering documentation structure...")

    docs_url = f"{config.base_url}{config.docs_path}"
    headers = {'User-Agent': 'Mozilla/5.0 (LimaCharlie Documentation Bot)'}
    structure = DocumentStructure()

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
    """Categorize a page based on its slug."""
    slug_lower = slug.lower()

    # Category mapping based on keywords
    categories = {
        "01-getting-started": ["quickstart", "what-is", "use-case", "introduction"],
        "02-sensors": ["sensor", "installation", "agent", "endpoint"],
        "03-events": ["event", "edr", "telemetry"],
        "04-query-console": ["lcql", "query", "search"],
        "05-detection-response": ["detection", "response", "replay", "d&r", "rule"],
        "06-platform-management": ["platform", "sdk", "adapter", "api", "organization"],
        "07-outputs": ["output", "siem", "export", "integration"],
        "08-add-ons": ["add-on", "extension", "ext-"],
        "09-tutorials": ["tutorial", "guide", "walkthrough", "example"],
        "10-faq": ["faq", "question"],
        "11-release-notes": ["release", "changelog", "version"],
    }

    for category, keywords in categories.items():
        if any(keyword in slug_lower for keyword in keywords):
            return category

    return "12-other"


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
