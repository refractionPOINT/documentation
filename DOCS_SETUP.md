# Documentation Site Setup Guide

This guide explains the MkDocs setup for the LimaCharlie official documentation site.

## Overview

The documentation site uses **MkDocs Material**, a modern, feature-rich static site generator perfect for technical documentation.

## Features

### Branding & Design
- **Custom Color Scheme**: Matches LimaCharlie brand (Midnight blue #00183c, Maroon Flush #c32152)
- **Typography**: Syne for headings, Rubik for body text, IBM Plex Mono for code
- **Dark Mode**: Dark mode by default with light mode toggle
- **Official Logo**: Downloaded from Brandfetch CDN

### Navigation
- **Tabbed Navigation**: Top-level navigation tabs for major sections
- **Expandable Sections**: Collapsible navigation tree
- **Search**: Full-text search with highlighting and suggestions
- **Breadcrumbs**: Path navigation for deep pages

### Content Features
- **Code Highlighting**: Syntax highlighting for YAML, Python, Go, Bash, JSON, and more
- **Code Annotations**: Add explanations inline with code
- **Admonitions**: Note, warning, tip, and other callout boxes
- **Mermaid Diagrams**: Flowcharts and diagrams in markdown
- **Tables**: Enhanced table styling

### Technical Features
- **Instant Navigation**: Fast page loads without full reload
- **Offline Search**: Search works without internet
- **Mobile Responsive**: Perfect display on all devices
- **SEO Optimized**: Proper meta tags and structure

## File Structure

```
documentation/
├── .github/
│   └── workflows/
│       └── docs.yml              # GitHub Actions deployment
├── docs/
│   └── assets/
│       ├── images/
│       │   ├── logo.svg          # LimaCharlie logo
│       │   ├── logo-dark.svg     # Dark theme logo
│       │   └── favicon.png       # Site favicon
│       └── stylesheets/
│           └── extra.css         # Custom brand styling
├── limacharlie/doc/              # Platform documentation (276 files)
├── go-sdk/                       # Go SDK documentation
├── python-sdk/                   # Python SDK documentation
├── sdk/                          # SDK landing page
├── overrides/                    # MkDocs theme overrides (if needed)
├── index.md                      # Site home page
├── mkdocs.yml                    # MkDocs configuration
├── requirements.txt              # Python dependencies
└── .gitignore                    # Git ignore patterns
```

## Configuration Highlights

### mkdocs.yml

Key configuration sections:

```yaml
site_name: LimaCharlie Documentation
docs_dir: .  # Use repo root as docs directory

theme:
  name: material
  palette:
    - scheme: slate      # Dark mode default
      primary: custom    # Custom primary color
      accent: custom     # Custom accent color

  features:
    - navigation.tabs           # Top tabs
    - navigation.expand         # Auto-expand sections
    - search.suggest            # Search suggestions
    - content.code.copy         # Copy code buttons

plugins:
  - search                      # Built-in search

markdown_extensions:
  - pymdownx.highlight          # Code highlighting
  - pymdownx.superfences        # Code blocks
  - admonition                  # Callouts
  # ... and more
```

### Custom CSS (docs/assets/stylesheets/extra.css)

Implements LimaCharlie branding:
- Brand colors for light and dark modes
- Custom heading styles with Syne font
- Enhanced code block styling
- Glassmorphic UI elements
- Custom scrollbar styling

## Deployment

### Automatic Deployment (GitHub Pages)

The site deploys automatically via GitHub Actions (`.github/workflows/docs.yml`):

1. Triggers on push to `master` or `main` branch
2. Installs Python dependencies
3. Builds static site with `mkdocs build`
4. Deploys to GitHub Pages with `mkdocs gh-deploy`

### Manual Deployment

To deploy manually:

```bash
# Build the site
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy --force
```

## Local Development

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Serve with live reload
mkdocs serve

# Open http://127.0.0.1:8000
```

### Build Static Site

```bash
mkdocs build
```

Outputs to `site/` directory.

## Customization Guide

### Changing Colors

Edit `docs/assets/stylesheets/extra.css`:

```css
:root {
  --md-primary-fg-color: #YOUR_COLOR;
  --md-accent-fg-color: #YOUR_ACCENT;
}
```

### Adding New Pages

1. Create markdown file in appropriate directory
2. Add to `nav:` in `mkdocs.yml`:

```yaml
nav:
  - Section Name:
    - Page Title: path/to/file.md
```

### Custom Components

Add custom HTML/CSS in `overrides/` directory:
- `overrides/main.html` - Override main template
- `overrides/partials/` - Override specific components

## Maintenance

### Updating Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Checking for Broken Links

```bash
mkdocs build --strict
```

This will fail if there are any broken internal links.

### Performance

The current setup handles:
- 276+ documentation pages
- Fast search indexing
- Instant navigation between pages
- Mobile-optimized delivery

## Troubleshooting

### Build Errors

If you encounter build errors:

1. Check `mkdocs.yml` syntax (valid YAML)
2. Verify all files in `nav:` exist
3. Check for malformed markdown
4. Run `mkdocs build --strict --verbose`

### Missing Pages

If pages don't appear:

1. Ensure file is in `docs_dir` (`.` in this case)
2. Check file is in `nav:` section
3. Verify file extension is `.md`
4. Check file permissions

### Styling Issues

If custom styles don't apply:

1. Check `extra.css` is loaded in `mkdocs.yml`
2. Verify CSS syntax
3. Check browser console for errors
4. Clear browser cache

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Python Markdown Extensions](https://facelessuser.github.io/pymdown-extensions/)
- [LimaCharlie Platform](https://limacharlie.io)

## Support

For questions or issues with the documentation site:

- Open an issue on GitHub
- Join [Community Slack](https://slack.limacharlie.io)
- Email [support@limacharlie.io](mailto:support@limacharlie.io)
