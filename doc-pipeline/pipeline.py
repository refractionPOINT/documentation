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
