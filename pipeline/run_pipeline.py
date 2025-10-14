#!/usr/bin/env python3
"""
Main pipeline runner for LimaCharlie documentation transformation.

Orchestrates all phases of the pipeline:
1. Discovery - Find all documentation pages
2. Fetch - Download HTML
3. Convert - HTML to raw Markdown
4. Transform - Claude-powered cleaning
5. Verify - Completeness check and final outputs
6. Synthesize - Reorganize into self-contained topics
"""
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

import config
from utils import log, log_error, log_success, log_warning


class PipelineRunner:
    """Orchestrates the complete documentation transformation pipeline."""

    def __init__(self, start_phase: int = 1, end_phase: int = 7):
        self.start_phase = start_phase
        self.end_phase = end_phase
        self.phases = [
            ("Discovery", "01_discover.py"),
            ("Fetch HTML", "02_fetch.py"),
            ("Convert to Markdown", "03_convert.py"),
            ("Transform with Claude", "04_transform.py"),
            ("Verify & Generate Outputs", "05_verify.py"),
            ("Topic Synthesis", "06_synthesize.py"),
            ("Validation & Quality Checks", "07_validate.py"),
        ]
        self.start_time = None
        self.phase_times = []

    def run_phase(self, phase_num: int, description: str, script: str) -> bool:
        """
        Run a single phase of the pipeline.

        Args:
            phase_num: Phase number (1-6)
            description: Human-readable description
            script: Script filename to run

        Returns:
            True if successful, False otherwise
        """
        log("\n" + "="*60)
        log(f"PHASE {phase_num}: {description}")
        log("="*60)

        script_path = config.PIPELINE_DIR / script

        if not script_path.exists():
            log_error(f"Script not found: {script_path}")
            return False

        phase_start = datetime.now()

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                check=True,
                cwd=config.BASE_DIR
            )

            phase_duration = (datetime.now() - phase_start).total_seconds()
            self.phase_times.append((description, phase_duration))

            log_success(f"Phase {phase_num} completed in {phase_duration:.1f}s")
            return True

        except subprocess.CalledProcessError as e:
            log_error(f"Phase {phase_num} failed with exit code {e.returncode}")
            return False
        except Exception as e:
            log_error(f"Phase {phase_num} failed: {e}")
            return False

    def run_all(self) -> bool:
        """
        Run all phases of the pipeline.

        Returns:
            True if all phases succeeded, False otherwise
        """
        self.start_time = datetime.now()

        log("="*60)
        log("LIMACHARLIE DOCUMENTATION TRANSFORMATION PIPELINE")
        log("="*60)
        log(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        log(f"Running phases {self.start_phase} to {self.end_phase}")
        log("")

        # Run each phase
        for i, (description, script) in enumerate(self.phases, start=1):
            if i < self.start_phase:
                log(f"Skipping Phase {i}: {description}")
                continue
            if i > self.end_phase:
                break

            success = self.run_phase(i, description, script)

            if not success:
                log_error(f"\nPipeline failed at Phase {i}: {description}")
                return False

        # Print summary
        total_duration = (datetime.now() - self.start_time).total_seconds()

        log("\n" + "="*60)
        log("PIPELINE COMPLETE")
        log("="*60)
        log(f"Total duration: {total_duration:.1f}s ({total_duration/60:.1f} minutes)")
        log("\nPhase timings:")
        for description, duration in self.phase_times:
            log(f"  {description:30s} {duration:6.1f}s")
        log("="*60)

        log_success("\n✓ Documentation transformation complete!")
        log(f"\nOutput files:")
        log(f"  - Index:    {config.INDEX_FILE}")
        log(f"  - Combined: {config.COMBINED_FILE}")
        log(f"  - Cleaned:  {config.CLEANED_MARKDOWN_DIR}/")
        log(f"  - Topics:   {config.TOPICS_DIR}/")
        log(f"  - Report:   {config.VERIFICATION_REPORT_FILE}")

        return True


def main():
    """Main entry point with CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Transform LimaCharlie documentation to LLM-friendly markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline
  python3 run_pipeline.py

  # Run only discovery and fetch
  python3 run_pipeline.py --start 1 --end 2

  # Resume from conversion phase
  python3 run_pipeline.py --start 3

  # Run only transformation (assumes previous phases completed)
  python3 run_pipeline.py --start 4 --end 4
        """
    )

    parser.add_argument(
        '--start',
        type=int,
        default=1,
        choices=range(1, 8),
        help='Start from phase (1=discover, 2=fetch, 3=convert, 4=transform, 5=verify, 6=synthesize, 7=validate)'
    )

    parser.add_argument(
        '--end',
        type=int,
        default=7,
        choices=range(1, 8),
        help='End at phase (1=discover, 2=fetch, 3=convert, 4=transform, 5=verify, 6=synthesize, 7=validate)'
    )

    args = parser.parse_args()

    if args.start > args.end:
        log_error("Start phase must be <= end phase")
        return 1

    # Run the pipeline
    runner = PipelineRunner(start_phase=args.start, end_phase=args.end)
    success = runner.run_all()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
