# tests/test_modules/test_web_scrape.py
import pytest
from click.testing import CliRunner
from osint.cli import cli

@pytest.fixture
def runner():
    return CliRunner()

def test_web_cmd_scrape(runner, mocker):
    """Test the web --scrape flag."""
    mock_http_get = mocker.patch('osint.core.http.http_client.get')

    # Mock the response object
    mock_response = mocker.MagicMock()
    mock_response.content = b'<html><head><title>Test Page</title><meta name="description" content="A test."></head><body><p>Email: test@example.com, Phone: (123) 456-7890</p><a href="/internal">Internal</a><a href="https://othersite.com">External</a></body></html>'
    mock_http_get.return_value = mock_response

    result = runner.invoke(cli, ['web', '--url', 'https://example.com', '--scrape'])
    assert result.exit_code == 0
    assert "Basic Info for https://example.com" in result.output
    assert "Test Page" in result.output
    assert "A test." in result.output
    assert "Emails Found" in result.output
    assert "test@example.com" in result.output
    assert "Phone Numbers Found" in result.output
    assert "(123) 456-7890" in result.output
    assert "Links Found" in result.output
    assert "Internal" in result.output
    assert "External" in result.output

def test_web_cmd_wayback(runner, mocker):
    """Test the web --wayback flag."""
    mock_cdx = mocker.patch('osint.modules.web_scrape.waybackpy.Cdx')
    mock_cdx_instance = mock_cdx.return_value

    # Mock the oldest() and newest() methods
    mock_oldest = mocker.MagicMock()
    mock_oldest.timestamp = "20000101000000"
    mock_oldest.archive_url = "http://web.archive.org/web/2000/example.com"
    mock_cdx_instance.oldest.return_value = mock_oldest

    mock_newest = mocker.MagicMock()
    mock_newest.timestamp = "20230101000000"
    mock_newest.archive_url = "http://web.archive.org/web/2023/example.com"
    mock_cdx_instance.newest.return_value = mock_newest

    result = runner.invoke(cli, ['web', '--url', 'https://example.com', '--wayback'])
    assert result.exit_code == 0
    assert "Wayback Machine Archives for https://example.com" in result.output
    assert "Oldest" in result.output
    assert "20000101000000" in result.output
    assert "Newest" in result.output
    assert "20230101000000" in result.output

def test_web_cmd_invalid_url(runner):
    """Test providing an invalid URL."""
    result = runner.invoke(cli, ['web', '--url', 'not-a-url'])
    assert result.exit_code == 1
    assert "Invalid URL format" in result.output
