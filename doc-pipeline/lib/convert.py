"""HTML to Markdown conversion and cleaning."""
import re
import subprocess
from typing import Optional

try:
    from ..models import Page
    from ..config import Config
except ImportError:
    # For testing when importing as a module
    from models import Page
    from config import Config


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
