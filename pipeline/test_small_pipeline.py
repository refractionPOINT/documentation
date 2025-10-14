#!/usr/bin/env python3
"""
Quick test script to validate the pipeline works on a small subset.
Creates a fake discovery with just 2 pages and runs through the pipeline.
"""
import sys
import json
from pathlib import Path

# Add pipeline to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from utils import log, log_success, save_json, ensure_dir

# Create a minimal test dataset
TEST_PAGES = {
    "https://docs.limacharlie.io/docs/what-is-limacharlie": {
        "url": "https://docs.limacharlie.io/docs/what-is-limacharlie",
        "title": "What is LimaCharlie",
        "discovered_via": "test",
        "slug": "what-is-limacharlie"
    },
    "https://docs.limacharlie.io/docs/quickstart": {
        "url": "https://docs.limacharlie.io/docs/quickstart",
        "title": "Quickstart Guide",
        "discovered_via": "test",
        "slug": "quickstart"
    }
}


def setup_test():
    """Create test discovered_pages.json"""
    log("Setting up test with 2 pages...")
    ensure_dir(config.METADATA_DIR)
    save_json(TEST_PAGES, config.DISCOVERED_PAGES_FILE)
    log_success(f"Created test discovery: {config.DISCOVERED_PAGES_FILE}")


def run_test_pipeline():
    """Run the pipeline on test data"""
    import subprocess

    phases = [
        ("Fetch", "02_fetch.py"),
        ("Convert", "03_convert.py"),
        ("Transform", "04_transform.py"),
        ("Verify", "05_verify.py"),
    ]

    for name, script in phases:
        log(f"\n{'='*60}")
        log(f"Testing {name}")
        log('='*60)

        result = subprocess.run(
            [sys.executable, str(config.PIPELINE_DIR / script)],
            cwd=config.BASE_DIR,
            capture_output=False
        )

        if result.returncode != 0:
            log(f"✗ {name} failed")
            return False

        log_success(f"✓ {name} passed")

    return True


def main():
    log("="*60)
    log("PIPELINE TEST - Small Subset")
    log("="*60)

    # Setup test data
    setup_test()

    # Run pipeline
    success = run_test_pipeline()

    if success:
        log_success("\n✓ All pipeline phases work correctly!")
        log("\nTest outputs:")
        log(f"  - HTML files:    {config.RAW_HTML_DIR}")
        log(f"  - Raw MD:        {config.RAW_MARKDOWN_DIR}")
        log(f"  - Cleaned MD:    {config.CLEANED_MARKDOWN_DIR}")
        log(f"  - INDEX.md:      {config.INDEX_FILE}")
        log(f"  - COMBINED.md:   {config.COMBINED_FILE}")
        return 0
    else:
        log("✗ Pipeline test failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
