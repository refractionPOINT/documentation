"""
Configuration for the LimaCharlie documentation transformation pipeline.
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
PIPELINE_DIR = BASE_DIR / "pipeline"
OUTPUT_DIR = BASE_DIR / "output"

# Source documentation
DOCS_BASE_URL = "https://docs.limacharlie.io"
DOCS_URL = f"{DOCS_BASE_URL}/docs"

# Output directories
RAW_HTML_DIR = OUTPUT_DIR / "raw-html"
RAW_MARKDOWN_DIR = OUTPUT_DIR / "raw-markdown"
CLEANED_MARKDOWN_DIR = OUTPUT_DIR / "cleaned-markdown"
TOPICS_DIR = OUTPUT_DIR / "topics"
METADATA_DIR = OUTPUT_DIR / "metadata"

# Topic subdirectories
TASKS_DIR = TOPICS_DIR / "tasks"
CONCEPTS_DIR = TOPICS_DIR / "concepts"
REFERENCE_DIR = TOPICS_DIR / "reference"

# Metadata files
DISCOVERED_PAGES_FILE = METADATA_DIR / "discovered_pages.json"
PROCESSED_TOPICS_FILE = METADATA_DIR / "processed_topics.json"
VERIFICATION_REPORT_FILE = METADATA_DIR / "verification_report.json"

# Final output files
INDEX_FILE = OUTPUT_DIR / "INDEX.md"
COMBINED_FILE = OUTPUT_DIR / "COMBINED.md"

# Pipeline settings
MAX_PARALLEL_WORKERS = int(os.getenv("MAX_PARALLEL_WORKERS", "5"))  # Reduced to avoid rate limiting
FETCH_DELAY_SECONDS = float(os.getenv("FETCH_DELAY_SECONDS", "1.0"))  # Increased to avoid 429 errors
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))

# User agent for requests
USER_AGENT = "Mozilla/5.0 (compatible; LimaCharlie-Doc-Pipeline/1.0)"

# Claude settings
CLAUDE_CLI = "claude"
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "sonnet")  # Can override with env var

# Algolia settings (for Document360 discovery)
# These are typically public read-only keys visible in the page source
ALGOLIA_APP_ID = "JX9O5RE9SU"
ALGOLIA_API_KEY = "N2M1ZDY0ZWNmYjc0MzhiZTI5ZDA1OGJiZTg4Y2E3MTNlZTcwYThiNDEyMjVlOTBkYTY5MGYyNTAzMGY3NjA2MmZpbHRlcnM9cHJvamVjdElkJTNBODRlYzIzMTEtMGUwNS00YzU4LTkwYjktYmFhOWMwNDFkMjJiJTIwQU5EJTIwTk9UJTIwaXNEZWxldGVkJTNBdHJ1ZSUyMEFORCUyMGlzRHJhZnQlM0FmYWxzZSUyMEFORCUyMGV4Y2x1ZGUlM0FmYWxzZSUyMEFORCUyMGlzSGlkZGVuJTNBZmFsc2UlMjBBTkQlMjBOT1QlMjBpc0NhdGVnb3J5SGlkZGVuJTNBdHJ1ZSUyMEFORCUyME5PVCUyMGlzVW5wdWJsaXNoZWQlM0F0cnVlJTIwQU5EJTIwTk9UJTIwZmxvd0FydGljbGVUeXBlJTNBZmxvaWsmbWluV29yZFNpemVmb3IxVHlwbz01Jm1pbldvcmRTaXplZm9yMlR5cG9zPTgmYWR2YW5jZWRTeW50YXg9dHJ1ZSZzeW5vbnltcz10cnVlJnR5cG9Ub2xlcmFuY2U9dHJ1ZSZyZW1vdmVTdG9wV29yZHM9ZW4mcmVzdHJpY3RJbmRpY2VzPWFydGljbGVzMTEmdmFsaWRVbnRpbD0xNzYwMzEyMDc2"
ALGOLIA_INDEX_NAME = "articles11"

# Logging
VERBOSE = os.getenv("VERBOSE", "true").lower() in ("true", "1", "yes")
