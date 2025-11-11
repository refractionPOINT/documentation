#!/usr/bin/env python3
"""
Test script to verify fetch_docs.py works with a small sample
"""

import sys
import os

# Add the pipeline directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from fetch_docs import LimaCharlieFetcher

class TestFetcher(LimaCharlieFetcher):
    """Test version that only fetches a few articles"""

    def fetch_all_articles(self):
        """Override to only fetch a few articles for testing"""
        print("\n[TEST MODE] Fetching only first 3 articles...")

        articles = super().fetch_all_articles()

        if articles:
            # Return only first 3 articles
            return articles[:3]
        return []

def main():
    print("=" * 80)
    print("TEST MODE: Fetching only 3 articles")
    print("=" * 80)

    fetcher = TestFetcher()
    return fetcher.run()

if __name__ == "__main__":
    sys.exit(main())
