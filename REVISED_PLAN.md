# Revised Implementation Plan - Focus on Quality

## Executive Summary

After manual quality assessment, the issues are **real, not verification false positives**. The HTML extraction logic in `convert.py` is failing for 141 pages (49% of dataset).

**Revised priorities:**
1. ⚡ **Fix HTML extraction** - Immediate 40% quality improvement
2. 🎯 **Semantic pipeline** - Enhancement layer (later)
3. 🧹 **Polish** - Nice to haves

## Key Finding

The conversion pipeline works great when it extracts the right HTML! 133 pages (46%) are already high quality. We just need to fix extraction for the other 141 pages.

**Before:** Thought verification had false positives
**After:** Verification is accurate, extraction is broken

---

## Phase 1: Fix HTML Extraction (PRIORITY)

### Goal
Fix `doc-pipeline/lib/convert.py` to correctly extract main content from Document360 pages.

### Current Problem

```python
# This is too simplistic for Document360
content_selectors = [
    'article',
    '.article-content',
    '[role="main"]',
]
```

These selectors often find the wrong element (metadata/navigation instead of main content).

### Solution: Robust Content Detection

**Step 1: Save extraction output for debugging** (30 min)

```python
# Add to convert.py
def save_extraction_debug(slug, html, extracted, markdown):
    """Save extraction artifacts for failed pages."""
    debug_dir = Path('.doc-pipeline-state/extraction-debug') / slug
    debug_dir.mkdir(parents=True, exist_ok=True)

    (debug_dir / 'full.html').write_text(html[:50000])  # First 50KB
    (debug_dir / 'extracted.html').write_text(extracted)
    (debug_dir / 'output.md').write_text(markdown)
```

**Step 2: Analyze failed pages** (1 hour)

Manually inspect HTML structure of:
- `adapter-types-evtx` (226 → 46 words)
- `add-ons-api-integrations` (287 → 39 words)
- `adapter-types-zendesk` (417 → 46 words)

Find the correct CSS selectors for Document360 content.

**Step 3: Implement improved extraction** (2-3 hours)

```python
def extract_main_content(html: str) -> str:
    """
    Extract main article content from Document360 HTML.

    Strategy:
    1. Try Document360-specific selectors
    2. Use heuristics (most <p> tags, longest text)
    3. Validate extraction (must have minimum content)
    4. Fall back to full HTML if extraction seems wrong
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Try Document360 specific patterns
    candidates = []

    # 1. Standard content selectors
    for selector in ['article', '.article-content', '.doc-content', 'main']:
        elem = soup.select_one(selector)
        if elem:
            candidates.append(('selector', elem, len(elem.get_text())))

    # 2. Find div with most paragraph tags
    for div in soup.find_all('div'):
        p_count = len(div.find_all('p'))
        if p_count > 3:  # Significant content
            candidates.append(('p-count', div, p_count * 100))

    # 3. Find element with most text
    for elem in soup.find_all(['div', 'section', 'article']):
        text_len = len(elem.get_text(strip=True))
        if text_len > 500:  # Minimum content threshold
            candidates.append(('text-len', elem, text_len))

    if not candidates:
        # Fall back to body
        return str(soup.find('body') or html)

    # Sort by score and pick best
    candidates.sort(key=lambda x: x[2], reverse=True)
    method, best_elem, score = candidates[0]

    extracted = str(best_elem)

    # Validation: Check if extraction looks reasonable
    word_count = len(best_elem.get_text().split())
    heading_count = len(best_elem.find_all(['h1', 'h2', 'h3', 'h4']))
    code_blocks = len(best_elem.find_all(['pre', 'code']))

    # If extraction seems too small, use next best candidate or full HTML
    if word_count < 100 and heading_count < 2:
        if len(candidates) > 1:
            extracted = str(candidates[1][1])
        else:
            extracted = html  # Use full HTML as last resort

    return extracted
```

**Step 4: Test on failed pages** (1 hour)

```bash
# Create test script
python3 doc-pipeline/test_extraction.py \
    adapter-types-evtx \
    add-ons-api-integrations \
    adapter-types-zendesk
```

Verify:
- Word count improves (226 → 200+ words)
- Code blocks preserved (6 in HTML → 6 in markdown)
- Sections present (Overview, Configurations, API Doc)

**Step 5: Re-run conversion on all pages** (10 min)

```bash
# Run just the conversion phase with improved extraction
python3 -m doc-pipeline --no-commit

# Check results
python3 -c "
import json
with open('.doc-pipeline-state/verification_report.json') as f:
    report = json.load(f)
    print(f'Critical issues: {report[\"critical\"]} (was 387)')
    print(f'Pages passed: {report[\"passed\"]}/{report[\"total_pages\"]} (was 12/290)')
"
```

**Target metrics:**
- Critical issues: <50 (was 387)
- Pages passing: >250 (was 12)
- Content loss pages: <20 (was 157)

### Time Estimate
- Debug setup: 30 min
- Analysis: 1 hour
- Implementation: 2-3 hours
- Testing: 1 hour
- Full re-run: 10 min

**Total: 5-6 hours**

### Success Criteria
- [ ] extraction-debug files created for failed pages
- [ ] Correct CSS selectors identified
- [ ] Improved extraction code implemented
- [ ] Tests passing on previously failed pages
- [ ] Verification report shows <50 critical issues
- [ ] >85% of pages passing quality checks

---

## Phase 2: Semantic Pipeline (ENHANCEMENT)

**Only start this after Phase 1 is complete and working**

### Why Semantic Pipeline Still Valuable

Even with fixed extraction, semantic processing adds:
- **API Index**: Comprehensive reference of all APIs
- **Smart Cross-References**: Semantic relationships, not just navigation links
- **Better Metadata**: Understanding-based keywords and complexity ratings
- **COMBINED.md**: Intelligently organized single-file documentation

### Approach

**Option A: Lightweight Enhancement (Recommended)**
- Keep fixed extraction for conversion
- Use semantic pipeline only for post-processing:
  - API extraction from converted markdown
  - Cross-reference generation
  - Index building

**Option B: Full Semantic Replacement**
- Claude does extraction AND enhancement
- Give Claude full HTML, let it extract content
- More ambitious, higher risk

### Implementation

See original `IMPROVEMENT_PLAN.md` Priority 1-2 for detailed steps.

**Time estimate: 12-16 hours**

---

## Phase 3: Polish

After Phase 1 (and optionally Phase 2), these improvements add value:

### 3a. Filter Navigation Pages from Verification (1 hour)

```python
def is_navigation_page(markdown: str) -> bool:
    """Detect category index pages."""
    if re.search(r'\d+ Articles? in this category', markdown):
        return True
    if len(markdown.split()) < 50:
        return True
    return False

# In verify.py, skip navigation pages or mark separately
```

### 3b. Add Extraction Tests (2 hours)

```python
# tests/test_extraction.py
def test_evtx_extraction():
    """Test extraction preserves content for EVTX page."""
    with open('fixtures/adapter-types-evtx.html') as f:
        html = f.read()

    extracted = extract_main_content(html)
    soup = BeautifulSoup(extracted, 'html.parser')

    # Verify key sections present
    assert soup.find(text=re.compile('Overview'))
    assert soup.find(text=re.compile('Configurations'))
    assert len(soup.find_all('pre')) >= 6  # Code blocks
```

### 3c. Document Extraction Patterns (1 hour)

Create `doc-pipeline/EXTRACTION_GUIDE.md`:
- Document360 HTML structure
- Known selector patterns
- Troubleshooting failed pages
- How to test extraction

**Total time: 4 hours**

---

## Simplified Timeline

### Week 1: Fix Extraction (Must Do)
- Days 1-2: Debug and implement improved extraction
- Day 3: Test and iterate
- Day 4: Re-run pipeline, verify quality
- Day 5: Commit, document findings

**Deliverable**: 85%+ pages with good quality

### Week 2+: Semantic Enhancements (Optional)
- Only if Phase 1 successful
- Only if semantic features provide clear value
- Consider lightweight approach first

**Deliverable**: API index, cross-references, COMBINED.md

---

## Decision Point

After completing Phase 1, evaluate:

**Scenario A: Quality is now excellent (>85% pass)**
→ Consider semantic enhancements a nice-to-have
→ Focus on using the good docs you have
→ Semantic pipeline can wait

**Scenario B: Quality still has issues**
→ Investigate remaining failures
→ Consider manual fixes for problem pages
→ Document workarounds

**Scenario C: Quality great, want more**
→ Proceed with lightweight semantic enhancements
→ API index and cross-references
→ Keep existing conversion, add enhancement layer

---

## Comparison: Old vs. New Plan

### Old Plan (IMPROVEMENT_PLAN.md)
- **Focus**: Debug semantic batching first
- **Time**: 46-58 hours (2 weeks)
- **Risk**: High (Claude CLI issues)
- **Value**: Semantic enhancements

### New Plan (This Document)
- **Focus**: Fix extraction first
- **Time**: 5-6 hours (1 day)
- **Risk**: Low (standard coding)
- **Value**: Immediate quality improvement

### Why This Is Better

1. **Faster results**: 1 day vs 2 weeks
2. **Lower risk**: Known fix vs debugging integration
3. **Incremental**: Can stop after Phase 1 if good enough
4. **Preserves options**: Can still do semantic pipeline later

---

## Next Steps

1. **Start Phase 1 immediately**
   ```bash
   cd doc-pipeline
   git checkout -b fix/html-extraction
   # Add debug output to convert.py
   # Test on adapter-types-evtx
   ```

2. **Create extraction test fixtures**
   ```bash
   mkdir -p doc-pipeline/tests/fixtures
   # Save HTML for failed pages
   ```

3. **Implement improved extraction**
   - See Step 3 above for code
   - Test incrementally
   - Verify on multiple failed pages

4. **Re-run pipeline and measure**
   ```bash
   python3 -m doc-pipeline --no-commit
   # Check verification report
   # Count improvements
   ```

5. **Commit if successful**
   ```bash
   git add -A
   git commit -m "fix: improve HTML content extraction for Document360 pages"
   ```

---

## Questions?

- See `FINDINGS.md` for detailed quality analysis
- See `IMPROVEMENT_PLAN.md` for original semantic pipeline plan
- See `QUICK_START.md` for development setup

**Start here:** Phase 1, Step 1 - Add debug output to save extraction artifacts
