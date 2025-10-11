"""Content analysis and metadata extraction."""
import re
from typing import Dict, List, Optional

# Import from parent package
try:
    from ..models import Page
    from ..config import Config
except ImportError:
    # Fallback for direct execution or testing
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from models import Page
    from config import Config


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
