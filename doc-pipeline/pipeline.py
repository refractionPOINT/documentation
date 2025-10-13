"""Main pipeline orchestration."""
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import List

# Handle both package and standalone imports
try:
    from .config import Config
    from .models import DocumentStructure, Page
    from .lib import fetch
    from .lib.claude_client import ClaudeClient
    from .lib.batch import create_semantic_batches
    from .lib.understand import process_batches_parallel, ProcessedPage
    from .lib.synthesize import build_api_index, resolve_cross_references
except ImportError:
    # Fallback for direct execution or testing
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from config import Config
    from models import DocumentStructure, Page
    from lib import fetch
    from lib.claude_client import ClaudeClient
    from lib.batch import create_semantic_batches
    from lib.understand import process_batches_parallel, ProcessedPage
    from lib.synthesize import build_api_index, resolve_cross_references


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


def run_pipeline(config: Config = None) -> bool:
    """
    Run the complete documentation pipeline.

    Phases:
    1. FETCH - Download pages
    2. BATCH_GROUP - Create semantic batches
    3. PARALLEL_UNDERSTAND - Process batches with Claude
    4. SYNTHESIZE - Build indexes and resolve references
    5. ENHANCE - Global optimizations (future)
    6. VERIFY - Semantic validation (future)
    7. DETECT - Git change tracking

    Args:
        config: Pipeline configuration

    Returns:
        True if successful, False otherwise
    """
    if config is None:
        config = Config()

    print("=" * 60)
    print("LIMACHARLIE DOCUMENTATION PIPELINE")
    print("=" * 60)

    # Initialize Claude client
    claude_client = ClaudeClient()
    claude_client.check_required()

    # Phase 1: FETCH
    print("\n[FETCH] Discovering and downloading pages...")
    structure = fetch.discover_documentation_structure(config)

    if not structure.categories:
        print("✗ Failed to discover documentation structure")
        return False

    total_pages = sum(len(pages) for pages in structure.categories.values())
    print(f"Discovered {total_pages} pages in {len(structure.categories)} categories")

    downloaded = fetch.download_all_pages(structure, config)
    if downloaded == 0:
        print("✗ Failed to download any pages")
        return False

    print(f"✓ Fetched {downloaded} pages")

    # Flatten pages from structure
    pages: List[Page] = []
    for category_pages in structure.categories.values():
        pages.extend(category_pages)

    # Phase 2: BATCH_GROUP
    print("\n[BATCH_GROUP] Creating semantic batches...")
    batches = create_semantic_batches(pages, claude_client)
    print(f"✓ Created {len(batches)} batches")

    # Phase 3: PARALLEL_UNDERSTAND
    print("\n[PARALLEL_UNDERSTAND] Processing batches with Claude...")
    processed_batches = asyncio.run(
        process_batches_parallel(batches, claude_client)
    )

    # Flatten to page list
    all_processed: List[ProcessedPage] = []
    for batch_pages in processed_batches.values():
        all_processed.extend(batch_pages)
    print(f"✓ Processed {len(all_processed)} pages")

    # Phase 4: SYNTHESIZE
    print("\n[SYNTHESIZE] Building indexes and resolving references...")
    api_index = build_api_index(all_processed, claude_client)
    resolved_pages = resolve_cross_references(all_processed)
    print(f"✓ Built API index and resolved cross-references")

    # Write output files
    print("\n[OUTPUT] Writing documentation files...")
    config.output_dir.mkdir(parents=True, exist_ok=True)

    for page in resolved_pages:
        output_file = config.output_dir / f"{page.slug}.md"
        output_file.write_text(page.enhanced_markdown)

    # Write API index
    (config.output_dir / "API_INDEX.md").write_text(api_index)

    # Write metadata index
    metadata_index = {
        page.slug: page.metadata
        for page in resolved_pages
    }
    (config.output_dir / "METADATA_INDEX.json").write_text(
        json.dumps(metadata_index, indent=2)
    )

    print(f"✓ Wrote {len(resolved_pages)} markdown files")

    # Phase 7: DETECT (if git enabled)
    if config.git_commit_changes:
        print("\n[DETECT] Detecting changes...")
        try:
            from .lib import detect
        except ImportError:
            from lib import detect
        detect.detect_and_report(config.output_dir, config)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)

    return True
