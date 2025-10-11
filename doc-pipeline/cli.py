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
