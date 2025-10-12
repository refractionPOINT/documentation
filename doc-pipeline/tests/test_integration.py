"""Integration tests for full pipeline."""
import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_pipeline_dry_run():
    """Test that pipeline can discover structure."""
    from lib import fetch
    from config import Config

    config = Config()
    structure = fetch.discover_documentation_structure(config)

    assert structure is not None
    assert len(structure.categories) > 0

    total_pages = sum(len(pages) for pages in structure.categories.values())
    assert total_pages > 0

    print(f"Discovered {total_pages} pages in {len(structure.categories)} categories")


def test_pipeline_phases_independent():
    """Test that each phase can run independently."""
    from models import Page, DocumentStructure
    from lib import convert, analyze, enhance
    from config import Config

    config = Config()

    # Create minimal test page
    page = Page(
        url="http://test.com",
        slug="test-page",
        title="Test Page",
        category="test",
        raw_html="<html><body><h1>Test</h1><p>Content</p><pre>code</pre></body></html>",
    )

    structure = DocumentStructure()
    structure.categories["test"] = [page]

    # Test convert phase
    assert convert.convert_page(page, config)
    assert page.markdown != ""

    # Test analyze phase
    metadata = analyze.extract_metadata(page, config)
    assert metadata is not None

    # Test enhance phase
    enhance.optimize_heading_hierarchy(page, config)
    assert page.markdown.startswith("# ")


def test_verification_catches_issues():
    """Test that verification catches problems."""
    from models import Page
    from lib.verify import verify_content_completeness

    page = Page(
        url="http://test.com",
        slug="test",
        title="Test",
        category="test",
    )

    # Simulate content loss
    page.raw_html = "<html><body>" + "word " * 100 + "</body></html>"
    page.markdown = "# Test\n\nOnly a few words"

    issues = verify_content_completeness(page)
    critical = [i for i in issues if i.severity == "critical"]

    assert len(critical) > 0
    assert any("content_loss" in i.issue_type for i in critical)


def test_pipeline_with_claude_phases(mocker, tmp_path):
    """Test complete pipeline with new Claude-powered phases."""
    import pytest
    pytest.importorskip('pytest_mock')

    from pipeline import run_pipeline
    from config import Config

    config = Config(
        output_dir=tmp_path / "output",
        state_dir=tmp_path / "state",
        base_url="https://docs.limacharlie.io",
        git_commit_changes=False,  # Disable git to avoid needing to mock detect
    )

    # Mock all external dependencies - patch in pipeline namespace
    mock_fetch_discover = mocker.patch('pipeline.fetch.discover_documentation_structure')
    mock_fetch_download = mocker.patch('pipeline.fetch.download_all_pages')

    from models import DocumentStructure, Page

    # Create mock structure
    mock_structure = DocumentStructure()
    test_page = Page(
        slug="test-page",
        title="Test",
        url="https://docs.limacharlie.io/docs/test-page",
        category="test",
        raw_html="<h1>Test</h1>"
    )
    mock_structure.categories["test"] = [test_page]

    mock_fetch_discover.return_value = mock_structure
    mock_fetch_download.return_value = 1

    # Mock ClaudeClient - need to patch where it's imported in pipeline
    mock_claude_instance = mocker.Mock()
    mock_claude_instance.is_available.return_value = True
    mock_claude_instance.check_required.return_value = None
    mock_claude_instance.run_subagent_prompt.return_value = '{"batches": []}'

    # Patch in both locations
    mocker.patch('lib.claude_client.ClaudeClient', return_value=mock_claude_instance)
    mocker.patch('pipeline.ClaudeClient', return_value=mock_claude_instance)

    # Mock batch creation - patch where it's imported
    mock_batches = [{
        'id': 'batch_01',
        'theme': 'Test',
        'pages': [test_page],
        'page_slugs': ['test-page']
    }]
    mocker.patch('pipeline.create_semantic_batches', return_value=mock_batches)

    # Mock understand phase - patch in pipeline namespace
    from lib.understand import ProcessedPage

    async def mock_async_process(*args, **kwargs):
        return {
            'batch_01': [ProcessedPage(
                slug="test-page",
                enhanced_markdown="# Test Page\n\nEnhanced content",
                extracted_apis=[],
                cross_refs=[],
                metadata={"summary": "Test"}
            )]
        }

    mocker.patch('pipeline.process_batches_parallel', side_effect=mock_async_process)

    # Mock synthesize phase - patch in pipeline namespace
    mocker.patch('pipeline.build_api_index', return_value="# API Index\n\nNo APIs")

    mocker.patch('pipeline.resolve_cross_references', return_value=[ProcessedPage(
        slug="test-page",
        enhanced_markdown="# Test Page\n\nEnhanced content",
        extracted_apis=[],
        cross_refs=[],
        metadata={"summary": "Test"}
    )])

    success = run_pipeline(config)

    assert success is True
    assert (tmp_path / "output" / "test-page.md").exists()
    output_content = (tmp_path / "output" / "test-page.md").read_text()
    assert "# Test Page" in output_content
