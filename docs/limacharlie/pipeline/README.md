# LimaCharlie Documentation Pipeline

This directory contains scripts to fetch and process the LimaCharlie documentation from https://docs.limacharlie.io/docs.

## Scripts

### fetch_docs.py

Main script to fetch all documentation articles from the LimaCharlie documentation site via the Algolia API.

**Features:**
- Automatically extracts API credentials from the documentation page
- Fetches all public, non-deleted, non-draft articles (~612 articles)
- Creates directory structure based on article breadcrumbs
- Saves articles as markdown with metadata headers
- Supports resume capability (skips already downloaded files)

**Dependencies:**
```bash
pip3 install requests beautifulsoup4 html2text
```

**Usage:**
```bash
# Fetch all documentation
python3 limacharlie/pipeline/fetch_docs.py

# Or make it executable and run directly
chmod +x limacharlie/pipeline/fetch_docs.py
./limacharlie/pipeline/fetch_docs.py
```

**Output:**
- Articles are saved to `./limacharlie/raw_markdown/`
- Directory structure mirrors the breadcrumb hierarchy (e.g., `Add-Ons/API Integrations/`)
- Each file includes a YAML metadata header with title, slug, breadcrumb, source URL, and article ID

### test_fetch.py

Test script that fetches only the first 3 articles to verify the setup works correctly.

**Usage:**
```bash
python3 limacharlie/pipeline/test_fetch.py
```

## How It Works

1. **API Credential Extraction**: The script fetches the documentation home page and extracts the Algolia API credentials (app ID, search key, index name) from the page source.

2. **Article Metadata Fetch**: Using the Algolia API, it fetches all article metadata including title, slug, breadcrumb, and full text content in a single query.

3. **Filtering**: The Algolia API key has built-in filters that automatically exclude:
   - Deleted articles (isDeleted: true)
   - Hidden articles (isHidden: true)
   - Draft articles (isDraft: true)
   - Excluded articles (exclude: true)
   - Category entries (isCategory: true)
   - Unpublished articles (isUnpublished: true)

4. **Processing**: For each article:
   - Creates the directory structure based on breadcrumb
   - Generates a markdown file with metadata header
   - Saves the plain text content from Algolia

5. **Error Handling**:
   - Skips articles without content
   - Supports resume capability (skips existing files)
   - Comprehensive error logging

## Output Format

Each markdown file contains:

```markdown
---
title: Article Title
slug: article-slug
breadcrumb: Category > Subcategory
source: https://docs.limacharlie.io/docs/article-slug
articleId: uuid-here
---

Article content in plain text format...
```

## Statistics

As of the last run:
- Total entries in Algolia: 680
- Articles (filtered): 612
- Categories (excluded): 68
- Output directory: `./limacharlie/raw_markdown/`
