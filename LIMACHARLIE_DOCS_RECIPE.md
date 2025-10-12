# LimaCharlie Documentation Conversion Recipe

This recipe provides step-by-step instructions for fetching and converting LimaCharlie documentation from document360 to clean markdown files. It automatically discovers the documentation structure from the website.

## Prerequisites

- Python 3.x installed
- Required Python packages: `pip install requests beautifulsoup4 markitdown`

## Steps

### 1. Create Project Structure

```bash
mkdir limacharlie-docs limacharlie-docs-markdown
```

### 2. Create Dynamic Documentation Discovery and Fetcher Script

Save this as `fetch_limacharlie_docs.py`:

```python
#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import os
import time
import json
import re
from urllib.parse import urljoin, urlparse

BASE_URL = "https://docs.limacharlie.io"
DOCS_URL = f"{BASE_URL}/docs"

def discover_documentation_structure():
    """Dynamically discover all documentation pages from the website."""
    print("Discovering documentation structure...")
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    visited = set()
    docs_structure = {}
    category_counter = 0
    
    # Fetch the main docs page
    try:
        response = requests.get(DOCS_URL, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for navigation links in the sidebar
        # Try multiple possible selectors for document360 navigation
        nav_selectors = [
            'nav a[href^="/docs"]',
            'aside a[href^="/docs"]',
            '.sidebar a[href^="/docs"]',
            'a[href^="/docs"]'
        ]
        
        all_links = set()
        for selector in nav_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href and '/docs/' in href:
                    all_links.add(href)
        
        print(f"Found {len(all_links)} documentation links")
        
        # Organize links into categories based on URL patterns
        for link in all_links:
            # Skip version-specific links
            if '/v1/' in link or '/v2/' in link:
                if '/v2/' in link:
                    link = link.replace('/v2', '')
                else:
                    continue
            
            # Extract page slug and potential category
            path = link.replace('/docs/', '')
            
            # Determine category based on common patterns
            category = None
            if 'quickstart' in path or 'what-is' in path or 'use-case' in path:
                category = "01-getting-started"
            elif 'sensor' in path or 'installation' in path or 'agent' in path:
                category = "02-sensors"
            elif 'event' in path or 'edr' in path:
                category = "03-events"
            elif 'lcql' in path or 'query' in path:
                category = "04-query-console"
            elif 'detection' in path or 'response' in path or 'replay' in path:
                category = "05-detection-response"
            elif 'platform' in path or 'sdk' in path or 'adapter' in path:
                category = "06-platform-management"
            elif 'output' in path or 'siem' in path:
                category = "07-outputs"
            elif 'add-on' in path or 'integration' in path or 'ext-' in path:
                category = "08-add-ons"
            elif 'tutorial' in path or 'report' in path:
                category = "09-tutorials"
            elif 'faq' in path:
                category = "10-faq"
            elif 'release' in path:
                category = "11-release-notes"
            else:
                category_counter += 1
                category = f"{category_counter:02d}-other"
            
            if category not in docs_structure:
                docs_structure[category] = []
            
            # Get the page title by fetching the page
            try:
                page_response = requests.get(f"{BASE_URL}{link}", headers=headers, timeout=10)
                page_soup = BeautifulSoup(page_response.text, 'html.parser')
                title = page_soup.find('h1')
                if title:
                    title = title.get_text().strip()
                else:
                    title = path.replace('-', ' ').title()
            except:
                title = path.replace('-', ' ').title()
            
            docs_structure[category].append((path, title))
            print(f"  Found: {category}/{path}")
            time.sleep(0.1)  # Be respectful
        
    except Exception as e:
        print(f"Error discovering structure: {e}")
        print("Falling back to manual search...")
        
        # Fallback: search for common documentation pages
        common_pages = [
            'what-is-limacharlie', 'quickstart', 'use-cases',
            'installation-keys', 'sensors', 'events', 'lcql',
            'detection-and-response', 'platform-management',
            'outputs', 'add-ons', 'tutorials', 'faq', 'release-notes'
        ]
        
        for page in common_pages:
            try:
                url = f"{DOCS_URL}/{page}"
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    category = "00-general"
                    if category not in docs_structure:
                        docs_structure[category] = []
                    docs_structure[category].append((page, page.replace('-', ' ').title()))
            except:
                continue
    
    return docs_structure

def download_page(url, save_path):
    """Download a single documentation page."""
    try:
        print(f"Downloading: {url}")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        metadata = {
            'url': url,
            'downloaded_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        meta_path = save_path.replace('.html', '.json')
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✓ Downloaded: {save_path}")
        return True
    except Exception as e:
        print(f"✗ Error: {url} - {e}")
        return False

def main():
    # Discover documentation structure dynamically
    docs_structure = discover_documentation_structure()
    
    if not docs_structure:
        print("Could not discover documentation structure!")
        return
    
    print(f"\nFound {sum(len(pages) for pages in docs_structure.values())} pages in {len(docs_structure)} categories")
    
    # Download all discovered pages
    for category, pages in sorted(docs_structure.items()):
        print(f"\nDownloading category: {category}")
        for page_slug, page_title in pages:
            url = f"{DOCS_URL}/{page_slug}"
            save_path = f"limacharlie-docs/{category}/{page_slug.replace('/', '-')}.html"
            download_page(url, save_path)
            time.sleep(0.5)  # Be respectful to the server
    
    # Save the discovered structure for reference
    with open('discovered_structure.json', 'w') as f:
        json.dump(docs_structure, f, indent=2)
    print("\nSaved documentation structure to discovered_structure.json")

if __name__ == "__main__":
    main()
```

### 3. Create Adaptive Conversion and Cleaning Script

Save this as `convert_and_clean.py`:

```python
#!/usr/bin/env python3
import subprocess
import re
from pathlib import Path
import os
import json

def clean_markdown_content(content):
    """Clean document360 artifacts from markdown content."""
    lines = content.split('\n')
    
    # Find main heading
    main_heading_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('# '):
            main_heading_idx = i
            break
    
    if main_heading_idx == -1:
        return content
    
    # Start from main heading
    cleaned_lines = [lines[main_heading_idx]]
    
    # Process content after heading
    i = main_heading_idx + 1
    skip_metadata = True
    
    while i < len(lines):
        line = lines[i]
        
        # Skip post-heading metadata
        if skip_metadata:
            if any(x in line for x in [
                'Updated on', 'Minutes to read', '* Print', '* Share', 
                '* Dark', 'Light', 'Article summary', 'Did you find this summary helpful?',
                'Thank you for your feedback!'
            ]):
                i += 1
                continue
            elif line.strip() == '---':
                i += 1
                continue
            elif line.strip() == '':
                i += 1
                continue
            else:
                skip_metadata = False
        
        # Check for feedback section
        if any(x in line for x in [
            'Was this article helpful?', 'How can we improve this article?',
            'Your feedback', 'Character limit :', 'Email (Optional)'
        ]):
            # Skip to What's Next or Related articles
            while i < len(lines):
                if lines[i].strip().startswith('###### What\'s Next') or \
                   lines[i].strip().startswith('###### Related articles'):
                    break
                i += 1
            continue
        
        cleaned_lines.append(line)
        i += 1
    
    result = '\n'.join(cleaned_lines)
    result = re.sub(r'\n{4,}', '\n\n\n', result)
    
    # Remove trailing empty lines and ---
    lines = result.split('\n')
    while lines and (lines[-1].strip() == '' or lines[-1].strip() == '---'):
        lines.pop()
    
    return '\n'.join(lines).strip()

def convert_file(html_path, md_path):
    """Convert HTML to markdown and clean it."""
    try:
        # Convert with markitdown
        result = subprocess.run(
            ['markitdown', str(html_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        
        if result.returncode == 0:
            # Clean the content
            cleaned = clean_markdown_content(result.stdout)
            
            # Save cleaned markdown
            os.makedirs(os.path.dirname(md_path), exist_ok=True)
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            
            print(f"✓ Converted: {md_path}")
            return True
    except Exception as e:
        print(f"✗ Error: {html_path} - {e}")
        return False

def create_combined_markdown(md_dir):
    """Create a single file with all documentation, organized by discovered structure."""
    with open(md_dir / "COMBINED.md", 'w') as combined:
        combined.write("# LimaCharlie Complete Documentation\n\n---\n\n")
        
        # Get all category directories that exist
        categories = []
        for cat_dir in sorted(md_dir.glob("*/")):
            if cat_dir.is_dir():
                # Extract category name from directory
                dir_name = cat_dir.name
                # Remove number prefix if present
                if re.match(r'^\d{2}-', dir_name):
                    display_name = dir_name[3:].replace('-', ' ').title()
                else:
                    display_name = dir_name.replace('-', ' ').title()
                
                categories.append((dir_name, display_name))
        
        # Write content for each category
        for cat_dir, cat_name in categories:
            category_path = md_dir / cat_dir
            
            # Get all markdown files in this category
            md_files = list(category_path.glob("*.md"))
            if md_files:
                combined.write(f"# {cat_name}\n\n")
                
                for md_file in sorted(md_files):
                    with open(md_file, 'r') as f:
                        content = f.read().strip()
                    
                    if content:
                        combined.write(content + "\n\n---\n\n")

def main():
    html_dir = Path("limacharlie-docs")
    md_dir = Path("limacharlie-docs-markdown")
    
    # Convert all HTML files found
    converted = 0
    failed = 0
    
    for html_file in html_dir.rglob("*.html"):
        relative_path = html_file.relative_to(html_dir)
        md_path = md_dir / relative_path.with_suffix('.md')
        
        if convert_file(html_file, md_path):
            converted += 1
        else:
            failed += 1
    
    print(f"\nConversion complete: {converted} successful, {failed} failed")
    
    # Create combined file
    print("Creating combined documentation...")
    create_combined_markdown(md_dir)
    print("✓ Created COMBINED.md")

if __name__ == "__main__":
    main()
```

### 4. Execute the Process

Run these commands in order:

```bash
# 1. Download all documentation pages (discovers structure automatically)
python3 fetch_limacharlie_docs.py

# 2. Convert HTML to clean Markdown
python3 convert_and_clean.py

# 3. Clean up (optional)
rm -rf limacharlie-docs
find limacharlie-docs-markdown -name "*.json" -delete
```

## Expected Output

- `limacharlie-docs-markdown/` directory with:
  - Dynamically organized category subdirectories
  - All discovered markdown files (number depends on current website)
  - `COMBINED.md` with all documentation in one file
- `discovered_structure.json` with the documentation structure that was found

## Key Features of This Process

1. **Dynamic Discovery**: Automatically finds all documentation pages on the website
2. **Adaptive Structure**: Organizes pages into categories based on URL patterns
3. **Clean Conversion**: Uses markitdown to convert HTML to Markdown
4. **Artifact Removal**: Strips all document360 UI elements:
   - Navigation headers/footers
   - Metadata (dates, reading time)
   - Share buttons and feedback forms
   - "Powered by Document360" banners
5. **Preserves Content**: Keeps all actual documentation content including:
   - Code blocks with proper formatting
   - Links and references
   - Images and diagrams
   - Section headings and structure
6. **Future-Proof**: Works even when pages are added, removed, or reorganized

## Advanced: Using Web Search for Discovery

If the direct discovery doesn't work well, you can enhance it with web search:

```python
# Add this function to fetch_limacharlie_docs.py for better discovery
def discover_via_search():
    """Use web search to find documentation pages."""
    search_terms = [
        "site:docs.limacharlie.io/docs",
        "site:docs.limacharlie.io/docs sensors",
        "site:docs.limacharlie.io/docs events",
        "site:docs.limacharlie.io/docs detection"
    ]
    
    discovered_urls = set()
    # Implementation would use search API or scraping
    # This is a placeholder for the concept
    return discovered_urls
```

## Notes

- The process adapts to the current website structure
- Takes about 2-3 minutes to complete depending on number of pages
- Requires internet connection to fetch documentation
- markitdown may show warnings about ffmpeg - these can be ignored
- The discovered structure is saved to `discovered_structure.json` for reference

## Quick One-Liner

If you save both scripts, you can run everything with:

```bash
python3 fetch_limacharlie_docs.py && python3 convert_and_clean.py && rm -rf limacharlie-docs && find limacharlie-docs-markdown -name "*.json" -delete
```

This will automatically discover, fetch, convert, clean, and organize all LimaCharlie documentation into markdown format.