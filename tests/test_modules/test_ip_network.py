# tests/test_modules/test_ip_network.py
import pytest
from click.testing import CliRunner
from osint.cli import cli

@pytest.fixture
def runner():
    return CliRunner()

def test_ip_cmd_asn_and_geo(runner, mocker):
    """Test the ip command with --asn and --geo flags."""
    mock_ipwhois = mocker.patch('osint.modules.ip_network.IPWhois')
    mock_instance = mock_ipwhois.return_value
    mock_instance.lookup_whois.return_value = {
        'asn': '15169',
        'asn_description': 'GOOGLE',
        'asn_country_code': 'US',
        'asn_registry': 'arin',
        'nets': [{'city': 'Mountain View', 'country': 'US', 'address': '1600 Amphitheatre Parkway'}]
    }

    result = runner.invoke(cli, ['ip', '--address', '8.8.8.8', '--asn', '--geo'])
    assert result.exit_code == 0
    assert "ASN Information for 8.8.8.8" in result.output
    assert "GOOGLE" in result.output
    assert "Geolocation Information for 8.8.8.8" in result.output
    assert "Mountain View" in result.output
    assert "1600 Amphitheatre Parkway" in result.output

def test_ip_cmd_ports(runner, mocker):
    """Test the ip command with the --ports flag."""
    mock_socket = mocker.patch('osint.modules.ip_network.socket.socket')
    mock_socket_instance = mock_socket.return_value
    # Simulate port 80 is open, all others are closed
    mock_socket_instance.connect_ex.side_effect = lambda addr: 0 if addr[1] == 80 else 1

    result = runner.invoke(cli, ['ip', '--address', '1.1.1.1', '--ports', '79-81'])
    assert result.exit_code == 0
    assert "Open Ports on 1.1.1.1" in result.output
    assert "80" in result.output
    assert "Open" in result.output
    assert "79" not in result.output
    assert "81" not in result.output

def test_ip_cmd_private_ip(runner, mocker):
    """Test that private IPs are handled gracefully."""
    mock_ipwhois = mocker.patch('osint.modules.ip_network.IPWhois')
    # ipwhois raises IPDefinedError for private addresses
    mock_ipwhois.side_effect = mocker.patch('osint.modules.ip_network.IPDefinedError')

    result = runner.invoke(cli, ['ip', '--address', '192.168.1.1', '--asn'])
    assert result.exit_code == 0
    assert "'192.168.1.1' is a private, reserved, or otherwise undefined IP address." in result.output

def test_ip_cmd_invalid_ip(runner):
    """Test providing an invalid IP address."""
    result = runner.invoke(cli, ['ip', '--address', '999.999.999.999'])
    assert result.exit_code == 1
    assert "'999.999.999.999' is not a valid IP address." in result.output
