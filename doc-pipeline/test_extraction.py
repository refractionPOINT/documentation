#!/usr/bin/env python3
"""
Test improved extraction on specific failed pages.

Usage:
    python3 test_extraction.py adapter-types-evtx add-ons-api-integrations
"""
import sys
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from lib.convert import extract_main_content, html_to_markdown, convert_page
from models import Page
from config import Config


def test_page(slug: str):
    """Test extraction on a specific page."""
    print(f"\n{'='*60}")
    print(f"Testing: {slug}")
    print('='*60)

    # Load page from fetch state
    state_file = Path('.doc-pipeline-state/01-fetch.json')
    if not state_file.exists():
        print(f"❌ State file not found: {state_file}")
        print("Run 'python3 -m doc-pipeline' first to fetch pages")
        return False

    with open(state_file) as f:
        state = json.load(f)

    # Find the page
    page_data = None
    for category, pages in state['categories'].items():
        for p in pages:
            if p['slug'] == slug:
                page_data = p
                break
        if page_data:
            break

    if not page_data:
        print(f"❌ Page not found: {slug}")
        return False

    print(f"✓ Found page: {page_data['title']}")
    print(f"  URL: {page_data['url']}")
    print(f"  HTML size: {len(page_data['raw_html'])} bytes")

    # Test extraction
    html = page_data['raw_html']
    extracted, method = extract_main_content(html, slug)

    print(f"\nExtraction method: {method}")
    print(f"  Extracted size: {len(extracted)} bytes")

    # Parse extracted to get stats
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(extracted, 'html.parser')

    text = soup.get_text(strip=True)
    word_count = len(text.split())
    heading_count = len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
    code_blocks = len(soup.find_all(['pre', 'code']))
    paragraphs = len(soup.find_all('p'))

    print(f"\nExtracted HTML stats:")
    print(f"  Words: {word_count}")
    print(f"  Headings: {heading_count}")
    print(f"  Code blocks: {code_blocks}")
    print(f"  Paragraphs: {paragraphs}")

    # Test markdown conversion
    markdown, _ = html_to_markdown(html, slug)
    md_word_count = len(markdown.split())
    md_lines = len(markdown.split('\n'))

    print(f"\nMarkdown output:")
    print(f"  Words: {md_word_count}")
    print(f"  Lines: {md_lines}")

    # Check quality
    print(f"\nQuality assessment:")
    if md_word_count < 50:
        print(f"  ❌ FAIL: Only {md_word_count} words (expected >50)")
        success = False
    elif code_blocks > 0 and '```' not in markdown:
        print(f"  ⚠️  WARNING: {code_blocks} code blocks in HTML but none in markdown")
        success = False
    elif word_count > 0 and md_word_count < word_count * 0.3:
        retention = (md_word_count / word_count * 100)
        print(f"  ⚠️  WARNING: Only {retention:.1f}% word retention")
        success = False
    else:
        print(f"  ✅ PASS: {md_word_count} words, looks reasonable")
        success = True

    # Show first few lines of markdown
    print(f"\nFirst 500 characters of markdown:")
    print("-" * 60)
    print(markdown[:500])
    if len(markdown) > 500:
        print("...")
    print("-" * 60)

    # Debug artifacts are saved automatically in convert_page
    debug_dir = Path('.doc-pipeline-state/extraction-debug') / slug
    if debug_dir.exists():
        print(f"\n✓ Debug artifacts saved to: {debug_dir}")
        print(f"  - full.html: Original HTML (first 50KB)")
        print(f"  - extracted.html: What was extracted")
        print(f"  - output.md: Final markdown")
        print(f"  - info.txt: Extraction stats")

    return success


def main():
    """Run tests on specified pages."""
    if len(sys.argv) < 2:
        print("Usage: python3 test_extraction.py <slug1> [slug2] [...]")
        print("\nCommon problematic pages:")
        print("  adapter-types-evtx")
        print("  add-ons-api-integrations")
        print("  adapter-types-zendesk")
        print("  config-hive-dr-rules")
        print("  ext-cloud-cli-vultr")
        return 1

    slugs = sys.argv[1:]
    results = []

    for slug in slugs:
        success = test_page(slug)
        results.append((slug, success))

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)

    passed = sum(1 for _, s in results if s)
    total = len(results)

    for slug, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {slug}")

    print(f"\nTotal: {passed}/{total} passed")

    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
