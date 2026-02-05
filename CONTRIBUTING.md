# Contributing to LimaCharlie Documentation

Thank you for your interest in contributing to the LimaCharlie documentation!

## Local Development

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/refractionPOINT/documentation.git
cd documentation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Building the Documentation

To build the documentation locally:

```bash
mkdocs build
```

This will create a `site/` directory with the generated static HTML files.

### Previewing Changes

To preview the documentation with live reload:

```bash
mkdocs serve
```

Then open your browser to http://127.0.0.1:8000

The documentation will automatically rebuild when you save changes to any file.

## Documentation Structure

```
documentation/
├── docs/                      # Static assets and custom pages
│   └── assets/
│       ├── images/           # Logo and images
│       └── stylesheets/      # Custom CSS
├── limacharlie/doc/          # Main platform documentation
├── go-sdk/                   # Go SDK documentation
├── python-sdk/              # Python SDK documentation
├── mkdocs.yml               # MkDocs configuration
└── requirements.txt         # Python dependencies
```

## Making Changes

### Editing Documentation

1. Find the relevant markdown file in `limacharlie/doc/`, `go-sdk/`, or `python-sdk/`
2. Make your changes
3. Test locally with `mkdocs serve`
4. Commit and create a pull request

### Adding New Pages

1. Create a new markdown file in the appropriate directory
2. Add the page to the `nav:` section in `mkdocs.yml`
3. Test the navigation locally
4. Submit a pull request

### Updating Styles

Custom styles are in `docs/assets/stylesheets/extra.css`. Modifications should maintain the LimaCharlie brand identity:

- Primary color: Midnight (#00183c)
- Accent color: Maroon Flush (#c32152)
- Fonts: Syne (headings), Rubik (body), IBM Plex Mono (code)

## Deployment

The documentation is automatically deployed to GitHub Pages when changes are merged to the `master` branch via GitHub Actions.

## Pull Request Guidelines

1. **Focus**: Keep PRs focused on a single topic or issue
2. **Testing**: Test your changes locally before submitting
3. **Description**: Provide a clear description of what changed and why
4. **Screenshots**: Include screenshots for visual changes
5. **Links**: Verify all internal links work correctly

## Code of Conduct

Please be respectful and professional in all interactions. We're building documentation to help the security community, and we appreciate your contributions!

## Questions?

- Join our [Community Slack](https://slack.limacharlie.io)
- Email [support@limacharlie.io](mailto:support@limacharlie.io)
- Open an issue on GitHub

