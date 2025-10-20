#!/usr/bin/env python3
"""
Script to clean up raw markdown documentation files using Claude Code.

This script:
1. Finds all markdown files in ./limacharlie/raw_markdown/
2. Launches a headless Claude Code instance
3. Instructs Claude to spawn parallel sub-agents to clean each file
4. Each sub-agent either:
   - Cleans the markdown file (removes navigation, headers/footers, etc.)
   - Deletes the file with rm if it only contains navigation/links

Dependencies:
- claude (Claude Code CLI must be installed)
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path

# Configuration
RAW_MARKDOWN_DIR = "./limacharlie/raw_markdown"
CLAUDE_BINARY = "claude"

# Prompt template for Claude to process all files
CLEANING_PROMPT_TEMPLATE = """You are tasked with cleaning up raw markdown documentation files.

TASK: Process ALL markdown files in the current directory (and subdirectories) using parallel sub-agents. Do NOT ask for confirmation - proceed immediately.

STEP 1: Use the Glob tool with pattern "**/*.md" to find all markdown files recursively (excluding __pycache__).
IMMEDIATELY after finding files, output: "Found X markdown files. Starting batch processing..."

STEP 2: For EACH .md file found, dispatch a Task agent with subagent_type='general-purpose'. Dispatch agents IN PARALLEL using a single message with multiple Task tool calls. Process files in batches of 10-20 at a time for efficiency.

BEFORE dispatching each batch, output: "Dispatching batch N (files X-Y)..."
AFTER each batch completes, output: "Batch N complete. Processed X files."

STEP 3: Each sub-agent must:
1. Read the markdown file
2. Analyze the content to determine if it's worth keeping
3. Take one of two actions:

**Action A: Clean and Replace** (for files with actual documentation content)
- Remove all navigation elements, UI elements, and metadata cruft
- Specifically remove:
  * The YAML frontmatter (the --- delimited section at the top with title, slug, breadcrumb, source, articleId, etc.)
  * "Share this", "Print", "Dark", "Light" toggles
  * Duplicate titles and headers
  * "Contents" sections
  * "Article summary" and feedback widgets ("Did you find this summary helpful?")
  * "Was this article helpful?" feedback forms
  * Comment forms and email signup forms
  * "Related articles", "What's Next", "Tags", "Table of contents" sections at the end
  * Any "Updated on" timestamps that are in the body
  * Horizontal rules (---/***) that are just decorative
- KEEP:
  * The actual documentation content (paragraphs, lists, code blocks)
  * Legitimate section headings (##, ###, etc.)
  * **ALL markdown link syntax EXACTLY as-is** - this is CRITICAL:
    - Preserve absolute external URLs: `[text](https://docs.limacharlie.io/...)`
    - Preserve Document360 relative paths: `[text](/v2/docs/...)` or `[text](/docs/...)`
    - Preserve local relative paths: `[text](../../other-file.md)`
    - Even if links appear broken or point to non-existent paths, YOU MUST PRESERVE THEM
    - Link conversion and fixing happens in STEP 4 - STEP 3 must preserve ALL link syntax AS-IS
    - Do NOT strip link syntax, do NOT convert links to plain text, do NOT remove "broken" links
  * Code examples and technical content
- Use the Write tool to completely replace the file with the cleaned content
  * Write is designed for complete file replacement and handles large files reliably
  * After cleaning the content, call Write with the same file path you just Read and the cleaned markdown as the content
  * This ensures even very large files (20KB+) are properly cleaned

**Action B: Delete** (for files that are just navigation/category pages)
- If a file contains ONLY navigation links, category listings, and UI elements with NO actual documentation content
- Use the Bash tool to run rm with THE ACTUAL FILE PATH you are currently processing
- For example, if you are processing "Add-Ons/developer-grant-program.md", run: rm "Add-Ons/developer-grant-program.md"
- DO NOT use placeholder text - use the real file path from the file you just read

**STEP 4: Link Processing** (for files being cleaned, not deleted)
After cleaning the content, process all links in the file:

**A. Unescape cdn.document360.io URLs:**
- Find any URLs containing `cdn.document360.io`
- If they contain backslash escape sequences (like `\\(`, `\\)`, or other `\\X` patterns), unescape them
- Example: `cdn.document360.io/file\\(1\\).png` should become `cdn.document360.io/file(1).png`
- Replace `\\(` with `(`, `\\)` with `)`, etc.

**B. Convert External LimaCharlie Documentation Links to Local Relative Links:**

For links pointing to `doc.limacharlie.io` or `docs.limacharlie.io`:

1. **Special Case - API Documentation Links:**
   - If the link points to `docs.limacharlie.io/apidocs/*`, replace the entire URL with `https://api.limacharlie.io/static/swagger/`
   - Example: `https://docs.limacharlie.io/apidocs/get-org-urls` → `https://api.limacharlie.io/static/swagger/`

2. **Regular Documentation Links - Convert to Local Relative Links:**
   - Detect both markdown links `[text](https://doc.limacharlie.io/...)` and bare URLs
   - Handle both `doc.limacharlie.io` and `docs.limacharlie.io` domains

   **Finding the Target File:**
   - IMPORTANT: All directory and file names use underscores (_) instead of spaces. When matching URLs to files, replace spaces with underscores.
   - First, use Glob with pattern `**/*.md` to get a list of all markdown files in the directory tree
   - Extract the slug/path from the URL (e.g., from `https://docs.limacharlie.io/docs/adapter-types-aws-cloudtrail`, extract `adapter-types-aws-cloudtrail`)
   - Try fuzzy filename matching: look for .md files whose names closely match the URL slug (remember: spaces in URLs may be underscores in filenames)
   - If multiple candidates exist, use your judgment to pick the most relevant one (consider directory structure, topic, etc.)
   - If filename matching doesn't work, use the Grep tool to search for content that matches the topic
   - If still uncertain, Read a few candidate files to verify which one is the correct target
   - Be thorough and persistent - the correct file almost certainly exists

   **Verifying the Target File Exists:**
   - BEFORE creating a relative link, you MUST verify the target file actually exists
   - Use the Read tool to attempt reading the first few lines of the target file
   - If the Read succeeds, the file exists and you can proceed to create the relative link
   - If the Read fails or the file doesn't exist, continue searching for alternative files
   - IMPORTANT: If after exhaustive searching you cannot find any existing file that matches, keep the original external URL unchanged - do NOT create a broken relative link to a non-existent file

   **Creating the Relative Link:**
   - Only proceed with this step if you have verified the target file exists (see above)
   - Calculate the relative path from the current file being processed to the verified target file
   - Remember: directory and file names use underscores instead of spaces
   - Example: if current file is `Outputs/Destinations/webhook.md` and target is `Platform_Management/outputs.md`, the relative path would be `../../Platform_Management/outputs.md`
   - Preserve any URL fragment/anchor (e.g., `#webhook-details`) in the converted link
   - Replace the external URL with the relative markdown link
   - Example: `[See details](https://doc.limacharlie.io/docs/outputs#webhook-details)` → `[See details](../../Platform_Management/outputs.md#webhook-details)`
   - Bare URLs should also be converted to markdown links with appropriate link text

**C. Convert Document360 Relative Links to Local Relative Links:**

Document360 relative links are paths like `[text](/v2/docs/...)` or `[text](/docs/...)` that were part of the original documentation platform.

1. **Detect Document360 Relative Links:**
   - Look for markdown links matching patterns: `[text](/v2/docs/...)` or `[text](/docs/...)`
   - These are NOT absolute URLs but relative paths from the Document360 platform
   - Extract the slug from the path (e.g., from `/v2/docs/template-strings-and-transforms`, extract `template-strings-and-transforms`)
   - Also extract the link text (e.g., "Transform") as it may provide context about the target

2. **Multi-Stage Iterative Search to Find Target File:**
   Use these strategies IN ORDER until a match is found:

   **Stage 1 - Direct Filename Matching:**
   - Use Glob with pattern `**/*{slug}*.md` to find files whose names contain the slug
   - Try variations: exact match, with underscores, with hyphens
   - Example: for slug `template-strings-and-transforms`, try `**/template-strings-and-transforms.md`, `**/template_strings_and_transforms.md`, etc.

   **Stage 2 - Content-Based Search Using Link Text:**
   - Use Grep to search for the link text (e.g., "Transform") in markdown files
   - Combine with keywords from the slug (e.g., "template", "strings", "transforms")
   - Look for title matches in the `# Header` or `title:` frontmatter

   **Stage 3 - Access Original Document360 Page for Context:**
   - Reconstruct the full Document360 URL: `https://docs.limacharlie.io` + the relative path
   - Example: `/v2/docs/template-strings-and-transforms` → `https://docs.limacharlie.io/v2/docs/template-strings-and-transforms`
   - Use WebFetch to access the page and extract its title, topic, or key content
   - Use that context to Grep for matching content in local markdown files

   **Stage 4 - Read Candidate Files to Verify Topic:**
   - If multiple candidates found, Read the first 50-100 lines of each
   - Compare content/topic with the link text and context from Document360
   - Select the best match based on topic relevance

   **Stage 5 - Fuzzy Directory Structure Matching:**
   - Consider the directory structure in the URL path if present
   - Example: `/docs/sensors/adapter-usage` likely maps to something in a `Sensors/` or `Adapters/` directory

3. **Verify Target File Exists:**
   - Before creating a relative link, MUST verify the target file exists
   - Use Read tool to read first few lines of the target file
   - If Read succeeds, proceed to create the relative link
   - If Read fails, continue searching or use fallback

4. **Create Relative Link:**
   - Calculate the relative path from current file to verified target file
   - Preserve any URL fragment/anchor (e.g., `#section-name`)
   - Convert the link: `[Transform](/v2/docs/template-strings-and-transforms)` → `[Transform](../../Events/template-strings-and-transforms.md)`

5. **Fallback - Keep Original Link and Log:**
   - If after exhaustive search (all 5 stages) no match is found, keep the original link UNCHANGED
   - Output a clear log message: "LINK_SKIPPED: Could not find local match for [link text](original path) in file: {current_file_path}"
   - Do NOT create broken relative links to non-existent files
   - Do NOT strip the link entirely - preservation is better than deletion

IMPORTANT:
- Be thorough but decisive - if in doubt whether to keep content, keep it.
- OUTPUT FREQUENT STATUS UPDATES - before and after each batch
- Print progress messages BEFORE using tools, not just after
- Use simple text output (not just tool results) so the user sees activity
- If you encounter any errors when cleaning a file, output a clear error message with the file path so it can be tracked

START NOW - find all .md files and dispatch the parallel cleaning agents immediately."""


class MarkdownCleaner:
    """Manages the Claude Code-based markdown cleaning process"""

    def __init__(self, raw_markdown_dir):
        self.raw_markdown_dir = Path(raw_markdown_dir).resolve()
        self.initial_file_mtimes = {}
        self.processed_count = 0
        self.monitoring = False

        if not self.raw_markdown_dir.exists():
            raise ValueError(f"Directory does not exist: {self.raw_markdown_dir}")

        if not self.raw_markdown_dir.is_dir():
            raise ValueError(f"Not a directory: {self.raw_markdown_dir}")

    def count_markdown_files(self):
        """Count total markdown files to be processed"""
        md_files = list(self.raw_markdown_dir.rglob("*.md"))
        return len(md_files)

    def capture_initial_state(self):
        """Capture modification times of all markdown files"""
        for md_file in self.raw_markdown_dir.rglob("*.md"):
            try:
                self.initial_file_mtimes[md_file] = md_file.stat().st_mtime
            except OSError:
                pass

    def monitor_progress(self):
        """Monitor file changes and report progress"""
        print(f"[{time.strftime('%H:%M:%S')}] Monitoring file changes...")
        sys.stdout.flush()

        last_count = 0
        no_change_count = 0

        while self.monitoring:
            time.sleep(2)  # Check every 2 seconds

            current_count = 0
            modified_files = []

            # Check for modifications
            for md_file in self.raw_markdown_dir.rglob("*.md"):
                try:
                    current_mtime = md_file.stat().st_mtime
                    initial_mtime = self.initial_file_mtimes.get(md_file, 0)

                    if current_mtime > initial_mtime:
                        current_count += 1
                        if len(modified_files) < 3:  # Keep track of recent changes
                            modified_files.append(md_file.name)
                except OSError:
                    # File might have been deleted
                    if md_file in self.initial_file_mtimes:
                        current_count += 1

            # Report progress if count changed
            if current_count != last_count:
                self.processed_count = current_count
                recent = f" (recent: {', '.join(modified_files)})" if modified_files else ""
                print(f"[{time.strftime('%H:%M:%S')}] Progress: {current_count} files processed{recent}")
                sys.stdout.flush()
                last_count = current_count
                no_change_count = 0
            else:
                no_change_count += 1
                # Show heartbeat every 15 seconds if no changes
                if no_change_count >= 7:  # 7 * 2 seconds = ~14 seconds
                    print(f"[{time.strftime('%H:%M:%S')}] Still working... ({current_count} files processed so far)")
                    sys.stdout.flush()
                    no_change_count = 0

    def run_claude_headless(self):
        """Run Claude Code in headless mode to clean markdown files"""
        print(f"Running Claude Code in: {self.raw_markdown_dir}")
        print("This will take a while as Claude processes all files...")
        print("-" * 80)
        print()
        sys.stdout.flush()

        # Capture initial state
        print("Capturing initial file states...")
        self.capture_initial_state()
        total_files = len(self.initial_file_mtimes)
        print(f"Tracking {total_files} files")
        print()

        # Build the command - run Claude directly
        cmd = [
            CLAUDE_BINARY,
            "--print",
            "--dangerously-skip-permissions",
            CLEANING_PROMPT_TEMPLATE
        ]

        try:
            # Set environment for unbuffered output
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'

            print("Starting Claude Code processing...")
            print(f"[{time.strftime('%H:%M:%S')}] Launching Claude...")
            print("=" * 80)
            sys.stdout.flush()

            # Start monitoring thread
            self.monitoring = True
            monitor_thread = threading.Thread(target=self.monitor_progress, daemon=True)
            monitor_thread.start()

            # Run Claude directly - let it write to our stdout/stderr
            # This avoids all buffering issues from pipes
            returncode = subprocess.call(
                cmd,
                cwd=self.raw_markdown_dir,
                env=env,
                stdin=subprocess.DEVNULL
            )

            # Stop monitoring
            self.monitoring = False
            monitor_thread.join(timeout=1)

            print("=" * 80)
            print(f"[{time.strftime('%H:%M:%S')}] Claude process completed")
            print(f"Total files processed: {self.processed_count}/{total_files}")

            if returncode != 0:
                print(f"Claude process failed with return code {returncode}")
                return False

            return True

        except FileNotFoundError:
            self.monitoring = False
            print(f"Error: Claude Code CLI ('{CLAUDE_BINARY}') not found in PATH")
            return False
        except KeyboardInterrupt:
            self.monitoring = False
            print("\n[Interrupted] Exiting...")
            raise
        except Exception as e:
            self.monitoring = False
            print(f"Unexpected error running Claude: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run(self):
        """Main execution flow"""
        print("=" * 80)
        print("LimaCharlie Markdown Documentation Cleaner")
        print("=" * 80)
        print(f"Target directory: {self.raw_markdown_dir}")

        # Count files
        file_count = self.count_markdown_files()
        print(f"Found {file_count} markdown files to process")
        print("")

        # Run Claude Code
        success = self.run_claude_headless()

        if success:
            print("\n" + "=" * 80)
            print("Success! Documentation has been cleaned.")
            print("Review the changes and commit when ready.")
            print("=" * 80)
            return 0
        else:
            print("\n" + "=" * 80)
            print("Failed to complete cleaning process.")
            print("=" * 80)
            return 1


def main():
    """Entry point"""
    try:
        cleaner = MarkdownCleaner(RAW_MARKDOWN_DIR)
        return cleaner.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        return 130
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
