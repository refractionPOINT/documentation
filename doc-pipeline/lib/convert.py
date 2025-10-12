"""HTML to Markdown conversion and cleaning."""
import re
import subprocess
from typing import Optional, Tuple
from pathlib import Path
from bs4 import BeautifulSoup

try:
    from ..models import Page
    from ..config import Config
except ImportError:
    # For testing when importing as a module
    from models import Page
    from config import Config


def save_extraction_debug(slug: str, html: str, extracted: str, markdown: str, method: str = "unknown"):
    """
    Save extraction artifacts for debugging.

    Creates .doc-pipeline-state/extraction-debug/<slug>/ with:
    - full.html: First 50KB of original HTML
    - extracted.html: What was extracted
    - output.md: Final markdown
    - info.txt: Extraction method and stats
    """
    try:
        debug_dir = Path('.doc-pipeline-state/extraction-debug') / slug
        debug_dir.mkdir(parents=True, exist_ok=True)

        # Save full HTML (limited to 50KB to avoid huge files)
        (debug_dir / 'full.html').write_text(html[:50000], encoding='utf-8')

        # Save extracted HTML
        (debug_dir / 'extracted.html').write_text(extracted, encoding='utf-8')

        # Save markdown output
        (debug_dir / 'output.md').write_text(markdown, encoding='utf-8')

        # Save info
        info = f"""Extraction Method: {method}
Original HTML length: {len(html)} chars
Extracted HTML length: {len(extracted)} chars
Markdown length: {len(markdown)} chars
Word count (markdown): {len(markdown.split())} words
"""
        (debug_dir / 'info.txt').write_text(info, encoding='utf-8')
    except Exception as e:
        # Don't fail conversion if debug save fails
        print(f"Warning: Could not save debug artifacts for {slug}: {e}")


def extract_main_content(html: str, slug: str = "") -> Tuple[str, str]:
    """
    Extract main article content from Document360 HTML using robust heuristics.

    Returns:
        Tuple of (extracted_html, method_used)

    Strategy:
    1. Try Document360-specific selectors
    2. Use heuristics (most paragraphs, longest text, code blocks)
    3. Validate extraction (minimum content requirements)
    4. Fall back to full HTML if extraction seems wrong
    """
    if not html:
        return "", "empty"

    try:
        soup = BeautifulSoup(html, 'html.parser')

        # Collect candidates with scoring
        candidates = []

        # Method 1: Standard Document360 selectors (prioritized by reliability)
        d360_selectors = [
            # Document360 article content (HIGHEST priority - actual content)
            '.content_block_text',
            '.default',  # Often wraps content_block_text
            # Other Document360 specific classes
            '.main_content_block',
            '.docs-main-content',
            '.content_block',
            '.d-article-content',
            '.article-content',
            '.doc-content',
            # Generic semantic tags (lower priority)
            'article',
            '[role="main"]',
            'main',
        ]

        for selector in d360_selectors:
            # Use select() to get ALL matches, not just first one
            elems = soup.select(selector)
            for i, elem in enumerate(elems):
                text_len = len(elem.get_text(strip=True))
                # Skip empty elements
                if text_len < 10:
                    continue

                # Highest boost for actual content classes
                if selector in ['.content_block_text', '.default']:
                    boost = 50000
                # High boost for other Document360-specific selectors
                elif 'content' in selector.lower() and '.' in selector:
                    boost = 10000
                else:
                    boost = 0
                score = text_len + boost
                method_name = f'selector:{selector}[{i}]' if len(elems) > 1 else f'selector:{selector}'
                candidates.append((method_name, elem, score))

        # Method 2: Find element with most paragraph tags (good indicator of content)
        all_containers = soup.find_all(['div', 'section', 'article'])
        for container in all_containers:
            p_count = len(container.find_all('p', recursive=True))
            if p_count >= 3:  # At least 3 paragraphs indicates real content
                score = p_count * 200  # Weight paragraphs heavily
                candidates.append((f'p-count:{p_count}', container, score))

        # Method 3: Find element with most text (longest content)
        for elem in all_containers:
            text_len = len(elem.get_text(strip=True))
            if text_len > 500:  # Minimum content threshold
                candidates.append((f'text-len:{text_len}', elem, text_len))

        # Method 4: Find element with code blocks (technical docs often have code)
        for elem in all_containers:
            code_blocks = len(elem.find_all(['pre', 'code'], recursive=True))
            if code_blocks >= 2:  # At least 2 code blocks
                text_len = len(elem.get_text(strip=True))
                score = text_len + (code_blocks * 500)  # Boost score for code
                candidates.append((f'code-blocks:{code_blocks}', elem, score))

        if not candidates:
            # Absolute fallback: use body
            body = soup.find('body')
            if body:
                return str(body), "fallback:body"
            return html, "fallback:full-html"

        # Sort by score and get best candidate
        candidates.sort(key=lambda x: x[2], reverse=True)
        method, best_elem, score = candidates[0]

        extracted = str(best_elem)

        # Validation: Check if extraction looks reasonable
        word_count = len(best_elem.get_text().split())
        heading_count = len(best_elem.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
        code_blocks = len(best_elem.find_all(['pre', 'code']))

        # Quality thresholds
        min_words = 50
        min_headings = 1

        # If extraction seems too small, try next best or full HTML
        if word_count < min_words or (heading_count < min_headings and code_blocks == 0):
            # Try second-best candidate if available
            if len(candidates) > 1:
                method2, elem2, score2 = candidates[1]
                word_count2 = len(elem2.get_text().split())
                if word_count2 > word_count * 2:  # Significantly more content
                    return str(elem2), f"{method2}:retry"

            # Last resort: use full HTML and let markitdown handle it
            return html, f"{method}:failed-validation-using-full-html"

        return extracted, method

    except Exception as e:
        print(f"Warning: Could not extract content with BeautifulSoup: {e}")
        return html, f"error:{e}"


def html_to_markdown(html: str, slug: str = "") -> Tuple[str, str]:
    """
    Convert HTML to markdown using markitdown.

    Returns:
        Tuple of (markdown, extraction_method)
    """
    try:
        # First extract main content to avoid converting navigation/UI elements
        main_content, method = extract_main_content(html, slug)

        # Use markitdown via subprocess (reads from stdin when no filename given)
        result = subprocess.run(
            ['markitdown', '--extension', 'html'],
            input=main_content,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True
        )
        return result.stdout, method
    except Exception as e:
        print(f"Error converting HTML: {e}")
        return "", f"error:{e}"


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


def convert_page(page: Page, config: Config, save_debug: bool = False) -> bool:
    """
    Convert a page's HTML to cleaned markdown.

    Updates page.markdown field.
    Returns True on success.

    Args:
        page: Page to convert
        config: Configuration
        save_debug: If True, save extraction artifacts for debugging
    """
    if not page.raw_html:
        print(f"✗ No HTML content for {page.slug}")
        return False

    try:
        # Convert to markdown (now returns tuple)
        raw_md, extraction_method = html_to_markdown(page.raw_html, page.slug)
        if not raw_md:
            print(f"✗ No markdown generated for {page.slug}")
            return False

        # Clean artifacts
        cleaned = clean_markdown_content(raw_md)

        # Normalize formatting
        normalized = normalize_formatting(cleaned)

        page.markdown = normalized

        # Save debug artifacts if requested or if page seems problematic
        word_count = len(normalized.split())
        if save_debug or word_count < 100:  # Auto-save for suspicious pages
            extracted_html, _ = extract_main_content(page.raw_html, page.slug)
            save_extraction_debug(
                page.slug,
                page.raw_html,
                extracted_html,
                normalized,
                extraction_method
            )
            if word_count < 100:
                print(f"⚠ {page.slug}: Only {word_count} words (method: {extraction_method})")

        print(f"✓ Converted: {page.slug} (method: {extraction_method})")
        return True

    except Exception as e:
        print(f"✗ Error converting {page.slug}: {e}")
        import traceback
        traceback.print_exc()
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
