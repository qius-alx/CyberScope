# tests/test_modules/test_shodan_ext.py
import pytest
from click.testing import CliRunner
from osint.cli import cli
from osint.core.config import settings
import shodan

@pytest.fixture
def runner():
    return CliRunner()

def test_shodan_cmd_success(runner, mocker):
    """Test the shodan command on a successful query."""
    settings.shodan_api_key = "fake_key"
    mock_shodan_api = mocker.patch('osint.modules.shodan_ext.shodan.Shodan')
    mock_api_instance = mock_shodan_api.return_value
    mock_api_instance.search.return_value = {
        'total': 1,
        'matches': [{
            'ip_str': '1.1.1.1',
            'port': 80,
            'hostnames': ['one.one.one.one'],
            'org': 'Cloudflare, Inc.',
            'location': {'city': 'San Francisco', 'country_name': 'United States'}
        }]
    }

    result = runner.invoke(cli, ['shodan', '--query', 'cloudflare', '--limit', '1'])
    assert result.exit_code == 0
    assert "Shodan Results for 'cloudflare'" in result.output
    assert "1.1.1.1" in result.output
    assert "Cloudflare, Inc." in result.output

def test_shodan_cmd_no_results(runner, mocker):
    """Test the shodan command when no results are found."""
    settings.shodan_api_key = "fake_key"
    mock_shodan_api = mocker.patch('osint.modules.shodan_ext.shodan.Shodan')
    mock_api_instance = mock_shodan_api.return_value
    mock_api_instance.search.return_value = {'total': 0, 'matches': []}

    result = runner.invoke(cli, ['shodan', '--query', 'a_query_with_no_results'])
    assert result.exit_code == 0
    assert "No results found on Shodan for this query" in result.output

def test_shodan_cmd_api_error(runner, mocker):
    """Test the shodan command when the API returns an error."""
    settings.shodan_api_key = "fake_key"
    mock_shodan_api = mocker.patch('osint.modules.shodan_ext.shodan.Shodan')
    mock_api_instance = mock_shodan_api.return_value
    mock_api_instance.search.side_effect = shodan.APIError("Invalid API key")

    result = runner.invoke(cli, ['shodan', '--query', 'test'])
    assert result.exit_code == 0
    assert "Shodan API error: Invalid API key" in result.output

def test_shodan_cmd_no_key(runner):
    """Test the shodan command when no API key is configured."""
    settings.shodan_api_key = None
    result = runner.invoke(cli, ['shodan', '--query', 'test'])
    assert result.exit_code == 0
    assert "Shodan search requires an API key" in result.output
