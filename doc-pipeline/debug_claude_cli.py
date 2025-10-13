#!/usr/bin/env python3
"""
Debug script to investigate Claude CLI integration issues.

Tests various scenarios to identify why the batching phase fails.
"""
import json
import subprocess
import sys
from pathlib import Path


def test_basic_json_response():
    """Test if Claude CLI can return simple JSON."""
    print("=" * 60)
    print("TEST 1: Basic JSON Response")
    print("=" * 60)

    prompt = "Return only this JSON with no other text: {\"test\": \"success\"}"

    try:
        result = subprocess.run(
            ['claude', '--print'],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=30
        )

        print(f"Return code: {result.returncode}")
        print(f"STDOUT length: {len(result.stdout)}")
        print(f"STDERR length: {len(result.stderr)}")
        print("\nRaw output:")
        print(result.stdout)
        print("\nCleaned output:")

        # Try to clean and parse
        cleaned = clean_response(result.stdout)
        print(cleaned)

        try:
            data = json.loads(cleaned)
            print(f"\n✅ Successfully parsed: {data}")
            return True
        except json.JSONDecodeError as e:
            print(f"\n❌ Failed to parse: {e}")
            return False

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


def test_batching_prompt_small():
    """Test batching with small dataset (5 pages)."""
    print("\n" + "=" * 60)
    print("TEST 2: Small Batching Prompt (5 pages)")
    print("=" * 60)

    pages = [
        "quickstart: Quickstart",
        "what-is-limacharlie: What is LimaCharlie?",
        "sensors: Sensors",
        "detection-and-response: Detection and Response",
        "lcql: LimaCharlie Query Language"
    ]

    prompt = f"""You are grouping documentation pages into semantic batches for parallel processing.

PAGES ({len(pages)} total):
{chr(10).join([f"- {p}" for p in pages])}

Create batches with these criteria:
1. Each batch contains 2-3 related pages
2. Pages in a batch share a common theme/topic
3. Users would likely read these pages together
4. Batches represent coherent workflows or concepts

Output JSON format:
{{
  "batches": [
    {{
      "id": "batch_01_descriptive_name",
      "theme": "Brief description of what this batch covers",
      "page_slugs": ["slug1", "slug2"]
    }}
  ]
}}

Output only valid JSON, no markdown formatting."""

    try:
        result = subprocess.run(
            ['claude', '--print'],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=60
        )

        print(f"Return code: {result.returncode}")
        print(f"\nRaw output (first 500 chars):")
        print(result.stdout[:500])

        # Clean and parse
        cleaned = clean_response(result.stdout)
        print(f"\nCleaned output (first 500 chars):")
        print(cleaned[:500])

        try:
            data = json.loads(cleaned)
            print(f"\n✅ Successfully parsed batches:")
            for batch in data.get('batches', []):
                print(f"  - {batch.get('id')}: {len(batch.get('page_slugs', []))} pages")
            return True
        except json.JSONDecodeError as e:
            print(f"\n❌ Failed to parse: {e}")
            print(f"Error at position {e.pos}")
            if e.pos < len(cleaned):
                print(f"Context: ...{cleaned[max(0, e.pos-50):e.pos+50]}...")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Command timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


def test_with_actual_pipeline_data():
    """Test with real page data from pipeline state."""
    print("\n" + "=" * 60)
    print("TEST 3: Real Pipeline Data (if available)")
    print("=" * 60)

    state_file = Path('.doc-pipeline-state/01-fetch.json')

    if not state_file.exists():
        print("⚠️  No pipeline state found, skipping test")
        return None

    try:
        with open(state_file) as f:
            state = json.load(f)

        # Get first 10 pages from first category
        categories = state.get('categories', {})
        if not categories:
            print("⚠️  No categories in state, skipping test")
            return None

        first_category = list(categories.keys())[0]
        pages = categories[first_category][:10]

        print(f"Testing with {len(pages)} pages from category: {first_category}")

        page_list = "\n".join([
            f"- {p['slug']}: {p['title']}"
            for p in pages
        ])

        prompt = f"""You are grouping documentation pages into semantic batches for parallel processing.

PAGES ({len(pages)} total):
{page_list}

Create batches with these criteria:
1. Each batch contains 3-5 related pages
2. Pages in a batch share a common theme/topic
3. Users would likely read these pages together
4. Batches represent coherent workflows or concepts

Output JSON format:
{{
  "batches": [
    {{
      "id": "batch_01_descriptive_name",
      "theme": "Brief description of what this batch covers",
      "page_slugs": ["slug1", "slug2"]
    }}
  ]
}}

Output only valid JSON, no markdown formatting."""

        result = subprocess.run(
            ['claude', '--print'],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=90
        )

        print(f"Return code: {result.returncode}")

        cleaned = clean_response(result.stdout)

        try:
            data = json.loads(cleaned)
            print(f"\n✅ Successfully parsed batches:")
            for batch in data.get('batches', []):
                print(f"  - {batch.get('id')}: {len(batch.get('page_slugs', []))} pages")
            return True
        except json.JSONDecodeError as e:
            print(f"\n❌ Failed to parse: {e}")
            # Save failed response for inspection
            debug_file = Path('.doc-pipeline-state/debug_response.txt')
            debug_file.parent.mkdir(exist_ok=True)
            with open(debug_file, 'w') as f:
                f.write(f"RAW OUTPUT:\n{result.stdout}\n\n")
                f.write(f"CLEANED OUTPUT:\n{cleaned}\n\n")
                f.write(f"ERROR: {e}")
            print(f"Saved failed response to: {debug_file}")
            return False

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def clean_response(raw_output: str) -> str:
    """
    Remove markdown code blocks and extra formatting from Claude output.

    Handles common patterns:
    - ```json ... ```
    - ```\n ... \n```
    - Extra whitespace
    """
    output = raw_output.strip()

    # Remove markdown code blocks
    if output.startswith('```'):
        lines = output.split('\n')

        # Remove first line if it's a code fence
        if lines[0].startswith('```'):
            lines = lines[1:]

        # Remove last line if it's a code fence
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]

        output = '\n'.join(lines).strip()

    return output


def main():
    """Run all tests."""
    print("\nClaude CLI Integration Debug Script")
    print("=" * 60)

    results = []

    # Test 1: Basic JSON
    results.append(('Basic JSON', test_basic_json_response()))

    # Test 2: Small batching
    results.append(('Small Batching (5 pages)', test_batching_prompt_small()))

    # Test 3: Real data
    result = test_with_actual_pipeline_data()
    if result is not None:
        results.append(('Real Pipeline Data (10 pages)', result))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    passed = sum(1 for _, r in results if r)
    total = len(results)

    print(f"\nTotal: {passed}/{total} tests passed")

    # Recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)

    if all(r for _, r in results):
        print("✅ All tests passed! The Claude CLI integration is working.")
        print("   The batching issue may be due to:")
        print("   - Prompt too large (290 pages)")
        print("   - Timeout (need longer than 300s)")
        print("   - Rate limiting")
    else:
        print("Issues found:")
        for name, result in results:
            if not result:
                print(f"  ❌ {name} failed")

        print("\nNext steps:")
        print("  1. Review the raw output above")
        print("  2. Check .doc-pipeline-state/debug_response.txt if available")
        print("  3. Consider implementing response cleaning in claude_client.py")
        print("  4. Test with smaller batches (category-level batching)")

    return 0 if all(r for _, r in results) else 1


if __name__ == '__main__':
    sys.exit(main())
