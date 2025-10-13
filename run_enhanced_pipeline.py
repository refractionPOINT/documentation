#!/usr/bin/env python3
"""
Enhanced documentation pipeline with:
- Claude-powered semantic categorization
- Content quality filtering (removes stubs)
- LLM-optimized output (strips human UI metadata)
"""
import sys
import json
from pathlib import Path
from dataclasses import asdict

sys.path.insert(0, 'doc-pipeline')

from models import DocumentStructure, Page
from config import Config
from lib.convert import convert_all_pages
from lib.analyze import analyze_all_pages
from lib.verify import verify_all_pages
from lib.claude_client import ClaudeClient
from lib import fetch, quality


def main():
    """Run enhanced pipeline with all improvements."""

    config = Config()

    # Check if Claude is available for categorization
    print("="*60)
    print("ENHANCED DOCUMENTATION PIPELINE")
    print("="*60)
    print("\nInitializing Claude client for smart categorization...")

    try:
        claude_client = ClaudeClient()
        claude_client.check_required()
        use_claude = True
        print("✓ Claude CLI available")
    except Exception as e:
        print(f"⚠ Claude CLI not available: {e}")
        print("  Falling back to rule-based categorization")
        claude_client = None
        use_claude = False

    # Phase 1: Fetch with smart categorization
    fetch_state = Path('.doc-pipeline-state/01-fetch.json')

    if fetch_state.exists():
        print("\n[FETCH] Loading cached pages...")
        with open(fetch_state) as f:
            state = json.load(f)

        # Convert to structure
        categories = {}
        for cat_name, pages_data in state['categories'].items():
            categories[cat_name] = [
                Page(
                    url=p['url'],
                    slug=p['slug'],
                    title=p['title'],
                    category=p['category'],
                    raw_html=p['raw_html']
                )
                for p in pages_data
            ]
        structure = DocumentStructure(categories=categories)
        total_pages = sum(len(pages) for pages in structure.categories.values())
        print(f"✓ Loaded {total_pages} cached pages")

    else:
        print("\n[FETCH] Discovering and downloading pages...")
        structure = fetch.discover_documentation_structure(
            config,
            claude_client=claude_client if use_claude else None
        )

        if not structure.categories:
            print("✗ Failed to discover documentation")
            return 1

        total_pages = sum(len(pages) for pages in structure.categories.values())
        print(f"Discovered {total_pages} pages in {len(structure.categories)} categories")

        # Download pages
        downloaded = fetch.download_all_pages(structure, config)
        if downloaded == 0:
            print("✗ Failed to download pages")
            return 1
        print(f"✓ Downloaded {downloaded} pages")

        # Save fetch state
        fetch_state.parent.mkdir(parents=True, exist_ok=True)
        with open(fetch_state, 'w') as f:
            json.dump(structure.to_dict(), f, indent=2)
        print(f"✓ Saved to {fetch_state}")

    # Phase 2: Convert HTML → Markdown
    print("\n[CONVERT] Converting HTML → Markdown (LLM-optimized)...")
    converted = convert_all_pages(structure, config)
    print(f"✓ Converted {converted}/{total_pages} pages")

    # Save conversion state
    convert_state = Path('.doc-pipeline-state/02-convert.json')
    with open(convert_state, 'w') as f:
        json.dump(structure.to_dict(), f, indent=2)
    print(f"✓ Saved to {convert_state}")

    # Phase 3: Quality filtering
    print("\n[QUALITY] Filtering low-quality stub pages...")

    # Flatten pages
    all_pages = []
    for pages_list in structure.categories.values():
        all_pages.extend(pages_list)

    # Apply quality pipeline
    quality_pages, quality_report = quality.apply_quality_pipeline(
        all_pages,
        remove_low_quality=True
    )

    print(f"✓ Kept {len(quality_pages)}/{len(all_pages)} quality pages")
    print(f"  Removed {len(all_pages) - len(quality_pages)} stub/low-quality pages")

    if quality_report['removed']:
        removed_file = Path('.doc-pipeline-state/removed_pages.txt')
        with open(removed_file, 'w') as f:
            f.write("REMOVED LOW-QUALITY PAGES\n")
            f.write("="*60 + "\n\n")
            for item in quality_report['removed']:
                f.write(f"{item}\n")
        print(f"  See {removed_file} for details")

    # Re-categorize quality pages with Claude
    print("\n[CATEGORIZE] Re-categorizing quality pages...")
    if use_claude and len(quality_pages) > 0:
        try:
            from lib import categorize
            categorization = categorize.categorize_pages_with_claude(
                quality_pages,
                claude_client
            )
            filtered_categories = categorize.apply_categorization(
                quality_pages,
                categorization
            )
            print(f"✓ Categorized into {len(filtered_categories)} semantic categories")
        except Exception as e:
            print(f"Warning: Claude categorization failed: {e}")
            print("Using fallback categorization...")
            # Fallback: use old categories
            filtered_categories = {}
            for page in quality_pages:
                cat = page.category or 'other'
                if cat not in filtered_categories:
                    filtered_categories[cat] = []
                filtered_categories[cat].append(page)
    else:
        # No Claude, organize by existing categories
        filtered_categories = {}
        for page in quality_pages:
            cat = page.category or 'other'
            if cat not in filtered_categories:
                filtered_categories[cat] = []
            filtered_categories[cat].append(page)

    structure.categories = filtered_categories

    # Save quality state
    quality_state = Path('.doc-pipeline-state/03-quality.json')
    with open(quality_state, 'w') as f:
        json.dump(structure.to_dict(), f, indent=2)
    print(f"✓ Saved to {quality_state}")

    # Phase 4: Analysis (extract metadata)
    print("\n[ANALYZE] Extracting metadata...")
    analyzed = analyze_all_pages(structure, config)
    print(f"✓ Analyzed {analyzed} pages")

    # Save analysis state
    analyze_state = Path('.doc-pipeline-state/04-analyze.json')
    with open(analyze_state, 'w') as f:
        json.dump(structure.to_dict(), f, indent=2)
    print(f"✓ Saved to {analyze_state}")

    # Phase 5: Verification
    print("\n[VERIFY] Running quality checks...")
    report = verify_all_pages(structure, config)

    # Save verification report
    verify_report = Path('.doc-pipeline-state/05-verification_report.json')
    with open(verify_report, 'w') as f:
        json.dump(asdict(report), f, indent=2)
    print(f"✓ Saved report to {verify_report}")

    # Print summary
    print("\n" + "="*60)
    print("PIPELINE SUMMARY")
    print("="*60)
    print(f"\nCategorization:")
    if use_claude:
        print("  Method: Claude semantic categorization")
    else:
        print("  Method: Rule-based with priority patterns")
    print(f"  Categories: {len(structure.categories)}")
    for cat, pages_list in sorted(structure.categories.items()):
        print(f"    - {cat}: {len(pages_list)} pages")

    print(f"\nQuality:")
    print(f"  Original pages: {total_pages}")
    print(f"  After filtering: {len(quality_pages)}")
    print(f"  Removed: {total_pages - len(quality_pages)} ({(total_pages - len(quality_pages))/total_pages*100:.1f}%)")

    print(f"\nVerification:")
    print(f"  Passed: {report.passed} ({report.passed/len(quality_pages)*100:.1f}%)")
    print(f"  Warnings: {report.warnings}")
    print(f"  Critical: {report.critical}")

    # Phase 6: Output
    print("\n[OUTPUT] Saving markdown files...")
    output_dir = Path('limacharlie-docs-enhanced')

    # Clear old output
    if output_dir.exists():
        import shutil
        shutil.rmtree(output_dir)

    saved = 0
    for category, pages_list in structure.categories.items():
        # Use category subdirectory if category is not empty
        if category and category.strip():
            category_dir = output_dir / category
        else:
            category_dir = output_dir / 'uncategorized'

        category_dir.mkdir(parents=True, exist_ok=True)

        for page in pages_list:
            if page.markdown:
                # Save markdown
                md_file = category_dir / f"{page.slug}.md"
                md_file.write_text(page.markdown, encoding='utf-8')

                # Save metadata
                json_file = category_dir / f"{page.slug}.json"
                metadata = {
                    'url': page.url,
                    'title': page.title,
                    'slug': page.slug,
                    'category': page.category,
                    'metadata': page.metadata,
                    'api_elements': page.api_elements,
                    'content_hash': page.content_hash
                }
                json_file.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
                saved += 1

    print(f"✓ Saved {saved} markdown files to {output_dir}")

    # Create combined documentation
    print("\n[OUTPUT] Creating combined documentation...")
    combined_file = output_dir / "COMBINED.md"
    with open(combined_file, 'w') as f:
        f.write("# LimaCharlie Documentation (LLM-Optimized)\n\n")
        f.write("This documentation has been optimized for AI/LLM consumption:\n")
        f.write("- Semantic categorization\n")
        f.write("- High-quality content only (stubs removed)\n")
        f.write("- No human UI metadata\n")
        f.write("- Clean markdown formatting\n\n")
        f.write("---\n\n")

        for category, pages_list in sorted(structure.categories.items()):
            f.write(f"# {category.replace('-', ' ').title()}\n\n")

            for page in sorted(pages_list, key=lambda p: p.title):
                if page.markdown:
                    f.write(f"## {page.title}\n\n")
                    f.write(f"**Source:** {page.url}\n\n")
                    f.write(page.markdown)
                    f.write("\n\n---\n\n")

    print(f"✓ Created {combined_file}")

    print("\n" + "="*60)
    print("✅ ENHANCED PIPELINE COMPLETE")
    print("="*60)
    print(f"\nOutput: {output_dir}/")
    print(f"Quality improvement: {total_pages} → {len(quality_pages)} pages")
    print(f"\nCategories created:")
    for cat in sorted(structure.categories.keys()):
        count = len(structure.categories[cat])
        print(f"  - {cat or 'uncategorized'}: {count} pages")

    return 0


if __name__ == '__main__':
    sys.exit(main())
