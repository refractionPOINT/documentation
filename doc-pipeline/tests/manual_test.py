#!/usr/bin/env python3
"""Manual test script for validating pipeline on small documentation subset."""
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from doc_pipeline.config import Config
from doc_pipeline.pipeline import run_pipeline


def main():
    """Run pipeline on small test subset."""
    print("MANUAL PIPELINE TEST")
    print("=" * 60)
    print("This will run the full pipeline but only process a small subset")
    print("of pages to validate the Claude-powered approach.")
    print()

    # Configure for small test
    config = Config(
        output_dir=Path("test-output"),
        state_dir=Path(".test-state"),
        # Add any test-specific config here
    )

    print("Configuration:")
    print(f"  Output: {config.output_dir}")
    print(f"  State: {config.state_dir}")
    print()

    input("Press Enter to start pipeline test...")

    try:
        success = run_pipeline(config)

        if success:
            print("\n✓ Pipeline completed successfully!")
            print("\nGenerated files:")
            for file in sorted(config.output_dir.glob("*.md")):
                print(f"  - {file.name}")

            # Show sample output
            sample_file = next(config.output_dir.glob("*.md"), None)
            if sample_file:
                print(f"\nSample output from {sample_file.name}:")
                print("-" * 60)
                print(sample_file.read_text()[:500])
                print("...")
                print("-" * 60)
        else:
            print("\n✗ Pipeline failed")
            return 1

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
