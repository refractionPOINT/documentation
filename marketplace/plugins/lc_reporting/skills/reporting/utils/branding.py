#!/usr/bin/env python3
"""
Brand Extraction and Styling Utility
Extracts brand colors and fonts from company websites for report customization
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json


# LimaCharlie Default Branding
LIMACHARLIE_BRAND = {
    'name': 'LimaCharlie',
    'primary_color': '#667eea',      # Purple-blue (from report gradient)
    'secondary_color': '#764ba2',    # Deep purple (from report gradient)
    'accent_color': '#4F9EEE',       # Bright blue
    'background_dark': '#00030C',    # Very dark navy
    'background_light': '#f5f5f5',   # Light gray
    'text_dark': '#333333',
    'text_light': '#ffffff',
    'success_color': '#28a745',
    'warning_color': '#ffc107',
    'danger_color': '#dc3545',
    'fonts': {
        'header': "'Syne', sans-serif",
        'body': "'Rubik', sans-serif",
        'code': "'IBM Plex Mono', monospace"
    },
    'gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
}

# Generic/Personal Email Domains (use LimaCharlie branding)
GENERIC_DOMAINS = [
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
    'aol.com', 'icloud.com', 'protonmail.com', 'mail.com',
    'zoho.com', 'yandex.com', 'gmx.com'
]


def extract_email_domain(email):
    """Extract domain from email address"""
    if not email or '@' not in email:
        return None
    return email.split('@')[1].lower()


def is_business_domain(domain):
    """Check if domain is a business domain (not generic email provider)"""
    return domain not in GENERIC_DOMAINS


def extract_colors_from_css(css_text):
    """Extract hex color codes from CSS text"""
    # Match hex colors (#RGB or #RRGGBB)
    hex_pattern = r'#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})\b'
    colors = re.findall(hex_pattern, css_text)

    # Normalize 3-char hex to 6-char
    normalized = []
    for color in colors:
        if len(color) == 3:
            color = ''.join([c*2 for c in color])
        normalized.append(f'#{color}')

    return list(set(normalized))  # Remove duplicates


def extract_fonts_from_css(css_text):
    """Extract font families from CSS text"""
    font_pattern = r'font-family:\s*([^;]+);'
    fonts = re.findall(font_pattern, css_text, re.IGNORECASE)
    return [f.strip() for f in fonts[:5]]  # Top 5 fonts


def fetch_company_branding(domain):
    """
    Fetch brand colors and fonts from a company website

    Args:
        domain: Company domain (e.g., 'anthropic.com')

    Returns:
        dict: Brand information or None if extraction fails
    """
    try:
        # Try to fetch the company homepage
        url = f'https://{domain}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; ReportGenerator/1.0)'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract CSS from inline styles and style tags
        css_text = ''
        for style in soup.find_all('style'):
            css_text += style.string or ''

        # Extract colors
        colors = extract_colors_from_css(css_text + response.text)

        # Extract fonts
        fonts = extract_fonts_from_css(css_text)

        # Get meta theme color if available
        theme_color = None
        theme_meta = soup.find('meta', attrs={'name': 'theme-color'})
        if theme_meta and theme_meta.get('content'):
            theme_color = theme_meta.get('content')

        # Try to identify primary colors (most common, excluding black/white/gray)
        primary_colors = [c for c in colors if c.lower() not in ['#ffffff', '#000000', '#fff', '#000']]

        # Filter out grays (colors where R, G, B are very similar)
        def is_colorful(hex_color):
            hex_color = hex_color.lstrip('#')
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            # If RGB values are within 30 of each other, it's grayish
            return max(r, g, b) - min(r, g, b) > 30

        colorful_colors = [c for c in primary_colors if is_colorful(c)]

        # Build brand dict
        brand = {
            'name': domain.split('.')[0].title(),
            'primary_color': theme_color or (colorful_colors[0] if colorful_colors else '#667eea'),
            'secondary_color': colorful_colors[1] if len(colorful_colors) > 1 else '#764ba2',
            'accent_color': colorful_colors[2] if len(colorful_colors) > 2 else '#4F9EEE',
            'all_colors': colors[:20],  # Top 20 colors found
            'fonts': {
                'header': fonts[0] if fonts else "'Arial', sans-serif",
                'body': fonts[1] if len(fonts) > 1 else "'Helvetica', sans-serif",
                'code': "'Courier New', monospace"
            },
            'source': url,
            'extracted': True
        }

        return brand

    except Exception as e:
        print(f"Warning: Could not extract branding from {domain}: {e}")
        return None


def get_brand_for_user(user_email=None):
    """
    Get appropriate branding based on user's email domain

    Args:
        user_email: User's email address (optional)

    Returns:
        dict: Brand configuration to use for reports
    """
    # Default to LimaCharlie branding
    if not user_email:
        return LIMACHARLIE_BRAND

    # Extract domain
    domain = extract_email_domain(user_email)
    if not domain:
        return LIMACHARLIE_BRAND

    # Check if business domain
    if not is_business_domain(domain):
        print(f"Using LimaCharlie branding (generic email domain: {domain})")
        return LIMACHARLIE_BRAND

    # Try to extract company branding
    print(f"Detected business domain: {domain}")
    print("Attempting to extract company branding...")

    company_brand = fetch_company_branding(domain)

    if company_brand:
        print(f"✓ Successfully extracted branding from {domain}")
        print(f"  Primary color: {company_brand['primary_color']}")
        print(f"  Secondary color: {company_brand['secondary_color']}")
        return company_brand
    else:
        print(f"✗ Could not extract branding, using LimaCharlie defaults")
        return LIMACHARLIE_BRAND


def generate_css_from_brand(brand):
    """
    Generate CSS variables from brand configuration

    Args:
        brand: Brand dictionary

    Returns:
        str: CSS variable definitions
    """
    return f"""
        /* Brand Colors */
        --brand-primary: {brand['primary_color']};
        --brand-secondary: {brand['secondary_color']};
        --brand-accent: {brand.get('accent_color', brand['primary_color'])};
        --brand-success: {brand.get('success_color', '#28a745')};
        --brand-warning: {brand.get('warning_color', '#ffc107')};
        --brand-danger: {brand.get('danger_color', '#dc3545')};

        /* Backgrounds */
        --bg-dark: {brand.get('background_dark', '#00030C')};
        --bg-light: {brand.get('background_light', '#f5f5f5')};

        /* Text Colors */
        --text-dark: {brand.get('text_dark', '#333333')};
        --text-light: {brand.get('text_light', '#ffffff')};

        /* Fonts */
        --font-header: {brand['fonts']['header']};
        --font-body: {brand['fonts']['body']};
        --font-code: {brand['fonts'].get('code', "'Courier New', monospace")};

        /* Gradient */
        --brand-gradient: {brand.get('gradient', f"linear-gradient(135deg, {brand['primary_color']} 0%, {brand['secondary_color']} 100%)")};
    """


def get_font_imports(brand):
    """
    Generate Google Fonts import links for brand fonts

    Args:
        brand: Brand dictionary

    Returns:
        str: HTML link tags for font imports
    """
    fonts = []

    # Extract font families from brand
    for font_type, font_family in brand['fonts'].items():
        # Extract first font name from family string
        match = re.search(r"'([^']+)'", font_family)
        if match:
            font_name = match.group(1)
            # Google Fonts uses + for spaces
            font_name_encoded = font_name.replace(' ', '+')
            fonts.append(font_name_encoded)

    # Generate import links
    if fonts:
        font_params = '|'.join([f'{font}:400,600,700' for font in fonts])
        return f'<link href="https://fonts.googleapis.com/css2?family={font_params}&display=swap" rel="stylesheet">'

    return ''


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        email = sys.argv[1]
        print(f"\nTesting brand extraction for: {email}\n")
        brand = get_brand_for_user(email)
        print(f"\nBrand Configuration:")
        print(json.dumps(brand, indent=2))
        print(f"\nCSS Variables:")
        print(generate_css_from_brand(brand))
    else:
        print("Usage: python branding.py user@example.com")
        print("\nTesting with LimaCharlie defaults:")
        print(json.dumps(LIMACHARLIE_BRAND, indent=2))
