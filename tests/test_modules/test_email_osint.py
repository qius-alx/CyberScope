# tests/test_modules/test_email_osint.py
import pytest
from click.testing import CliRunner
from osint.cli import cli
from osint.core.config import settings

@pytest.fixture
def runner():
    return CliRunner()

def test_email_cmd_dns(runner, mocker):
    """Test the email --dns flag."""
    mock_resolve = mocker.patch('osint.modules.email_osint.dns.resolver.resolve')

    mock_mx = mocker.MagicMock()
    mock_mx.preference = 10
    mock_mx.exchange.to_text.return_value = "mail.example.com."

    mock_txt = mocker.MagicMock()
    mock_txt.to_text.return_value = '"v=spf1 include:_spf.google.com ~all"'

    def resolve_side_effect(domain, record_type):
        if record_type == 'MX':
            return [mock_mx]
        if record_type == 'TXT':
            return [mock_txt]
        return []

    mock_resolve.side_effect = resolve_side_effect

    result = runner.invoke(cli, ['email', '--address', 'test@example.com', '--dns'])
    assert result.exit_code == 0
    assert "DNS Mail Records for example.com" in result.output
    assert "mail.example.com" in result.output
    assert "v=spf1" in result.output

def test_email_cmd_hibp_found(runner, mocker):
    """Test the email --hibp flag when breaches are found."""
    settings.hibp_api_key = "fake_key" # Set a fake key for the test
    mock_http_get = mocker.patch('osint.modules.email_osint.http_client.session.get')

    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {'Name': 'TestBreach', 'Domain': 'test.com', 'BreachDate': '2022-01-01', 'Description': 'A test breach.'}
    ]
    mock_http_get.return_value = mock_response

    result = runner.invoke(cli, ['email', '--address', 'test@example.com', '--hibp'])
    assert result.exit_code == 0
    assert "Breaches Found for test@example.com" in result.output
    assert "TestBreach" in result.output

def test_email_cmd_hibp_not_found(runner, mocker):
    """Test the email --hibp flag when no breaches are found (404)."""
    settings.hibp_api_key = "fake_key"
    mock_get = mocker.patch('osint.modules.email_osint.http_client.session.get')

    # Simulate a 404 response
    mock_response = mocker.MagicMock()
    mock_response.status_code = 404
    exception = Exception("404 Client Error")
    exception.response = mock_response
    mock_get.side_effect = exception

    result = runner.invoke(cli, ['email', '--address', 'safe@example.com', '--hibp'])
    assert result.exit_code == 0
    assert "Good news! No breaches found" in result.output

def test_email_cmd_hibp_no_key(runner):
    """Test the email --hibp flag when no API key is set."""
    settings.hibp_api_key = None # Ensure key is not set
    result = runner.invoke(cli, ['email', '--address', 'test@example.com', '--hibp'])
    assert result.exit_code == 0
    assert "HIBP check requires an API key" in result.output

def test_email_cmd_invalid_email(runner):
    """Test providing an invalid email address."""
    result = runner.invoke(cli, ['email', '--address', 'not-an-email'])
    assert result.exit_code == 1
    assert "'not-an-email' is not a valid email address." in result.output
