"""Content quality filtering for LLM-optimized documentation."""
import re
from typing import List, Tuple, Optional, Dict
from pathlib import Path

try:
    from ..models import Page
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from models import Page


def assess_content_quality(page: Page) -> Tuple[bool, str]:
    """
    Assess if a page has sufficient quality content for LLM consumption.

    Args:
        page: Page to assess

    Returns:
        Tuple of (is_quality, reason)
        - is_quality: True if page has valuable content
        - reason: Explanation of quality decision
    """
    if not page.markdown:
        return False, "No markdown content"

    content = page.markdown

    # Extract actual content (skip title and metadata)
    lines = content.split('\n')
    content_lines = []
    skip_patterns = [
        '* 1 Minute to read', '* 2 Minutes to read', '* 3 Minutes to read',
        '* Print', '* Share', '* Dark', 'Light',
        '###### Related articles', '###### What\'s Next',
        'Tags', '* [', 'Updated on', 'Minutes to read'
    ]

    in_content = False
    for line in lines:
        # Skip title
        if line.strip().startswith('# '):
            in_content = True
            continue

        # Skip metadata and navigation
        if any(pattern in line for pattern in skip_patterns):
            continue

        if in_content:
            content_lines.append(line)

    actual_content = '\n'.join(content_lines).strip()

    # Count meaningful content
    word_count = len(actual_content.split())
    heading_count = len(re.findall(r'^#{2,6}\s+', actual_content, re.MULTILINE))
    code_block_count = len(re.findall(r'```', actual_content)) // 2
    paragraph_count = len(re.findall(r'\n\n.+', actual_content))
    list_item_count = len(re.findall(r'^\s*[-*]\s+\w+', actual_content, re.MULTILINE))

    # Quality thresholds
    MIN_WORDS = 50
    MIN_SUBSTANTIVE_CONTENT = 30  # Either paragraphs, list items, or code

    # Check for stub pages
    if word_count < MIN_WORDS:
        # Allow short pages if they have code examples
        if code_block_count >= 1 and word_count >= 20:
            return True, f"Short but has code examples ({code_block_count} blocks)"
        return False, f"Too few words ({word_count} < {MIN_WORDS})"

    # Check for link-only pages (just navigation)
    link_count = len(re.findall(r'\[.+?\]\(.+?\)', actual_content))
    if link_count > word_count / 10:  # More than 10% of words are links
        if paragraph_count == 0 and code_block_count == 0:
            return False, f"Link-only page ({link_count} links, no content)"

    # Check for substantive content
    substantive_count = paragraph_count + list_item_count + (code_block_count * 2)
    if substantive_count < MIN_SUBSTANTIVE_CONTENT and word_count < 100:
        return False, f"Insufficient substantive content ({substantive_count} items)"

    # Passed all checks
    return True, f"Quality content ({word_count} words, {heading_count} headings, {code_block_count} code blocks)"


def filter_low_quality_pages(
    pages: List[Page],
    strict: bool = True
) -> Tuple[List[Page], List[Tuple[str, str]]]:
    """
    Filter out low-quality stub pages.

    Args:
        pages: List of pages to filter
        strict: If True, remove all low-quality pages. If False, only remove empty.

    Returns:
        Tuple of (quality_pages, removed_pages_with_reasons)
    """
    quality_pages = []
    removed_pages = []

    for page in pages:
        is_quality, reason = assess_content_quality(page)

        if is_quality:
            quality_pages.append(page)
        else:
            removed_pages.append((page.slug, reason))

    return quality_pages, removed_pages


def strip_human_metadata(markdown: str) -> str:
    """
    Strip all human-oriented UI metadata for LLM optimization.

    Removes:
    - "X Minutes to read"
    - Print/Share/Dark/Light buttons
    - Feedback forms
    - "Related articles" and "What's Next" sections
    - Tag sections
    - Timestamps

    Args:
        markdown: Original markdown content

    Returns:
        Cleaned markdown optimized for LLM consumption
    """
    if not markdown:
        return ""

    lines = markdown.split('\n')
    cleaned_lines = []
    skip_until_next_section = False

    # Patterns to completely remove
    remove_patterns = [
        r'^\* \d+ Minutes? to read',
        r'^Minutes? to read:?\s*\d+',  # Also match "Minutes to read: 5" format
        r'^\* Print\s*$',
        r'^\* Share\s*$',
        r'^\* Dark\s*$',
        r'^\* Light\s*$',
        r'^Light\s*$',
        r'^Dark\s*$',
        r'^Article summary\s*$',
        r'^Did you find this summary helpful\?',
        r'^Thank you for your feedback!',
        r'^Was this article helpful\?',
        r'^How can we improve this article\?',
        r'^Your feedback',
        r'^Character limit :',
        r'^Email \(Optional\)',
        r'^Powered by Document360',
        r'^Updated on',
        r'^\* Updated on',  # With bullet point
        # Feedback form elements
        r'^Yes\s+No\s*$',  # Feedback yes/no buttons
        r'^\[\s*\]\s+Need more information\s*$',
        r'^\[\s*\]\s+Difficult to understand\s*$',
        r'^\[\s*\]\s+Inaccurate or irrelevant content\s*$',
        r'^\[\s*\]\s+Missing/broken link\s*$',
        r'^\[\s*\]\s+Others\s*$',
        r'^\[\s*\]\s+Notify me about change\s*$',
        r'^Comment\s*$',
        r'^Comment \(Optional\)\s*$',
        r'^Please enter your comment\s*$',
        r'^Email\s*$',
        r'^Please enter a valid email\s*$',
        r'^Cancel\s*$',
        # Navigation/UI chrome
        r'^Share this\s*$',
        r'^Contents\s+x\s*$',
        r'^\* v\d+\s*$',  # Version selector
        r'^\+ \[v\d+.*?\]\(/.*?\)\s*$',  # Version links
        r'^\* \[.*?\]\(.*?\)\s*$',  # Navigation links at top
        r'^!\[.*?\]\(https://cdn\.document360\.io.*?\)',  # Logo images
        r'^\[Powered by.*?Document360.*?\]',  # Powered by footer
    ]

    # Section headers to remove entirely (with their content)
    skip_sections = [
        '###### Related articles',
        '###### What\'s Next',
        '## Tags',
        'Tags',
    ]

    # Find first real content heading (skip all navigation/chrome before it)
    content_start = 0
    for idx, line in enumerate(lines):
        # Look for first H1 heading that's actual content (not just "Contents" or similar)
        if line.strip().startswith('# ') and len(line.strip()) > 3:
            heading_text = line.strip()[2:].lower()
            # Skip if it's a navigation heading
            if heading_text not in ['contents', 'menu', 'navigation', 'toc']:
                content_start = idx
                break

    i = content_start
    while i < len(lines):
        line = lines[i]

        # Check if this is a section to skip
        if any(section in line for section in skip_sections):
            skip_until_next_section = True
            i += 1
            continue

        # Stop skipping when we hit a new section
        if skip_until_next_section:
            # New heading (not the skip-worthy kind)
            if line.strip().startswith('#') and not any(section in line for section in skip_sections):
                skip_until_next_section = False
            else:
                i += 1
                continue

        # Check if line matches any remove pattern
        if any(re.match(pattern, line.strip()) for pattern in remove_patterns):
            i += 1
            continue

        # Remove standalone "---" dividers that separate metadata
        if line.strip() == '---':
            # Check if this is between metadata sections
            if i > 0 and i < len(lines) - 1:
                # If surrounded by empty lines or metadata, skip it
                prev_empty = not lines[i-1].strip()
                next_empty = not lines[i+1].strip() if i+1 < len(lines) else True
                if prev_empty or next_empty:
                    i += 1
                    continue

        cleaned_lines.append(line)
        i += 1

    result = '\n'.join(cleaned_lines)

    # Remove excessive blank lines (more than 2 in a row)
    result = re.sub(r'\n{3,}', '\n\n', result)

    # Remove trailing whitespace
    result = result.strip()

    return result


def optimize_for_llm(page: Page) -> bool:
    """
    Optimize page content for LLM consumption.

    Applies all LLM optimizations:
    - Strip human UI metadata
    - Convert /docs/ links to relative slug references
    - Remove numbered directory prefixes from internal references

    Args:
        page: Page to optimize (modified in place)

    Returns:
        True if successful
    """
    if not page.markdown:
        return False

    # Strip human metadata
    cleaned = strip_human_metadata(page.markdown)

    # Convert /docs/ URLs to relative references
    # [Link](/docs/some-page) → [Link](some-page.md)
    cleaned = re.sub(
        r'\[([^\]]+)\]\(/docs/([^)]+)\)',
        r'[\1](\2.md)',
        cleaned
    )

    # Remove numbered prefixes from links if they exist
    # [Link](01-category/page.md) → [Link](category/page.md)
    cleaned = re.sub(
        r'\[([^\]]+)\]\((\d{2}-[^/]+)/([^)]+)\)',
        r'[\1](\2/\3)',
        cleaned
    )
    cleaned = re.sub(
        r'\[([^\]]+)\]\((\d{2}-[^)]+)\.md\)',
        r'[\1](\2.md)',
        cleaned
    )

    page.markdown = cleaned
    return True


def apply_quality_pipeline(
    pages: List[Page],
    remove_low_quality: bool = True
) -> Tuple[List[Page], Dict[str, List[str]]]:
    """
    Apply complete quality pipeline to pages.

    Args:
        pages: Input pages
        remove_low_quality: If True, remove low-quality pages

    Returns:
        Tuple of (processed_pages, report_dict)
    """
    report = {
        'removed': [],
        'optimized': [],
        'errors': []
    }

    # Filter low quality if requested
    if remove_low_quality:
        quality_pages, removed = filter_low_quality_pages(pages, strict=True)
        report['removed'] = [f"{slug}: {reason}" for slug, reason in removed]
        print(f"  Quality filter: Kept {len(quality_pages)}/{len(pages)} pages")
        pages = quality_pages

    # Optimize all remaining pages for LLM
    for page in pages:
        try:
            if optimize_for_llm(page):
                report['optimized'].append(page.slug)
        except Exception as e:
            report['errors'].append(f"{page.slug}: {e}")

    return pages, report
