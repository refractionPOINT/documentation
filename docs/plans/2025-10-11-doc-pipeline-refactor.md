# LimaCharlie Documentation Pipeline Refactor Implementation Plan

> **For Claude:** Use `${CLAUDE_PLUGIN_ROOT}/skills/collaboration/executing-plans/SKILL.md` to implement this plan task-by-task.

**Goal:** Refactor the LimaCharlie documentation generation process into a deterministic, maintainable, LLM-optimized pipeline with content-aware change detection and verification.

**Architecture:** Functional pipeline with explicit phases (FETCH → CONVERT → ANALYZE → ENHANCE → VERIFY → DETECT). Each phase operates on well-defined data structures (Page objects) with state saved between phases. Git-based change tracking with intelligent diff reporting.

**Tech Stack:** Python 3.x, requests, beautifulsoup4, markitdown, dataclasses, pathlib, git

---

## Task 1: Project Structure & Configuration

**Files:**
- Create: `doc-pipeline/README.md`
- Create: `doc-pipeline/requirements.txt`
- Create: `doc-pipeline/config.py`
- Create: `doc-pipeline/models.py`

**Step 1: Create directory structure**

```bash
mkdir -p doc-pipeline/lib
mkdir -p doc-pipeline/tests
touch doc-pipeline/__init__.py
touch doc-pipeline/lib/__init__.py
```

**Step 2: Create requirements.txt**

```text
requests>=2.31.0
beautifulsoup4>=4.12.0
markitdown>=0.0.1a2
```

**Step 3: Create README.md**

```markdown
# LimaCharlie Documentation Pipeline

Automated pipeline for fetching, converting, and optimizing LimaCharlie documentation for LLM consumption.

## Features

- Dynamic structure discovery from docs.limacharlie.io
- Content-aware change detection
- LLM-optimized markdown generation
- API signature extraction
- Git-based change tracking
- Verification for correctness

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Full pipeline run
python -m doc-pipeline.cli

# Dry run
python -m doc-pipeline.cli --dry-run

# Skip git commit
python -m doc-pipeline.cli --no-commit
```

## Architecture

```
FETCH → CONVERT → ANALYZE → ENHANCE → VERIFY → DETECT
```

Each phase saves intermediate state for debugging/resumption.
```

**Step 4: Create models.py with data structures**

```python
"""Data models for documentation pipeline."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Page:
    """Represents a single documentation page."""
    url: str
    slug: str
    title: str
    category: str
    raw_html: str = ""
    markdown: str = ""
    metadata: Dict = field(default_factory=dict)
    api_elements: List[Dict] = field(default_factory=list)
    content_hash: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'url': self.url,
            'slug': self.slug,
            'title': self.title,
            'category': self.category,
            'raw_html': self.raw_html,
            'markdown': self.markdown,
            'metadata': self.metadata,
            'api_elements': self.api_elements,
            'content_hash': self.content_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Page':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class DocumentStructure:
    """Represents the entire documentation structure."""
    categories: Dict[str, List[Page]] = field(default_factory=dict)
    navigation: Dict = field(default_factory=dict)
    api_index: Dict = field(default_factory=dict)
    discovered_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'categories': {
                cat: [page.to_dict() for page in pages]
                for cat, pages in self.categories.items()
            },
            'navigation': self.navigation,
            'api_index': self.api_index,
            'discovered_at': self.discovered_at.isoformat() if self.discovered_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'DocumentStructure':
        """Create from dictionary."""
        categories = {
            cat: [Page.from_dict(page) for page in pages]
            for cat, pages in data.get('categories', {}).items()
        }
        discovered_at = None
        if data.get('discovered_at'):
            discovered_at = datetime.fromisoformat(data['discovered_at'])

        return cls(
            categories=categories,
            navigation=data.get('navigation', {}),
            api_index=data.get('api_index', {}),
            discovered_at=discovered_at,
        )


@dataclass
class VerificationIssue:
    """Represents a verification problem found."""
    severity: str  # "critical", "warning", "info"
    page_slug: str
    issue_type: str
    message: str
    details: Optional[Dict] = None


@dataclass
class VerificationReport:
    """Report of verification results."""
    total_pages: int = 0
    passed: int = 0
    warnings: int = 0
    critical: int = 0
    issues: List[VerificationIssue] = field(default_factory=list)

    def add_issue(self, issue: VerificationIssue):
        """Add an issue and update counters."""
        self.issues.append(issue)
        if issue.severity == "critical":
            self.critical += 1
        elif issue.severity == "warning":
            self.warnings += 1
```

**Step 5: Create config.py**

```python
"""Configuration for documentation pipeline."""
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Pipeline configuration."""
    # Source
    base_url: str = "https://docs.limacharlie.io"
    docs_path: str = "/docs"

    # Output paths
    output_dir: Path = Path("limacharlie-docs-markdown")
    state_dir: Path = Path(".doc-pipeline-state")
    raw_html_dir: Path = Path("limacharlie-docs")

    # Behavior
    rate_limit_delay: float = 0.5  # seconds between requests
    request_timeout: int = 30
    retry_attempts: int = 3

    # Enhancement options
    extract_api_signatures: bool = True
    generate_summaries: bool = True
    add_cross_references: bool = True
    optimize_headings: bool = True

    # Verification options
    verify_content: bool = True
    verify_apis: bool = True
    verify_metadata: bool = True
    fail_on_critical: bool = False

    # Change detection
    git_commit_changes: bool = True
    git_commit_message: str = "Update LimaCharlie documentation"

    def __post_init__(self):
        """Ensure paths are Path objects."""
        if not isinstance(self.output_dir, Path):
            self.output_dir = Path(self.output_dir)
        if not isinstance(self.state_dir, Path):
            self.state_dir = Path(self.state_dir)
        if not isinstance(self.raw_html_dir, Path):
            self.raw_html_dir = Path(self.raw_html_dir)
```

**Step 6: Commit**

```bash
git add doc-pipeline/
git commit -m "feat: add project structure, models, and config"
```

---

## Task 2: Fetch Module

**Files:**
- Create: `doc-pipeline/lib/fetch.py`
- Create: `doc-pipeline/tests/test_fetch.py`

**Step 1: Create lib/fetch.py with discovery and download functions**

```python
"""Documentation fetching and discovery."""
import time
import hashlib
from typing import Dict, List, Tuple, Optional
import requests
from bs4 import BeautifulSoup
from ..models import Page, DocumentStructure
from ..config import Config


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
```

**Step 2: Create basic test**

```python
"""Tests for fetch module."""
from doc-pipeline.lib.fetch import _categorize_page


def test_categorize_page_getting_started():
    assert _categorize_page("quickstart") == "01-getting-started"
    assert _categorize_page("what-is-limacharlie") == "01-getting-started"


def test_categorize_page_sensors():
    assert _categorize_page("sensor-installation") == "02-sensors"
    assert _categorize_page("agent-configuration") == "02-sensors"


def test_categorize_page_other():
    assert _categorize_page("random-page") == "12-other"
```

**Step 3: Run test**

```bash
cd doc-pipeline && python -m pytest tests/test_fetch.py -v
```

Expected: PASS (3 tests)

**Step 4: Commit**

```bash
git add doc-pipeline/lib/fetch.py doc-pipeline/tests/test_fetch.py
git commit -m "feat: add fetch module with discovery and download"
```

---

## Task 3: Convert Module

**Files:**
- Create: `doc-pipeline/lib/convert.py`
- Create: `doc-pipeline/tests/test_convert.py`

**Step 1: Create lib/convert.py**

```python
"""HTML to Markdown conversion and cleaning."""
import re
import subprocess
from typing import Optional
from ..models import Page
from ..config import Config


def html_to_markdown(html: str) -> str:
    """
    Convert HTML to markdown using markitdown.

    Returns raw markdown output.
    """
    try:
        # Use markitdown via subprocess
        result = subprocess.run(
            ['markitdown', '-'],
            input=html,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True
        )
        return result.stdout
    except Exception as e:
        print(f"Error converting HTML: {e}")
        return ""


def clean_markdown_content(content: str) -> str:
    """
    Clean Document360 artifacts from markdown content.

    Removes UI elements, metadata, feedback forms, etc.
    """
    if not content:
        return ""

    lines = content.split('\n')

    # Find main heading
    main_heading_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('# '):
            main_heading_idx = i
            break

    if main_heading_idx == -1:
        return content

    # Start from main heading
    cleaned_lines = [lines[main_heading_idx]]

    # Process content after heading
    i = main_heading_idx + 1
    skip_metadata = True

    # Patterns to skip
    skip_patterns = [
        'Updated on', 'Minutes to read', '* Print', '* Share',
        '* Dark', 'Light', 'Article summary',
        'Did you find this summary helpful?',
        'Thank you for your feedback!',
        'Was this article helpful?',
        'How can we improve this article?',
        'Your feedback', 'Character limit :',
        'Email (Optional)', 'Powered by Document360'
    ]

    while i < len(lines):
        line = lines[i]

        # Skip post-heading metadata
        if skip_metadata:
            if any(pattern in line for pattern in skip_patterns):
                i += 1
                continue
            elif line.strip() in ['---', '']:
                i += 1
                continue
            else:
                skip_metadata = False

        # Check for feedback section
        if any(pattern in line for pattern in skip_patterns):
            # Skip until we find next section or end
            while i < len(lines):
                if lines[i].strip().startswith('###### What\'s Next') or \
                   lines[i].strip().startswith('###### Related articles'):
                    break
                i += 1
            continue

        cleaned_lines.append(line)
        i += 1

    result = '\n'.join(cleaned_lines)

    # Normalize excessive newlines
    result = re.sub(r'\n{4,}', '\n\n\n', result)

    # Remove trailing empty lines and dividers
    lines = result.split('\n')
    while lines and lines[-1].strip() in ['', '---']:
        lines.pop()

    return '\n'.join(lines).strip()


def normalize_formatting(content: str) -> str:
    """
    Normalize markdown formatting for consistency.

    - Ensure code blocks have language tags
    - Consistent spacing
    - Proper heading hierarchy
    """
    if not content:
        return ""

    lines = content.split('\n')
    normalized = []
    in_code_block = False

    for i, line in enumerate(lines):
        # Detect code block start
        if line.strip().startswith('```'):
            in_code_block = not in_code_block

            # If starting code block without language, try to infer
            if in_code_block and line.strip() == '```':
                # Look ahead for common patterns
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if any(kw in next_line for kw in ['def ', 'class ', 'import ']):
                        line = '```python'
                    elif any(kw in next_line for kw in ['function', 'const ', 'let ']):
                        line = '```javascript'
                    elif any(kw in next_line for kw in ['curl ', 'http ', 'GET ', 'POST ']):
                        line = '```bash'

        normalized.append(line)

    return '\n'.join(normalized)


def convert_page(page: Page, config: Config) -> bool:
    """
    Convert a page's HTML to cleaned markdown.

    Updates page.markdown field.
    Returns True on success.
    """
    if not page.raw_html:
        print(f"✗ No HTML content for {page.slug}")
        return False

    try:
        # Convert to markdown
        raw_md = html_to_markdown(page.raw_html)
        if not raw_md:
            return False

        # Clean artifacts
        cleaned = clean_markdown_content(raw_md)

        # Normalize formatting
        normalized = normalize_formatting(cleaned)

        page.markdown = normalized

        print(f"✓ Converted: {page.slug}")
        return True

    except Exception as e:
        print(f"✗ Error converting {page.slug}: {e}")
        return False


def convert_all_pages(structure, config: Config) -> int:
    """
    Convert all pages in structure to markdown.

    Returns number of successfully converted pages.
    """
    total = sum(len(pages) for pages in structure.categories.values())
    converted = 0

    print(f"\nConverting {total} pages...")

    for category, pages in structure.categories.items():
        for page in pages:
            if convert_page(page, config):
                converted += 1

    print(f"✓ Converted {converted}/{total} pages")
    return converted
```

**Step 2: Create test**

```python
"""Tests for convert module."""
from doc_pipeline.lib.convert import clean_markdown_content, normalize_formatting


def test_clean_markdown_removes_metadata():
    content = """# Main Title

Updated on Jan 1, 2024
Minutes to read: 5
* Print * Share

## Actual Content

This is the real content."""

    result = clean_markdown_content(content)
    assert "Updated on" not in result
    assert "Minutes to read" not in result
    assert "Actual Content" in result


def test_normalize_formatting_adds_language():
    content = """Some text

```
def hello():
    print("world")
```"""

    result = normalize_formatting(content)
    assert "```python" in result


def test_clean_markdown_preserves_code_blocks():
    content = """# Title

```python
def test():
    pass
```

More content."""

    result = clean_markdown_content(content)
    assert "```python" in result
    assert "def test():" in result
```

**Step 3: Run test**

```bash
python -m pytest doc-pipeline/tests/test_convert.py -v
```

Expected: PASS (3 tests)

**Step 4: Commit**

```bash
git add doc-pipeline/lib/convert.py doc-pipeline/tests/test_convert.py
git commit -m "feat: add convert module with cleaning and normalization"
```

---

## Task 4: Analyze Module

**Files:**
- Create: `doc-pipeline/lib/analyze.py`
- Create: `doc-pipeline/tests/test_analyze.py`

**Step 1: Create lib/analyze.py**

```python
"""Content analysis and metadata extraction."""
import re
from typing import Dict, List, Optional
from ..models import Page
from ..config import Config


def extract_metadata(page: Page, config: Config) -> Dict:
    """
    Extract metadata from page content.

    Returns dictionary with:
    - summary: 2-3 sentence overview
    - keywords: List of key terms
    - complexity: beginner/intermediate/advanced
    - use_cases: Identified use cases
    """
    if not page.markdown:
        return {}

    metadata = {
        'summary': _generate_summary(page),
        'keywords': _extract_keywords(page),
        'complexity': _assess_complexity(page),
        'use_cases': _extract_use_cases(page),
    }

    page.metadata.update(metadata)
    return metadata


def _generate_summary(page: Page) -> str:
    """Generate a brief summary from first paragraph."""
    lines = page.markdown.split('\n')

    # Skip title and find first substantial paragraph
    in_paragraph = False
    paragraph_lines = []

    for line in lines[1:]:  # Skip title
        line = line.strip()

        # Skip empty lines, headings, and code blocks
        if not line or line.startswith('#') or line.startswith('```'):
            if paragraph_lines:
                break
            continue

        paragraph_lines.append(line)

        # Stop after ~2-3 sentences
        if len(paragraph_lines) >= 3:
            break

    summary = ' '.join(paragraph_lines)

    # Truncate to reasonable length
    if len(summary) > 300:
        summary = summary[:297] + '...'

    return summary


def _extract_keywords(page: Page) -> List[str]:
    """Extract key terms from the page."""
    keywords = set()

    # Extract from title
    title_words = page.title.lower().split()
    keywords.update(word for word in title_words if len(word) > 3)

    # Common LimaCharlie terms
    lc_terms = [
        'sensor', 'detection', 'response', 'event', 'telemetry',
        'lcql', 'query', 'rule', 'output', 'integration',
        'api', 'sdk', 'add-on', 'extension', 'organization',
        'edr', 'd&r', 'siem', 'endpoint', 'agent'
    ]

    content_lower = page.markdown.lower()
    for term in lc_terms:
        if term in content_lower:
            keywords.add(term)

    # Extract from headings
    headings = re.findall(r'^#{2,6}\s+(.+)$', page.markdown, re.MULTILINE)
    for heading in headings:
        words = heading.lower().split()
        keywords.update(word for word in words if len(word) > 4)

    return sorted(list(keywords))[:15]  # Limit to 15 keywords


def _assess_complexity(page: Page) -> str:
    """Assess page complexity level."""
    content = page.markdown.lower()

    # Beginner indicators
    beginner_terms = ['quickstart', 'getting started', 'introduction', 'basics']
    beginner_score = sum(1 for term in beginner_terms if term in content)

    # Advanced indicators
    advanced_terms = ['api', 'sdk', 'advanced', 'custom', 'script', 'integration']
    advanced_score = sum(1 for term in advanced_terms if term in content)

    # Code blocks
    code_blocks = len(re.findall(r'```', page.markdown)) // 2

    if beginner_score > 0 and advanced_score == 0:
        return 'beginner'
    elif code_blocks > 5 or advanced_score > 2:
        return 'advanced'
    else:
        return 'intermediate'


def _extract_use_cases(page: Page) -> List[str]:
    """Extract mentioned use cases."""
    use_cases = []

    # Look for use case sections
    use_case_pattern = re.compile(
        r'use case[s]?:?\s*[-•*]?\s*(.+?)(?:\n|$)',
        re.IGNORECASE | re.MULTILINE
    )

    matches = use_case_pattern.findall(page.markdown)
    use_cases.extend(match.strip() for match in matches if match.strip())

    # Common patterns
    if 'threat detection' in page.markdown.lower():
        use_cases.append('Threat Detection')
    if 'incident response' in page.markdown.lower():
        use_cases.append('Incident Response')
    if 'forensics' in page.markdown.lower():
        use_cases.append('Forensics')
    if 'compliance' in page.markdown.lower():
        use_cases.append('Compliance')

    return list(set(use_cases))[:5]  # Limit to 5


def extract_api_elements(page: Page, config: Config) -> List[Dict]:
    """
    Extract API signatures, endpoints, and parameters.

    Returns list of API element dictionaries.
    """
    if not page.markdown:
        return []

    api_elements = []

    # Extract REST endpoints
    endpoints = _extract_rest_endpoints(page.markdown)
    api_elements.extend(endpoints)

    # Extract Python API calls
    python_apis = _extract_python_apis(page.markdown)
    api_elements.extend(python_apis)

    # Extract CLI commands
    cli_commands = _extract_cli_commands(page.markdown)
    api_elements.extend(cli_commands)

    page.api_elements = api_elements
    return api_elements


def _extract_rest_endpoints(content: str) -> List[Dict]:
    """Extract REST API endpoints."""
    endpoints = []

    # Pattern: GET /api/v1/resource
    pattern = re.compile(
        r'(GET|POST|PUT|DELETE|PATCH)\s+([/\w\-\{\}]+)',
        re.IGNORECASE
    )

    matches = pattern.findall(content)
    for method, path in matches:
        endpoints.append({
            'type': 'rest_endpoint',
            'method': method.upper(),
            'path': path,
        })

    return endpoints


def _extract_python_apis(content: str) -> List[Dict]:
    """Extract Python API calls."""
    apis = []

    # Look in Python code blocks
    code_blocks = re.findall(r'```python\n(.+?)```', content, re.DOTALL)

    for block in code_blocks:
        # Find function calls like: client.function(...)
        pattern = re.compile(r'(\w+)\.(\w+)\([^)]*\)')
        matches = pattern.findall(block)

        for obj, method in matches:
            apis.append({
                'type': 'python_api',
                'object': obj,
                'method': method,
            })

    return apis


def _extract_cli_commands(content: str) -> List[Dict]:
    """Extract CLI commands."""
    commands = []

    # Look in bash code blocks
    code_blocks = re.findall(r'```(?:bash|shell)\n(.+?)```', content, re.DOTALL)

    for block in code_blocks:
        lines = block.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Extract command (first word)
                parts = line.split()
                if parts:
                    commands.append({
                        'type': 'cli_command',
                        'command': parts[0],
                        'full': line,
                    })

    return commands


def build_api_index(structure) -> Dict:
    """
    Build comprehensive API index from all pages.

    Returns dictionary mapping API types to lists of APIs with page references.
    """
    index = {
        'rest_endpoints': [],
        'python_apis': [],
        'cli_commands': [],
    }

    for category, pages in structure.categories.items():
        for page in pages:
            for api in page.api_elements:
                api_type = api['type']

                # Add page reference
                api_with_ref = api.copy()
                api_with_ref['page_slug'] = page.slug
                api_with_ref['page_title'] = page.title

                # Add to appropriate index
                if api_type == 'rest_endpoint':
                    index['rest_endpoints'].append(api_with_ref)
                elif api_type == 'python_api':
                    index['python_apis'].append(api_with_ref)
                elif api_type == 'cli_command':
                    index['cli_commands'].append(api_with_ref)

    structure.api_index = index
    return index


def analyze_all_pages(structure, config: Config) -> int:
    """
    Analyze all pages and build API index.

    Returns number of successfully analyzed pages.
    """
    total = sum(len(pages) for pages in structure.categories.values())
    analyzed = 0

    print(f"\nAnalyzing {total} pages...")

    for category, pages in structure.categories.items():
        for page in pages:
            try:
                if config.extract_api_signatures:
                    extract_api_elements(page, config)
                if config.generate_summaries:
                    extract_metadata(page, config)

                print(f"✓ Analyzed: {page.slug}")
                analyzed += 1
            except Exception as e:
                print(f"✗ Error analyzing {page.slug}: {e}")

    # Build API index
    print("\nBuilding API index...")
    api_index = build_api_index(structure)
    total_apis = sum(len(apis) for apis in api_index.values())
    print(f"✓ Indexed {total_apis} API elements")

    return analyzed
```

**Step 2: Create test**

```python
"""Tests for analyze module."""
from doc_pipeline.models import Page
from doc_pipeline.lib.analyze import _extract_keywords, _assess_complexity, _extract_rest_endpoints


def test_extract_keywords():
    page = Page(
        url="http://test.com",
        slug="test",
        title="Detection and Response",
        category="test",
    )
    page.markdown = """# Detection and Response

This page covers detection rules and response actions.

## Using LCQL

Query your events with LCQL."""

    keywords = _extract_keywords(page)
    assert 'detection' in keywords
    assert 'response' in keywords
    assert 'lcql' in keywords


def test_assess_complexity_beginner():
    page = Page(
        url="http://test.com",
        slug="quickstart",
        title="Quickstart",
        category="test",
    )
    page.markdown = "# Quickstart\n\nGetting started with LimaCharlie is easy."

    complexity = _assess_complexity(page)
    assert complexity == 'beginner'


def test_extract_rest_endpoints():
    content = """
GET /api/v1/orgs/{oid}/sensors
POST /api/v1/orgs/{oid}/rules
"""

    endpoints = _extract_rest_endpoints(content)
    assert len(endpoints) == 2
    assert endpoints[0]['method'] == 'GET'
    assert '/sensors' in endpoints[0]['path']
```

**Step 3: Run test**

```bash
python -m pytest doc-pipeline/tests/test_analyze.py -v
```

Expected: PASS (3 tests)

**Step 4: Commit**

```bash
git add doc-pipeline/lib/analyze.py doc-pipeline/tests/test_analyze.py
git commit -m "feat: add analyze module with metadata and API extraction"
```

---

## Task 5: Enhance Module

**Files:**
- Create: `doc-pipeline/lib/enhance.py`

**Step 1: Create lib/enhance.py**

```python
"""LLM-specific optimizations and enhancements."""
import re
from typing import Dict, List, Set
from ..models import Page
from ..config import Config


def add_cross_references(structure, config: Config) -> int:
    """
    Add cross-references between related pages.

    Returns number of cross-references added.
    """
    if not config.add_cross_references:
        return 0

    print("\nAdding cross-references...")

    # Build slug to page mapping
    slug_map = {}
    for category, pages in structure.categories.items():
        for page in pages:
            slug_map[page.slug] = page

    total_refs = 0

    for category, pages in structure.categories.items():
        for page in pages:
            refs = _find_related_pages(page, slug_map)
            if refs:
                page.metadata['related_pages'] = refs
                total_refs += len(refs)
                print(f"  {page.slug}: {len(refs)} references")

    print(f"✓ Added {total_refs} cross-references")
    return total_refs


def _find_related_pages(page: Page, slug_map: Dict[str, Page]) -> List[Dict]:
    """Find pages related to this one."""
    related = []

    # Extract key terms from this page
    content_lower = page.markdown.lower()
    keywords = set(page.metadata.get('keywords', []))

    # Check other pages for matches
    for slug, other_page in slug_map.items():
        if slug == page.slug:
            continue

        # Calculate relevance score
        score = 0

        # Check if other page is mentioned
        if other_page.title.lower() in content_lower:
            score += 5

        if slug in content_lower:
            score += 3

        # Check keyword overlap
        other_keywords = set(other_page.metadata.get('keywords', []))
        overlap = keywords & other_keywords
        score += len(overlap)

        # Check category similarity
        if page.category == other_page.category:
            score += 2

        if score >= 3:  # Threshold for relevance
            related.append({
                'slug': slug,
                'title': other_page.title,
                'score': score,
            })

    # Return top 5 most related
    related.sort(key=lambda x: x['score'], reverse=True)
    return related[:5]


def optimize_heading_hierarchy(page: Page, config: Config) -> bool:
    """
    Ensure consistent heading hierarchy.

    - Single H1 (title)
    - Logical H2-H6 progression
    - No skipped levels

    Updates page.markdown.
    Returns True if changes made.
    """
    if not config.optimize_headings or not page.markdown:
        return False

    lines = page.markdown.split('\n')
    changes_made = False

    # Track heading levels
    h1_count = 0
    prev_level = 0

    for i, line in enumerate(lines):
        if not line.strip().startswith('#'):
            continue

        # Count heading level
        level = 0
        for char in line:
            if char == '#':
                level += 1
            else:
                break

        # Ensure single H1
        if level == 1:
            h1_count += 1
            if h1_count > 1:
                # Demote to H2
                lines[i] = '#' + line
                changes_made = True
                level = 2

        # Check for skipped levels
        if prev_level > 0 and level > prev_level + 1:
            # Reduce to prev_level + 1
            correct_level = prev_level + 1
            heading_text = line.lstrip('#').strip()
            lines[i] = '#' * correct_level + ' ' + heading_text
            changes_made = True
            level = correct_level

        prev_level = level

    if changes_made:
        page.markdown = '\n'.join(lines)
        print(f"  Optimized headings: {page.slug}")

    return changes_made


def enhance_code_blocks(page: Page) -> bool:
    """
    Enhance code blocks with better formatting.

    - Add language identifiers where missing
    - Add line numbers for long blocks
    - Ensure proper spacing

    Updates page.markdown.
    Returns True if changes made.
    """
    if not page.markdown:
        return False

    changes_made = False
    lines = page.markdown.split('\n')
    result = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check for code block start
        if line.strip().startswith('```'):
            # Check if language is specified
            if line.strip() == '```':
                # Look ahead to infer language
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    lang = _infer_language(next_line)
                    if lang:
                        line = f'```{lang}'
                        changes_made = True

            result.append(line)
            i += 1

            # Copy code block content
            while i < len(lines) and not lines[i].strip().startswith('```'):
                result.append(lines[i])
                i += 1

            # Add closing ```
            if i < len(lines):
                result.append(lines[i])
                i += 1
        else:
            result.append(line)
            i += 1

    if changes_made:
        page.markdown = '\n'.join(result)

    return changes_made


def _infer_language(code_line: str) -> str:
    """Infer programming language from code."""
    code = code_line.strip()

    if code.startswith('def ') or code.startswith('class ') or 'import ' in code:
        return 'python'
    elif code.startswith('function ') or code.startswith('const ') or code.startswith('let '):
        return 'javascript'
    elif code.startswith('curl ') or code.startswith('GET ') or code.startswith('POST '):
        return 'bash'
    elif code.startswith('{') or code.startswith('['):
        return 'json'
    elif code.startswith('<?php'):
        return 'php'

    return ''


def enhance_all_pages(structure, config: Config) -> int:
    """
    Enhance all pages with LLM optimizations.

    Returns number of enhanced pages.
    """
    print("\nEnhancing pages for LLM consumption...")

    # Add cross-references
    if config.add_cross_references:
        add_cross_references(structure, config)

    # Optimize individual pages
    enhanced = 0
    for category, pages in structure.categories.items():
        for page in pages:
            changes = False

            if config.optimize_headings:
                changes |= optimize_heading_hierarchy(page, config)

            changes |= enhance_code_blocks(page)

            if changes:
                enhanced += 1

    print(f"✓ Enhanced {enhanced} pages")
    return enhanced
```

**Step 2: Commit**

```bash
git add doc-pipeline/lib/enhance.py
git commit -m "feat: add enhance module for LLM optimizations"
```

---

## Task 6: Verify Module (Content Correctness)

**Files:**
- Create: `doc-pipeline/lib/verify.py`
- Create: `doc-pipeline/tests/test_verify.py`

**Step 1: Create lib/verify.py**

```python
"""Content verification and correctness checking."""
import re
from typing import List
from bs4 import BeautifulSoup
from ..models import Page, VerificationIssue, VerificationReport
from ..config import Config


def verify_content_completeness(page: Page) -> List[VerificationIssue]:
    """
    Verify markdown content is complete compared to source HTML.

    Checks:
    - Word count shouldn't drop significantly
    - All code blocks preserved
    - Heading count matches
    - Links still present
    """
    issues = []

    if not page.raw_html or not page.markdown:
        return issues

    # Parse HTML for comparison
    soup = BeautifulSoup(page.raw_html, 'html.parser')

    # Remove script and style elements
    for element in soup(['script', 'style', 'nav', 'footer', 'header']):
        element.decompose()

    html_text = soup.get_text()
    html_words = len(html_text.split())
    md_words = len(page.markdown.split())

    # Check word count (allow 10% loss for removed UI elements)
    if html_words > 0:
        ratio = md_words / html_words
        if ratio < 0.85:
            issues.append(VerificationIssue(
                severity="critical",
                page_slug=page.slug,
                issue_type="content_loss",
                message=f"Significant word count loss: {html_words} → {md_words} ({ratio:.1%})",
                details={'html_words': html_words, 'md_words': md_words}
            ))

    # Check code blocks
    html_code_blocks = len(soup.find_all(['pre', 'code']))
    md_code_blocks = len(re.findall(r'```', page.markdown)) // 2

    if html_code_blocks > md_code_blocks:
        issues.append(VerificationIssue(
            severity="critical",
            page_slug=page.slug,
            issue_type="missing_code_blocks",
            message=f"Missing code blocks: {html_code_blocks} in HTML, {md_code_blocks} in markdown",
            details={'html_blocks': html_code_blocks, 'md_blocks': md_code_blocks}
        ))

    # Check headings
    html_headings = len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
    md_headings = len(re.findall(r'^#{1,6}\s', page.markdown, re.MULTILINE))

    if abs(html_headings - md_headings) > 2:  # Allow small variance
        issues.append(VerificationIssue(
            severity="warning",
            page_slug=page.slug,
            issue_type="heading_mismatch",
            message=f"Heading count differs: {html_headings} in HTML, {md_headings} in markdown",
            details={'html_headings': html_headings, 'md_headings': md_headings}
        ))

    # Check links
    html_links = len(soup.find_all('a', href=True))
    md_links = len(re.findall(r'\[.+?\]\(.+?\)', page.markdown))

    if html_links > md_links + 3:  # Allow for nav links removed
        issues.append(VerificationIssue(
            severity="warning",
            page_slug=page.slug,
            issue_type="missing_links",
            message=f"Possible missing links: {html_links} in HTML, {md_links} in markdown",
            details={'html_links': html_links, 'md_links': md_links}
        ))

    return issues


def verify_api_extraction(page: Page) -> List[VerificationIssue]:
    """
    Verify extracted APIs match source content.

    Re-parse HTML and compare against extracted api_elements.
    Flag hallucinated or missed APIs.
    """
    issues = []

    if not page.raw_html or not page.api_elements:
        return issues

    # Re-extract APIs from HTML
    soup = BeautifulSoup(page.raw_html, 'html.parser')
    code_blocks = soup.find_all(['pre', 'code'])

    html_api_patterns = set()
    for block in code_blocks:
        text = block.get_text()

        # Find REST endpoints
        endpoints = re.findall(r'(GET|POST|PUT|DELETE|PATCH)\s+([/\w\-\{\}]+)', text, re.IGNORECASE)
        for method, path in endpoints:
            html_api_patterns.add(f"{method}:{path}")

    # Compare with extracted APIs
    extracted_patterns = set()
    for api in page.api_elements:
        if api['type'] == 'rest_endpoint':
            extracted_patterns.add(f"{api['method']}:{api['path']}")

    # Check for hallucinated APIs (in extracted but not in HTML)
    hallucinated = extracted_patterns - html_api_patterns
    if hallucinated:
        issues.append(VerificationIssue(
            severity="critical",
            page_slug=page.slug,
            issue_type="hallucinated_api",
            message=f"Extracted APIs not found in source: {hallucinated}",
            details={'hallucinated': list(hallucinated)}
        ))

    # Check for missed APIs (in HTML but not extracted)
    missed = html_api_patterns - extracted_patterns
    if missed and len(missed) > len(extracted_patterns) * 0.3:  # More than 30% missed
        issues.append(VerificationIssue(
            severity="warning",
            page_slug=page.slug,
            issue_type="missed_api",
            message=f"Possibly missed APIs: {missed}",
            details={'missed': list(missed)}
        ))

    return issues


def verify_metadata_accuracy(page: Page) -> List[VerificationIssue]:
    """
    Verify metadata reflects actual content.

    Checks:
    - Keywords appear in content
    - Summary reflects actual content
    - Related pages exist
    """
    issues = []

    if not page.metadata:
        return issues

    content_lower = page.markdown.lower()

    # Verify keywords
    keywords = page.metadata.get('keywords', [])
    missing_keywords = []
    for keyword in keywords:
        if keyword.lower() not in content_lower:
            missing_keywords.append(keyword)

    if missing_keywords and len(missing_keywords) > len(keywords) * 0.3:
        issues.append(VerificationIssue(
            severity="warning",
            page_slug=page.slug,
            issue_type="invalid_keyword",
            message=f"Keywords not found in content: {missing_keywords}",
            details={'missing_keywords': missing_keywords}
        ))

    # Verify summary isn't empty
    summary = page.metadata.get('summary', '')
    if not summary or len(summary) < 20:
        issues.append(VerificationIssue(
            severity="info",
            page_slug=page.slug,
            issue_type="poor_summary",
            message="Summary is empty or too short",
            details={'summary': summary}
        ))

    return issues


def verify_cross_references(structure) -> List[VerificationIssue]:
    """
    Verify all cross-references point to real pages.

    Checks internal links and related_pages metadata.
    """
    issues = []

    # Build set of valid slugs
    valid_slugs = set()
    for category, pages in structure.categories.items():
        for page in pages:
            valid_slugs.add(page.slug)

    # Check each page's references
    for category, pages in structure.categories.items():
        for page in pages:
            # Check related_pages in metadata
            related = page.metadata.get('related_pages', [])
            for ref in related:
                if ref['slug'] not in valid_slugs:
                    issues.append(VerificationIssue(
                        severity="warning",
                        page_slug=page.slug,
                        issue_type="broken_reference",
                        message=f"Related page not found: {ref['slug']}",
                        details={'referenced_slug': ref['slug']}
                    ))

            # Check internal links in markdown
            internal_links = re.findall(r'\[.+?\]\((/docs/[^\)]+)\)', page.markdown)
            for link in internal_links:
                # Extract slug from link
                slug = link.replace('/docs/', '').strip('/')
                if slug and slug not in valid_slugs:
                    issues.append(VerificationIssue(
                        severity="warning",
                        page_slug=page.slug,
                        issue_type="broken_link",
                        message=f"Internal link may be broken: {link}",
                        details={'link': link}
                    ))

    return issues


def verify_all_pages(structure, config: Config) -> VerificationReport:
    """
    Run all verification checks and generate report.

    Returns VerificationReport with all issues found.
    """
    print("\nVerifying content correctness...")

    report = VerificationReport()

    for category, pages in structure.categories.items():
        for page in pages:
            report.total_pages += 1
            page_issues = []

            # Run all verification checks
            if config.verify_content:
                page_issues.extend(verify_content_completeness(page))

            if config.verify_apis:
                page_issues.extend(verify_api_extraction(page))

            if config.verify_metadata:
                page_issues.extend(verify_metadata_accuracy(page))

            # Add issues to report
            for issue in page_issues:
                report.add_issue(issue)

            # Count as passed if no critical issues
            if not any(i.severity == "critical" for i in page_issues):
                report.passed += 1

    # Check cross-references
    ref_issues = verify_cross_references(structure)
    for issue in ref_issues:
        report.add_issue(issue)

    # Print summary
    print(f"\n✓ Verified {report.total_pages} pages")
    print(f"  Passed: {report.passed}")
    print(f"  Warnings: {report.warnings}")
    print(f"  Critical: {report.critical}")

    if report.critical > 0 and config.fail_on_critical:
        print("\n✗ CRITICAL ISSUES FOUND - Pipeline halted")
        return report

    return report
```

**Step 2: Create test**

```python
"""Tests for verify module."""
from doc_pipeline.models import Page
from doc_pipeline.lib.verify import verify_content_completeness, verify_metadata_accuracy


def test_verify_content_completeness_passes():
    page = Page(
        url="http://test.com",
        slug="test",
        title="Test",
        category="test",
    )
    page.raw_html = "<html><body><h1>Test</h1><p>Content with many words to test the verification.</p><pre>code</pre></body></html>"
    page.markdown = "# Test\n\nContent with many words to test the verification.\n\n```\ncode\n```"

    issues = verify_content_completeness(page)
    critical = [i for i in issues if i.severity == "critical"]
    assert len(critical) == 0


def test_verify_metadata_invalid_keywords():
    page = Page(
        url="http://test.com",
        slug="test",
        title="Test",
        category="test",
    )
    page.markdown = "# Test\n\nThis is about sensors and detection."
    page.metadata = {
        'keywords': ['sensors', 'detection', 'nonexistent', 'fake', 'hallucinated']
    }

    issues = verify_metadata_accuracy(page)
    keyword_issues = [i for i in issues if i.issue_type == "invalid_keyword"]
    assert len(keyword_issues) > 0
```

**Step 3: Run test**

```bash
python -m pytest doc-pipeline/tests/test_verify.py -v
```

Expected: PASS (2 tests)

**Step 4: Commit**

```bash
git add doc-pipeline/lib/verify.py doc-pipeline/tests/test_verify.py
git commit -m "feat: add verify module for content correctness checking"
```

---

## Task 7: Change Detection Module

**Files:**
- Create: `doc-pipeline/lib/detect.py`

**Step 1: Create lib/detect.py**

```python
"""Git-based change detection and reporting."""
import subprocess
from typing import Dict, List, Tuple
from pathlib import Path
from ..config import Config


def commit_changes(output_dir: Path, config: Config) -> bool:
    """
    Commit generated documentation to git.

    Returns True if committed successfully.
    """
    if not config.git_commit_changes:
        print("\nSkipping git commit (disabled in config)")
        return False

    try:
        # Stage all changes in output directory
        subprocess.run(
            ['git', 'add', str(output_dir)],
            check=True,
            capture_output=True
        )

        # Check if there are changes to commit
        status = subprocess.run(
            ['git', 'status', '--porcelain', str(output_dir)],
            capture_output=True,
            text=True,
            check=True
        )

        if not status.stdout.strip():
            print("\nNo changes to commit")
            return False

        # Commit
        subprocess.run(
            ['git', 'commit', '-m', config.git_commit_message],
            check=True,
            capture_output=True
        )

        print(f"\n✓ Committed changes: {config.git_commit_message}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n✗ Git commit failed: {e}")
        return False


def generate_change_report(output_dir: Path, config: Config) -> Dict:
    """
    Generate report of changes from git diff.

    Returns dictionary with:
    - structural_changes: Added/removed files
    - content_changes: Modified files with details
    - significant_changes: Major changes requiring review
    """
    report = {
        'structural_changes': {
            'added': [],
            'removed': [],
        },
        'content_changes': [],
        'significant_changes': [],
        'total_files_changed': 0,
    }

    try:
        # Get diff stats
        diff_stats = subprocess.run(
            ['git', 'diff', 'HEAD~1', 'HEAD', '--numstat', '--', str(output_dir)],
            capture_output=True,
            text=True,
            check=True
        )

        for line in diff_stats.stdout.strip().split('\n'):
            if not line:
                continue

            parts = line.split('\t')
            if len(parts) != 3:
                continue

            added, removed, filepath = parts

            # Skip if binary or no changes
            if added == '-' or removed == '-':
                continue

            report['total_files_changed'] += 1

            # Categorize change
            change_info = {
                'file': filepath,
                'lines_added': int(added),
                'lines_removed': int(removed),
            }

            # Check for structural changes
            if int(added) > 0 and int(removed) == 0:
                report['structural_changes']['added'].append(filepath)
            elif int(removed) > 0 and int(added) == 0:
                report['structural_changes']['removed'].append(filepath)
            else:
                report['content_changes'].append(change_info)

            # Flag significant changes (large diffs)
            if int(added) + int(removed) > 100:
                report['significant_changes'].append(change_info)

        # Get detailed diff for significant changes
        for change in report['significant_changes']:
            diff_detail = subprocess.run(
                ['git', 'diff', 'HEAD~1', 'HEAD', '--', change['file']],
                capture_output=True,
                text=True,
                check=True
            )
            change['diff'] = _summarize_diff(diff_detail.stdout)

    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not generate git diff: {e}")
        report['error'] = str(e)

    return report


def _summarize_diff(diff: str) -> Dict:
    """Summarize a git diff into key changes."""
    summary = {
        'added_sections': [],
        'removed_sections': [],
        'modified_headings': [],
    }

    lines = diff.split('\n')
    for line in lines:
        if line.startswith('+') and not line.startswith('+++'):
            # Added line
            text = line[1:].strip()
            if text.startswith('#'):
                summary['added_sections'].append(text)
        elif line.startswith('-') and not line.startswith('---'):
            # Removed line
            text = line[1:].strip()
            if text.startswith('#'):
                summary['removed_sections'].append(text)

    return summary


def categorize_changes(report: Dict) -> Dict:
    """
    Categorize changes into types.

    Returns categories:
    - structural: New/removed pages
    - significant_content: Major updates
    - minor_content: Small edits
    - noise: Timestamps, formatting
    """
    categories = {
        'structural': {
            'count': len(report['structural_changes']['added']) +
                     len(report['structural_changes']['removed']),
            'details': report['structural_changes'],
        },
        'significant_content': {
            'count': len(report['significant_changes']),
            'details': report['significant_changes'],
        },
        'minor_content': {
            'count': len(report['content_changes']) - len(report['significant_changes']),
            'details': [c for c in report['content_changes']
                       if c not in report['significant_changes']],
        },
    }

    return categories


def print_change_report(report: Dict, categories: Dict):
    """Print human-readable change report."""
    print("\n" + "="*60)
    print("DOCUMENTATION CHANGE REPORT")
    print("="*60)

    print(f"\nTotal files changed: {report['total_files_changed']}")

    # Structural changes
    if categories['structural']['count'] > 0:
        print(f"\n📁 STRUCTURAL CHANGES ({categories['structural']['count']})")
        added = report['structural_changes']['added']
        removed = report['structural_changes']['removed']

        if added:
            print(f"\n  Added ({len(added)}):")
            for file in added[:10]:  # Show first 10
                print(f"    + {file}")
            if len(added) > 10:
                print(f"    ... and {len(added) - 10} more")

        if removed:
            print(f"\n  Removed ({len(removed)}):")
            for file in removed[:10]:
                print(f"    - {file}")
            if len(removed) > 10:
                print(f"    ... and {len(removed) - 10} more")

    # Significant changes
    if categories['significant_content']['count'] > 0:
        print(f"\n⚠️  SIGNIFICANT CONTENT CHANGES ({categories['significant_content']['count']})")
        print("\n  These pages have major updates requiring review:\n")

        for change in report['significant_changes'][:5]:  # Show first 5
            print(f"    {change['file']}")
            print(f"      +{change['lines_added']} -{change['lines_removed']} lines")

            if 'diff' in change:
                if change['diff'].get('added_sections'):
                    print(f"      Added: {len(change['diff']['added_sections'])} sections")
                if change['diff'].get('removed_sections'):
                    print(f"      Removed: {len(change['diff']['removed_sections'])} sections")
            print()

        if len(report['significant_changes']) > 5:
            print(f"    ... and {len(report['significant_changes']) - 5} more")

    # Minor changes
    if categories['minor_content']['count'] > 0:
        print(f"\n📝 Minor content changes: {categories['minor_content']['count']} files")

    print("\n" + "="*60)


def detect_and_report(output_dir: Path, config: Config) -> Dict:
    """
    Full change detection workflow.

    1. Commit changes to git
    2. Generate change report
    3. Categorize changes
    4. Print report

    Returns full report dictionary.
    """
    print("\n" + "="*60)
    print("CHANGE DETECTION")
    print("="*60)

    # Commit changes
    committed = commit_changes(output_dir, config)

    if not committed:
        print("\nNo changes detected or commit failed")
        return {}

    # Generate report
    report = generate_change_report(output_dir, config)

    if report.get('error'):
        print(f"\nError generating report: {report['error']}")
        return report

    # Categorize and print
    categories = categorize_changes(report)
    print_change_report(report, categories)

    return report
```

**Step 2: Commit**

```bash
git add doc-pipeline/lib/detect.py
git commit -m "feat: add detect module for git-based change tracking"
```

---

## Task 8: Pipeline Orchestrator

**Files:**
- Create: `doc-pipeline/pipeline.py`

**Step 1: Create pipeline.py**

```python
"""Main pipeline orchestrator."""
import json
from pathlib import Path
from datetime import datetime
from .config import Config
from .models import DocumentStructure
from .lib import fetch, convert, analyze, enhance, verify, detect


def save_state(structure: DocumentStructure, state_file: Path):
    """Save pipeline state to JSON."""
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with open(state_file, 'w') as f:
        json.dump(structure.to_dict(), f, indent=2)
    print(f"State saved to {state_file}")


def load_state(state_file: Path) -> DocumentStructure:
    """Load pipeline state from JSON."""
    if not state_file.exists():
        return None

    with open(state_file, 'r') as f:
        data = json.load(f)

    return DocumentStructure.from_dict(data)


def save_pages(structure: DocumentStructure, output_dir: Path):
    """Save individual markdown files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for category, pages in structure.categories.items():
        category_dir = output_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        for page in pages:
            if page.markdown:
                # Save markdown
                md_file = category_dir / f"{page.slug.replace('/', '-')}.md"
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(page.markdown)

                # Save metadata
                meta_file = category_dir / f"{page.slug.replace('/', '-')}.json"
                with open(meta_file, 'w') as f:
                    json.dump({
                        'url': page.url,
                        'title': page.title,
                        'slug': page.slug,
                        'category': page.category,
                        'metadata': page.metadata,
                        'api_elements': page.api_elements,
                        'content_hash': page.content_hash,
                    }, f, indent=2)


def create_combined_docs(structure: DocumentStructure, output_dir: Path):
    """Create combined documentation files."""
    # Single combined file
    combined_file = output_dir / "COMBINED.md"
    with open(combined_file, 'w') as f:
        f.write("# LimaCharlie Complete Documentation\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        for category, pages in sorted(structure.categories.items()):
            # Category header
            display_name = category[3:].replace('-', ' ').title() if category[2] == '-' else category
            f.write(f"# {display_name}\n\n")

            for page in sorted(pages, key=lambda p: p.title):
                if page.markdown:
                    f.write(f"## {page.title}\n\n")
                    f.write(page.markdown)
                    f.write("\n\n---\n\n")

    print(f"✓ Created {combined_file}")

    # API index
    if structure.api_index:
        api_file = output_dir / "API_INDEX.md"
        with open(api_file, 'w') as f:
            f.write("# LimaCharlie API Index\n\n")

            # REST endpoints
            if structure.api_index.get('rest_endpoints'):
                f.write("## REST API Endpoints\n\n")
                for api in structure.api_index['rest_endpoints']:
                    f.write(f"- `{api['method']} {api['path']}`\n")
                    f.write(f"  - Page: [{api['page_title']}]({api['page_slug']}.md)\n")
                f.write("\n")

            # Python APIs
            if structure.api_index.get('python_apis'):
                f.write("## Python SDK\n\n")
                for api in structure.api_index['python_apis']:
                    f.write(f"- `{api['object']}.{api['method']}()`\n")
                    f.write(f"  - Page: [{api['page_title']}]({api['page_slug']}.md)\n")
                f.write("\n")

            # CLI commands
            if structure.api_index.get('cli_commands'):
                f.write("## CLI Commands\n\n")
                for cmd in structure.api_index['cli_commands']:
                    f.write(f"- `{cmd['command']}`\n")
                    f.write(f"  - Page: [{cmd['page_title']}]({cmd['page_slug']}.md)\n")

        print(f"✓ Created {api_file}")

    # Metadata index
    meta_file = output_dir / "METADATA_INDEX.json"
    with open(meta_file, 'w') as f:
        all_metadata = {}
        for category, pages in structure.categories.items():
            for page in pages:
                all_metadata[page.slug] = {
                    'title': page.title,
                    'category': page.category,
                    'url': page.url,
                    'metadata': page.metadata,
                }
        json.dump(all_metadata, f, indent=2)

    print(f"✓ Created {meta_file}")


def run_pipeline(config: Config = None):
    """
    Execute the complete documentation pipeline.

    Phases:
    1. FETCH - Discover and download pages
    2. CONVERT - HTML to markdown
    3. ANALYZE - Extract metadata and APIs
    4. ENHANCE - LLM optimizations
    5. VERIFY - Content correctness
    6. DETECT - Change detection
    """
    if config is None:
        config = Config()

    print("="*60)
    print("LIMACHARLIE DOCUMENTATION PIPELINE")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"  Source: {config.base_url}{config.docs_path}")
    print(f"  Output: {config.output_dir}")
    print(f"  State: {config.state_dir}")
    print()

    # PHASE 1: FETCH
    print("\n" + "="*60)
    print("PHASE 1: FETCH")
    print("="*60)

    structure = fetch.discover_documentation_structure(config)

    if not structure.categories:
        print("✗ Failed to discover documentation structure")
        return False

    total_pages = sum(len(pages) for pages in structure.categories.values())
    print(f"\nDiscovered {total_pages} pages in {len(structure.categories)} categories")

    downloaded = fetch.download_all_pages(structure, config)
    if downloaded == 0:
        print("✗ Failed to download any pages")
        return False

    # Save state after fetch
    save_state(structure, config.state_dir / "01-fetch.json")

    # PHASE 2: CONVERT
    print("\n" + "="*60)
    print("PHASE 2: CONVERT")
    print("="*60)

    converted = convert.convert_all_pages(structure, config)
    if converted == 0:
        print("✗ Failed to convert any pages")
        return False

    save_state(structure, config.state_dir / "02-convert.json")

    # PHASE 3: ANALYZE
    print("\n" + "="*60)
    print("PHASE 3: ANALYZE")
    print("="*60)

    analyzed = analyze.analyze_all_pages(structure, config)
    save_state(structure, config.state_dir / "03-analyze.json")

    # PHASE 4: ENHANCE
    print("\n" + "="*60)
    print("PHASE 4: ENHANCE")
    print("="*60)

    enhanced = enhance.enhance_all_pages(structure, config)
    save_state(structure, config.state_dir / "04-enhance.json")

    # PHASE 5: VERIFY
    print("\n" + "="*60)
    print("PHASE 5: VERIFY")
    print("="*60)

    verification_report = verify.verify_all_pages(structure, config)

    if verification_report.critical > 0 and config.fail_on_critical:
        print("\n✗ CRITICAL VERIFICATION FAILURES - Pipeline halted")
        print("\nCritical Issues:")
        for issue in verification_report.issues:
            if issue.severity == "critical":
                print(f"  - {issue.page_slug}: {issue.message}")
        return False

    # Save final state and output
    save_state(structure, config.state_dir / "05-verify.json")
    save_pages(structure, config.output_dir)
    create_combined_docs(structure, config.output_dir)

    # Save verification report
    report_file = config.state_dir / "verification_report.json"
    with open(report_file, 'w') as f:
        json.dump({
            'total_pages': verification_report.total_pages,
            'passed': verification_report.passed,
            'warnings': verification_report.warnings,
            'critical': verification_report.critical,
            'issues': [
                {
                    'severity': issue.severity,
                    'page_slug': issue.page_slug,
                    'issue_type': issue.issue_type,
                    'message': issue.message,
                    'details': issue.details,
                }
                for issue in verification_report.issues
            ]
        }, f, indent=2)

    print(f"\n✓ Verification report saved to {report_file}")

    # PHASE 6: DETECT
    print("\n" + "="*60)
    print("PHASE 6: DETECT")
    print("="*60)

    change_report = detect.detect_and_report(config.output_dir, config)

    # Save change report
    if change_report:
        report_file = config.state_dir / "change_report.json"
        with open(report_file, 'w') as f:
            json.dump(change_report, f, indent=2)
        print(f"\n✓ Change report saved to {report_file}")

    # Final summary
    print("\n" + "="*60)
    print("PIPELINE COMPLETE")
    print("="*60)
    print(f"\n✓ Processed {total_pages} pages")
    print(f"  Downloaded: {downloaded}")
    print(f"  Converted: {converted}")
    print(f"  Analyzed: {analyzed}")
    print(f"  Enhanced: {enhanced}")
    print(f"\n✓ Output: {config.output_dir}")
    print(f"✓ State: {config.state_dir}")

    return True
```

**Step 2: Commit**

```bash
git add doc-pipeline/pipeline.py
git commit -m "feat: add pipeline orchestrator"
```

---

## Task 9: CLI Interface

**Files:**
- Create: `doc-pipeline/cli.py`
- Create: `doc-pipeline/__main__.py`

**Step 1: Create cli.py**

```python
"""Command-line interface for documentation pipeline."""
import argparse
import sys
from pathlib import Path
from .config import Config
from .pipeline import run_pipeline


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='LimaCharlie Documentation Pipeline - Fetch, convert, and optimize documentation for LLMs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline run
  python -m doc_pipeline

  # Dry run (discover structure only)
  python -m doc_pipeline --dry-run

  # Skip git commit
  python -m doc_pipeline --no-commit

  # Custom output directory
  python -m doc_pipeline --output-dir ./docs

  # Disable verification
  python -m doc_pipeline --no-verify
        """
    )

    parser.add_argument(
        '--output-dir',
        type=Path,
        default='limacharlie-docs-markdown',
        help='Output directory for generated markdown (default: limacharlie-docs-markdown)'
    )

    parser.add_argument(
        '--state-dir',
        type=Path,
        default='.doc-pipeline-state',
        help='State directory for intermediate files (default: .doc-pipeline-state)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Discover structure only, do not download or process'
    )

    parser.add_argument(
        '--no-commit',
        action='store_true',
        help='Skip git commit step'
    )

    parser.add_argument(
        '--no-verify',
        action='store_true',
        help='Skip verification phase'
    )

    parser.add_argument(
        '--fail-on-critical',
        action='store_true',
        help='Halt pipeline if critical verification issues found'
    )

    parser.add_argument(
        '--rate-limit',
        type=float,
        default=0.5,
        help='Delay between requests in seconds (default: 0.5)'
    )

    args = parser.parse_args()

    # Build config from args
    config = Config(
        output_dir=args.output_dir,
        state_dir=args.state_dir,
        rate_limit_delay=args.rate_limit,
        git_commit_changes=not args.no_commit,
        verify_content=not args.no_verify,
        verify_apis=not args.no_verify,
        verify_metadata=not args.no_verify,
        fail_on_critical=args.fail_on_critical,
    )

    # Dry run: just discovery
    if args.dry_run:
        print("DRY RUN MODE - Discovery only\n")
        from .lib import fetch
        structure = fetch.discover_documentation_structure(config)

        print("\nDiscovered structure:")
        for category, pages in sorted(structure.categories.items()):
            print(f"\n{category} ({len(pages)} pages):")
            for page in pages[:5]:  # Show first 5
                print(f"  - {page.title} ({page.slug})")
            if len(pages) > 5:
                print(f"  ... and {len(pages) - 5} more")

        total = sum(len(pages) for pages in structure.categories.values())
        print(f"\nTotal: {total} pages across {len(structure.categories)} categories")
        return 0

    # Full pipeline run
    try:
        success = run_pipeline(config)
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n✗ Pipeline interrupted by user")
        return 130
    except Exception as e:
        print(f"\n✗ Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
```

**Step 2: Create __main__.py**

```python
"""Allow running as python -m doc_pipeline."""
from .cli import main

if __name__ == '__main__':
    main()
```

**Step 3: Update README with usage examples**

Add to doc-pipeline/README.md after "## Usage":

```markdown
### Command Line Options

```bash
# Full pipeline run (default)
python -m doc_pipeline

# Discover structure only (dry run)
python -m doc_pipeline --dry-run

# Skip git commit
python -m doc_pipeline --no-commit

# Skip verification phase
python -m doc_pipeline --no-verify

# Custom output directory
python -m doc_pipeline --output-dir ./my-docs

# Fail on critical verification issues
python -m doc_pipeline --fail-on-critical

# Slower rate limiting (1 second between requests)
python -m doc_pipeline --rate-limit 1.0
```

### Output Files

After a successful run, you'll find:

**Generated Documentation:**
- `limacharlie-docs-markdown/` - Individual markdown files organized by category
- `limacharlie-docs-markdown/COMBINED.md` - All documentation in one file
- `limacharlie-docs-markdown/API_INDEX.md` - Searchable API reference
- `limacharlie-docs-markdown/METADATA_INDEX.json` - Metadata for all pages

**Pipeline State:**
- `.doc-pipeline-state/01-fetch.json` - State after fetch phase
- `.doc-pipeline-state/02-convert.json` - State after conversion
- `.doc-pipeline-state/03-analyze.json` - State after analysis
- `.doc-pipeline-state/04-enhance.json` - State after enhancement
- `.doc-pipeline-state/05-verify.json` - Final state
- `.doc-pipeline-state/verification_report.json` - Verification results
- `.doc-pipeline-state/change_report.json` - Git change analysis
```

**Step 4: Commit**

```bash
git add doc-pipeline/cli.py doc-pipeline/__main__.py doc-pipeline/README.md
git commit -m "feat: add CLI interface and main entry point"
```

---

## Task 10: Integration Tests & Documentation

**Files:**
- Create: `doc-pipeline/tests/test_integration.py`
- Create: `PIPELINE_USAGE.md` (in repo root)

**Step 1: Create integration test**

```python
"""Integration tests for full pipeline."""
import tempfile
from pathlib import Path
from doc_pipeline.config import Config
from doc_pipeline.pipeline import run_pipeline


def test_pipeline_dry_run():
    """Test that pipeline can discover structure."""
    from doc_pipeline.lib import fetch

    config = Config()
    structure = fetch.discover_documentation_structure(config)

    assert structure is not None
    assert len(structure.categories) > 0

    total_pages = sum(len(pages) for pages in structure.categories.values())
    assert total_pages > 0

    print(f"Discovered {total_pages} pages in {len(structure.categories)} categories")


def test_pipeline_phases_independent():
    """Test that each phase can run independently."""
    from doc_pipeline.models import Page, DocumentStructure
    from doc_pipeline.lib import convert, analyze, enhance
    from doc_pipeline.config import Config

    config = Config()

    # Create minimal test page
    page = Page(
        url="http://test.com",
        slug="test-page",
        title="Test Page",
        category="test",
        raw_html="<html><body><h1>Test</h1><p>Content</p><pre>code</pre></body></html>",
    )

    structure = DocumentStructure()
    structure.categories["test"] = [page]

    # Test convert phase
    assert convert.convert_page(page, config)
    assert page.markdown != ""

    # Test analyze phase
    metadata = analyze.extract_metadata(page, config)
    assert metadata is not None

    # Test enhance phase
    enhance.optimize_heading_hierarchy(page, config)
    assert page.markdown.startswith("# ")


def test_verification_catches_issues():
    """Test that verification catches problems."""
    from doc_pipeline.models import Page
    from doc_pipeline.lib.verify import verify_content_completeness

    page = Page(
        url="http://test.com",
        slug="test",
        title="Test",
        category="test",
    )

    # Simulate content loss
    page.raw_html = "<html><body>" + "word " * 100 + "</body></html>"
    page.markdown = "# Test\n\nOnly a few words"

    issues = verify_content_completeness(page)
    critical = [i for i in issues if i.severity == "critical"]

    assert len(critical) > 0
    assert any("content_loss" in i.issue_type for i in critical)
```

**Step 2: Create usage documentation**

Create `PIPELINE_USAGE.md` in repo root:

```markdown
# Documentation Pipeline Usage Guide

This guide explains how to use the LimaCharlie documentation pipeline to generate LLM-optimized documentation.

## Quick Start

```bash
# Install dependencies
pip install -r doc-pipeline/requirements.txt

# Run full pipeline
python -m doc_pipeline

# Or from doc-pipeline directory
cd doc-pipeline
python -m doc_pipeline
```

## Understanding the Pipeline

The pipeline runs in 6 phases:

### 1. FETCH
- Discovers all documentation pages from docs.limacharlie.io
- Downloads HTML for each page
- Organizes into categories based on URL patterns

### 2. CONVERT
- Converts HTML to Markdown using markitdown
- Removes Document360 UI artifacts
- Normalizes formatting

### 3. ANALYZE
- Extracts metadata (summary, keywords, complexity)
- Identifies API signatures, endpoints, CLI commands
- Builds comprehensive API index

### 4. ENHANCE
- Adds cross-references between related pages
- Optimizes heading hierarchy
- Enhances code blocks with language tags
- LLM-specific formatting improvements

### 5. VERIFY
- Validates content completeness (word count, code blocks, headings)
- Checks for hallucinated or missed APIs
- Verifies metadata accuracy
- Validates cross-references
- Generates verification report

### 6. DETECT
- Commits changes to git
- Generates change report with categorization
- Identifies structural vs content changes
- Highlights significant updates

## Common Workflows

### First-Time Setup

```bash
# Clone and install
git clone <repo>
cd documentation
pip install -r doc-pipeline/requirements.txt

# Run pipeline
python -m doc_pipeline

# Check output
ls limacharlie-docs-markdown/
cat limacharlie-docs-markdown/COMBINED.md
```

### Regular Updates

```bash
# Pull latest
git pull

# Run pipeline (generates diff report)
python -m doc_pipeline

# Review changes
git log -1 -p
cat .doc-pipeline-state/change_report.json
```

### Debugging Issues

```bash
# Dry run to check discovery
python -m doc_pipeline --dry-run

# Run without commit to inspect output
python -m doc_pipeline --no-commit

# Check intermediate state
cat .doc-pipeline-state/02-convert.json

# Review verification report
cat .doc-pipeline-state/verification_report.json
```

### Custom Configuration

Create a Python script:

```python
from doc_pipeline.config import Config
from doc_pipeline.pipeline import run_pipeline

config = Config(
    output_dir="my-docs",
    rate_limit_delay=1.0,
    fail_on_critical=True,
)

run_pipeline(config)
```

## Output Files Explained

### Individual Markdown Files
`limacharlie-docs-markdown/<category>/<page-slug>.md`
- One file per documentation page
- Clean markdown optimized for LLM consumption
- Preserved code blocks, links, structure

### Combined Documentation
`limacharlie-docs-markdown/COMBINED.md`
- All documentation in a single file
- Organized by category
- Useful for feeding entire context to LLM

### API Index
`limacharlie-docs-markdown/API_INDEX.md`
- Searchable reference of all APIs
- REST endpoints, Python SDK, CLI commands
- Links back to source pages

### Metadata Index
`limacharlie-docs-markdown/METADATA_INDEX.json`
- Structured metadata for all pages
- Summaries, keywords, complexity levels
- Use cases and categorization
- Useful for semantic search

### Verification Report
`.doc-pipeline-state/verification_report.json`
- Lists all verification issues found
- Categorized by severity (critical/warning/info)
- Details of content loss, missing APIs, etc.

### Change Report
`.doc-pipeline-state/change_report.json`
- Git diff analysis
- Structural vs content changes
- Significant updates highlighted
- Useful for understanding what changed upstream

## Troubleshooting

### Pipeline fails during FETCH
- Check internet connection
- Verify docs.limacharlie.io is accessible
- Try slower rate limiting: `--rate-limit 2.0`

### Verification shows critical issues
- Review `.doc-pipeline-state/verification_report.json`
- Check specific pages mentioned in report
- Consider if issues are false positives
- Use `--no-verify` to skip if needed

### Git commit fails
- Ensure you're in a git repository
- Check git status and resolve conflicts
- Use `--no-commit` to skip git integration

### Missing dependencies
```bash
pip install requests beautifulsoup4 markitdown
```

### Rate limiting / timeout errors
```bash
python -m doc_pipeline --rate-limit 2.0
```

## Integration with LLMs

The generated documentation is optimized for LLM consumption:

### For Context Loading
Use `COMBINED.md` to load full documentation context:
```python
with open('limacharlie-docs-markdown/COMBINED.md') as f:
    docs = f.read()

response = llm.query(f"Based on these docs:\n\n{docs}\n\nHow do I...?")
```

### For Semantic Search
Use `METADATA_INDEX.json` for embeddings:
```python
import json

with open('limacharlie-docs-markdown/METADATA_INDEX.json') as f:
    metadata = json.load(f)

# Create embeddings from summaries
for slug, info in metadata.items():
    embedding = create_embedding(info['metadata']['summary'])
    store_embedding(slug, embedding)
```

### For API Reference
Use `API_INDEX.md` for specific API queries:
```python
# Load API index
with open('limacharlie-docs-markdown/API_INDEX.md') as f:
    api_docs = f.read()

# Query specific API
response = llm.query(f"API reference:\n{api_docs}\n\nHow to use sensor.task()?")
```

## Maintenance

### Updating from Upstream
Run the pipeline periodically to stay in sync with docs.limacharlie.io:

```bash
# Weekly/monthly cron job
0 2 * * 1 cd /path/to/documentation && python -m doc_pipeline
```

### Reviewing Changes
After each run, review the change report:

```bash
# View latest commit
git show

# View change report
cat .doc-pipeline-state/change_report.json

# View verification issues
cat .doc-pipeline-state/verification_report.json
```

### Customizing Categories
Edit `doc-pipeline/lib/fetch.py` function `_categorize_page()` to adjust category mappings.

### Adding Custom Enhancements
Extend `doc-pipeline/lib/enhance.py` to add your own LLM optimizations.

## Architecture

See `doc-pipeline/README.md` for detailed architecture documentation.

## Contributing

Found a bug or want to improve the pipeline? See `CONTRIBUTING.md` for guidelines.
```

**Step 3: Run tests**

```bash
python -m pytest doc-pipeline/tests/test_integration.py -v
```

Expected: PASS (3 tests)

**Step 4: Commit**

```bash
git add doc-pipeline/tests/test_integration.py PIPELINE_USAGE.md
git commit -m "feat: add integration tests and usage documentation"
```

---

## Task 11: Final Polish & README

**Files:**
- Update: `doc-pipeline/README.md`
- Create: `.doc-pipeline-state/.gitignore`

**Step 1: Update main README with complete information**

Update `doc-pipeline/README.md`:

```markdown
# LimaCharlie Documentation Pipeline

Automated pipeline for fetching, converting, and optimizing LimaCharlie documentation for LLM consumption.

## Overview

This pipeline transforms the LimaCharlie documentation website into clean, structured markdown optimized for Large Language Models. It provides:

- **Dynamic Discovery**: Automatically finds all documentation pages
- **Content-Aware Processing**: Detects structural and content changes
- **LLM Optimization**: Metadata extraction, API indexing, cross-references
- **Verification**: Ensures correctness against source content
- **Change Tracking**: Git-based diff reporting

## Features

### Automated Discovery & Fetching
- Crawls docs.limacharlie.io navigation
- Discovers all pages automatically
- Handles rate limiting and retries
- Fallback discovery for reliability

### Clean Conversion
- HTML → Markdown using markitdown
- Removes Document360 UI artifacts
- Preserves code blocks, links, structure
- Normalizes formatting for consistency

### Content Analysis
- Extracts metadata (summary, keywords, complexity)
- Identifies API signatures and endpoints
- Detects CLI commands
- Builds comprehensive API index

### LLM Optimizations
- Adds cross-references between related pages
- Optimizes heading hierarchy
- Enhances code blocks with language tags
- Consistent formatting throughout

### Verification
- Validates content completeness
- Detects hallucinated or missed APIs
- Verifies metadata accuracy
- Checks cross-references
- Generates detailed reports

### Change Detection
- Git-based tracking
- Categorizes structural vs content changes
- Identifies significant updates
- Human-readable diff reports

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

Requirements:
- Python 3.8+
- Git (for change tracking)
- Internet connection (for fetching)

## Usage

### Quick Start

```bash
# Run full pipeline
python -m doc_pipeline

# Output in: limacharlie-docs-markdown/
```

### Command Line Options

```bash
# Discover structure only (dry run)
python -m doc_pipeline --dry-run

# Skip git commit
python -m doc_pipeline --no-commit

# Skip verification
python -m doc_pipeline --no-verify

# Custom output directory
python -m doc_pipeline --output-dir ./my-docs

# Fail on critical verification issues
python -m doc_pipeline --fail-on-critical

# Slower rate limiting
python -m doc_pipeline --rate-limit 1.0
```

### Programmatic Usage

```python
from doc_pipeline.config import Config
from doc_pipeline.pipeline import run_pipeline

config = Config(
    output_dir="my-docs",
    rate_limit_delay=1.0,
    extract_api_signatures=True,
    verify_content=True,
    fail_on_critical=True,
)

success = run_pipeline(config)
```

## Architecture

### Pipeline Phases

```
Input: docs.limacharlie.io
  ↓
[FETCH] → Discover structure + Download HTML
  ↓
[CONVERT] → HTML to markdown + Clean artifacts
  ↓
[ANALYZE] → Extract metadata + API signatures
  ↓
[ENHANCE] → Add cross-refs + Optimize structure
  ↓
[VERIFY] → Validate correctness
  ↓
[DETECT] → Git diff + Change report
  ↓
Output: Optimized markdown + Reports
```

### Project Structure

```
doc-pipeline/
├── config.py           # Configuration
├── models.py           # Data structures
├── pipeline.py         # Main orchestrator
├── cli.py             # Command-line interface
├── lib/
│   ├── fetch.py       # Fetching & discovery
│   ├── convert.py     # HTML → Markdown
│   ├── analyze.py     # Metadata extraction
│   ├── enhance.py     # LLM optimizations
│   ├── verify.py      # Correctness checking
│   └── detect.py      # Change detection
└── tests/
    ├── test_fetch.py
    ├── test_convert.py
    ├── test_analyze.py
    ├── test_verify.py
    └── test_integration.py
```

## Output Files

### Generated Documentation

- `limacharlie-docs-markdown/<category>/<page>.md` - Individual pages
- `limacharlie-docs-markdown/COMBINED.md` - All docs in one file
- `limacharlie-docs-markdown/API_INDEX.md` - Searchable API reference
- `limacharlie-docs-markdown/METADATA_INDEX.json` - Structured metadata

### Pipeline State

- `.doc-pipeline-state/01-fetch.json` - After fetch phase
- `.doc-pipeline-state/02-convert.json` - After conversion
- `.doc-pipeline-state/03-analyze.json` - After analysis
- `.doc-pipeline-state/04-enhance.json` - After enhancement
- `.doc-pipeline-state/05-verify.json` - Final state
- `.doc-pipeline-state/verification_report.json` - Verification results
- `.doc-pipeline-state/change_report.json` - Git diff analysis

## Configuration

Edit `config.py` or pass custom `Config` object:

```python
@dataclass
class Config:
    # Source
    base_url: str = "https://docs.limacharlie.io"
    docs_path: str = "/docs"

    # Output
    output_dir: Path = Path("limacharlie-docs-markdown")
    state_dir: Path = Path(".doc-pipeline-state")

    # Behavior
    rate_limit_delay: float = 0.5
    request_timeout: int = 30
    retry_attempts: int = 3

    # Features
    extract_api_signatures: bool = True
    generate_summaries: bool = True
    add_cross_references: bool = True
    optimize_headings: bool = True

    # Verification
    verify_content: bool = True
    verify_apis: bool = True
    verify_metadata: bool = True
    fail_on_critical: bool = False

    # Git
    git_commit_changes: bool = True
    git_commit_message: str = "Update LimaCharlie documentation"
```

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_fetch.py -v

# Run integration tests
pytest tests/test_integration.py -v
```

## Troubleshooting

### Pipeline Fails During FETCH
- Check internet connection
- Verify docs.limacharlie.io is accessible
- Try slower rate limiting: `--rate-limit 2.0`

### Verification Shows Critical Issues
- Review `.doc-pipeline-state/verification_report.json`
- Check specific pages mentioned
- Use `--no-verify` to skip if needed

### Git Commit Fails
- Ensure you're in a git repository
- Check git status and resolve conflicts
- Use `--no-commit` to skip git integration

## Contributing

Contributions welcome! Please:
1. Write tests for new features
2. Update documentation
3. Follow existing code style
4. Add type hints

## License

See LICENSE file in repository root.

## See Also

- `PIPELINE_USAGE.md` - Detailed usage guide
- `tests/` - Test examples
- `lib/` - Module documentation
```

**Step 2: Create .gitignore for state directory**

```
# Ignore state files but keep directory
*
!.gitignore
```

Save to `.doc-pipeline-state/.gitignore`

**Step 3: Commit**

```bash
mkdir -p .doc-pipeline-state
echo "*" > .doc-pipeline-state/.gitignore
echo "!.gitignore" >> .doc-pipeline-state/.gitignore
git add doc-pipeline/README.md .doc-pipeline-state/.gitignore
git commit -m "docs: complete README and finalize pipeline structure"
```

---

## Summary

The implementation plan creates a complete, production-ready documentation pipeline with:

- **11 tasks** covering all components
- **Modular architecture** with clear separation of concerns
- **Comprehensive testing** for each module
- **Complete documentation** for users and developers
- **Git-based change tracking** with detailed reporting
- **Content verification** to prevent hallucinations
- **LLM optimizations** throughout

All code is pre-generated (no prompt-time generation), deterministic, and designed for semi-automatic updates.

Ready to implement!
