#!/usr/bin/env python3
"""
Phase 4: Transform raw markdown to clean, LLM-optimized markdown using Claude.

This is the key innovation: instead of brittle regex cleaning, we use Claude sub-agents
to intelligently extract documentation content and remove UI chrome.
"""
import subprocess
import sys
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import config
from utils import (
    log, log_error, log_success, log_warning,
    ensure_dir, ProgressTracker, save_json
)


class ClaudeTransformer:
    """Uses Claude CLI to clean documentation pages in parallel."""

    def __init__(self):
        self.successful = 0
        self.failed = 0
        self.processing_log = []

        # Load the cleaning prompt
        prompt_file = config.PIPELINE_DIR / "prompts" / "clean_page.md"
        if not prompt_file.exists():
            log_error(f"Prompt template not found: {prompt_file}")
            sys.exit(1)

        with open(prompt_file, 'r', encoding='utf-8') as f:
            self.cleaning_prompt = f.read()

        # Check if Claude CLI is available
        try:
            result = subprocess.run(
                [config.CLAUDE_CLI, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            log(f"Using Claude CLI: {result.stdout.strip()}")
        except Exception as e:
            log_error(f"Claude CLI not found or not working: {e}")
            log_error(f"Make sure '{config.CLAUDE_CLI}' is in your PATH")
            sys.exit(1)

    def transform_page(self, md_path: Path) -> bool:
        """
        Transform a single raw markdown page to clean markdown using Claude.

        Args:
            md_path: Path to raw markdown file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Read raw markdown
            with open(md_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()

            # Check if file is too small (likely failed conversion)
            if len(raw_content.strip()) < 100:
                log_warning(f"Skipping {md_path.name} (too small, likely empty)")
                return False

            # Prepare output path
            output_path = config.CLEANED_MARKDOWN_DIR / md_path.name

            # Skip if already processed
            if output_path.exists():
                log(f"Skipping (already exists): {md_path.name}")
                return True

            # Create full prompt with the raw markdown
            full_prompt = f"{self.cleaning_prompt}\n\n---\n\n{raw_content}"

            # Save full prompt to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp:
                tmp.write(full_prompt)
                tmp_path = tmp.name

            try:
                # Call Claude CLI to process the page
                # Pass the combined prompt via stdin
                result = subprocess.run(
                    [config.CLAUDE_CLI],
                    input=full_prompt,
                    capture_output=True,
                    text=True,
                    timeout=120,  # 2 minutes per page
                    encoding='utf-8'
                )

                if result.returncode != 0:
                    log_error(f"Claude failed for {md_path.name}: {result.stderr}")
                    return False

                cleaned_content = result.stdout.strip()

                # Validate output
                if len(cleaned_content) < 50:
                    log_error(f"Claude output too short for {md_path.name}")
                    return False

                # Save cleaned markdown
                ensure_dir(config.CLEANED_MARKDOWN_DIR)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)

                log(f"Transformed: {md_path.name} ({len(raw_content)} → {len(cleaned_content)} bytes)")

                # Record processing info
                self.processing_log.append({
                    "file": md_path.name,
                    "raw_size": len(raw_content),
                    "cleaned_size": len(cleaned_content),
                    "reduction": f"{(1 - len(cleaned_content)/len(raw_content))*100:.1f}%"
                })

                return True

            finally:
                # Clean up temp file
                Path(tmp_path).unlink(missing_ok=True)

        except subprocess.TimeoutExpired:
            log_error(f"Timeout transforming {md_path.name}")
            return False
        except Exception as e:
            log_error(f"Error transforming {md_path.name}: {e}")
            return False

    def transform_all(self, md_files: list, max_workers: int = None) -> dict:
        """
        Transform all markdown files using parallel Claude instances.

        Args:
            md_files: List of raw markdown file paths
            max_workers: Number of parallel workers (Claude instances)

        Returns:
            Dictionary with transformation statistics
        """
        if max_workers is None:
            # For Claude API calls, be conservative with parallelism
            max_workers = min(config.MAX_PARALLEL_WORKERS, 5)

        log(f"Transforming {len(md_files)} pages with {max_workers} parallel Claude instances...")
        log("This will take a while as each page is processed by Claude...")

        ensure_dir(config.CLEANED_MARKDOWN_DIR)
        progress = ProgressTracker(len(md_files), "Transforming with Claude")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all transformation jobs
            future_to_file = {
                executor.submit(self.transform_page, md_path): md_path
                for md_path in md_files
            }

            # Process completed jobs
            for future in as_completed(future_to_file):
                md_path = future_to_file[future]
                try:
                    success = future.result()
                    if success:
                        self.successful += 1
                    else:
                        self.failed += 1
                except Exception as e:
                    log_error(f"Exception transforming {md_path}: {e}")
                    self.failed += 1

                progress.update()

        progress.complete()

        return {
            "successful": self.successful,
            "failed": self.failed,
            "total": len(md_files),
            "processing_log": self.processing_log
        }


def main():
    """Main entry point."""

    # Find all raw markdown files
    if not config.RAW_MARKDOWN_DIR.exists():
        log_error(f"Raw markdown directory not found: {config.RAW_MARKDOWN_DIR}")
        log_error("Please run 03_convert.py first")
        sys.exit(1)

    md_files = list(config.RAW_MARKDOWN_DIR.glob("*.md"))

    if not md_files:
        log_error(f"No markdown files found in {config.RAW_MARKDOWN_DIR}")
        sys.exit(1)

    log(f"Found {len(md_files)} markdown files to transform")

    # Transform all files
    transformer = ClaudeTransformer()
    results = transformer.transform_all(md_files)

    # Save processing log
    log_file = config.METADATA_DIR / "transformation_log.json"
    save_json(results, log_file)

    # Report results
    log_success(f"Transformation complete: {results['successful']} successful, {results['failed']} failed")

    if results['failed'] > 0:
        log_warning(f"{results['failed']} pages failed to transform")

    if results['successful'] == 0:
        log_error("No pages were successfully transformed")
        sys.exit(1)

    # Count cleaned files
    cleaned_files = list(config.CLEANED_MARKDOWN_DIR.glob("*.md"))
    log_success(f"Total cleaned markdown files: {len(cleaned_files)}")

    # Show some statistics
    if results['processing_log']:
        avg_reduction = sum(
            float(entry['reduction'].rstrip('%'))
            for entry in results['processing_log']
        ) / len(results['processing_log'])
        log(f"Average content reduction: {avg_reduction:.1f}%")

    return 0


if __name__ == "__main__":
    sys.exit(main())
