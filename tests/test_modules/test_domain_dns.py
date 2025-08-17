# tests/test_modules/test_domain_dns.py
import pytest
from click.testing import CliRunner
from osint.cli import cli

@pytest.fixture
def runner():
    return CliRunner()

def test_domain_cmd_no_options(runner, mocker):
    """Test the domain command with no investigation flags, which should run all checks."""
    mock_whois = mocker.patch('osint.modules.domain_dns.whois.whois')
    mock_whois.return_value = {'domain_name': 'EXAMPLE.COM'}
    mocker.patch('osint.modules.domain_dns.dns.resolver.resolve', return_value=[])

    result = runner.invoke(cli, ['domain', '--name', 'example.com'])
    assert result.exit_code == 0
    assert "Performing WHOIS lookup" in result.output
    assert "Querying DNS records" in result.output

def test_domain_cmd_invalid_domain(runner):
    """Test the domain command with an invalid domain."""
    result = runner.invoke(cli, ['domain', '--name', 'not-a-valid-domain', '--whois'])
    assert result.exit_code == 1 # sys.exit(1) is called
    assert "'not-a-valid-domain' is not a valid domain name." in result.output

def test_domain_cmd_whois(runner, mocker):
    """Test the domain --whois flag."""
    # Mock the external call to whois.whois
    mock_whois = mocker.patch('osint.modules.domain_dns.whois.whois')
    mock_whois.return_value = {
        'domain_name': 'EXAMPLE.COM',
        'registrar': 'Example Registrar',
        'creation_date': '2022-01-01',
    }
    # Mock the dns resolver to ensure it's not called
    mock_resolve = mocker.patch('osint.modules.domain_dns.dns.resolver.resolve')

    result = runner.invoke(cli, ['domain', '--name', 'example.com', '--whois'])

    assert result.exit_code == 0
    mock_whois.assert_called_once_with('example.com')
    mock_resolve.assert_not_called()
    assert "WHOIS Information for example.com" in result.output
    assert "Example Registrar" in result.output

def test_domain_cmd_dns(runner, mocker):
    """Test the domain --dns flag."""
    # Mock the whois call to ensure it's not called
    mock_whois = mocker.patch('osint.modules.domain_dns.whois.whois')
    # Mock the external call to dns.resolver.resolve
    mock_resolve = mocker.patch('osint.modules.domain_dns.dns.resolver.resolve')

    # Create a mock response for A records
    mock_a_record = mocker.MagicMock()
    mock_a_record.to_text.return_value = "93.184.216.34"
    mock_resolve.return_value = [mock_a_record]

    result = runner.invoke(cli, ['domain', '--name', 'example.com', '--dns'])

    assert result.exit_code == 0
    mock_resolve.assert_called_with('example.com', 'A') # At least with 'A'
    mock_whois.assert_not_called()
    assert "DNS Records for example.com" in result.output
    assert "93.184.216.34" in result.output

def test_domain_cmd_all_checks(runner, mocker):
    """Test the domain command with both --whois and --dns flags."""
    mock_whois = mocker.patch('osint.modules.domain_dns.whois.whois')
    mock_whois.return_value = {'domain_name': 'EXAMPLE.COM', 'registrar': 'Test Registrar'}

    mock_resolve = mocker.patch('osint.modules.domain_dns.dns.resolver.resolve')
    mock_a_record = mocker.MagicMock()
    mock_a_record.to_text.return_value = "1.2.3.4"
    mock_resolve.return_value = [mock_a_record]

    result = runner.invoke(cli, ['domain', '--name', 'example.com', '--whois', '--dns'])

    assert result.exit_code == 0
    assert "WHOIS Information for example.com" in result.output
    assert "Test Registrar" in result.output
    assert "DNS Records for example.com" in result.output
    assert "1.2.3.4" in result.output
