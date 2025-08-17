# src/osint/modules/ip_network.py
import click
import sys
import socket
from ipwhois import IPWhois
from ipwhois.exceptions import IPDefinedError

from osint.core.logger import logger
from osint.ui.tables import print_table
from osint.core.validators import validate_ip

def get_ip_info(ip_address: str, run_asn: bool, run_geo: bool):
    """
    Retrieves ASN and Geolocation info for an IP address.
    """
    logger.info(f"Performing WHOIS lookup for {ip_address}...")
    try:
        obj = IPWhois(ip_address)
        results = obj.lookup_whois()

        if run_asn:
            asn_data = results.get('asn_description')
            if asn_data:
                asn_headers = ["ASN", "Description", "Country Code", "Registry"]
                asn_rows = [[
                    results.get('asn'),
                    asn_data,
                    results.get('asn_country_code'),
                    results.get('asn_registry')
                ]]
                print_table(f"ASN Information for {ip_address}", asn_headers, asn_rows)
            else:
                logger.warning(f"No ASN data found for {ip_address}.")

        if run_geo:
            nets = results.get('nets', [{}])[0]
            if nets.get('city') or nets.get('country'):
                geo_headers = ["Key", "Value"]
                geo_rows = [
                    ["Address", nets.get('address')],
                    ["City", nets.get('city')],
                    ["State", nets.get('state')],
                    ["Country", nets.get('country')],
                    ["Postal Code", nets.get('postal_code')],
                ]
                # Filter out rows with no value
                geo_rows = [row for row in geo_rows if row[1]]
                print_table(f"Geolocation Information for {ip_address}", geo_headers, geo_rows)
            else:
                logger.warning(f"No Geolocation data found for {ip_address}.")

    except IPDefinedError:
        logger.error(f"'{ip_address}' is a private, reserved, or otherwise undefined IP address.")
    except Exception as e:
        logger.error(f"Could not retrieve WHOIS information for {ip_address}: {e}")

def scan_ports(ip_address: str, port_range_str: str):
    """
    Scans a range of ports on the given IP address.
    port_range_str should be in the format 'start-end'.
    """
    logger.info(f"Scanning ports on {ip_address} in range {port_range_str}...")
    try:
        start_port, end_port = map(int, port_range_str.split('-'))
        if not (0 < start_port <= 65535 and 0 < end_port <= 65535 and start_port <= end_port):
            raise ValueError("Port numbers out of valid range (1-65535).")
    except ValueError as e:
        logger.error(f"Invalid port range: {e}. Please use 'start-end' (e.g., '80-1024').")
        return

    open_ports = []
    for port in range(start_port, end_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5) # Set a timeout to avoid long waits
        result = sock.connect_ex((ip_address, port))
        if result == 0:
            open_ports.append([port, "Open"])
        sock.close()

    if open_ports:
        headers = ["Port", "State"]
        print_table(f"Open Ports on {ip_address}", headers, open_ports)
    else:
        logger.info(f"No open ports found in the range {port_range_str} on {ip_address}.")


@click.command('ip')
@click.option('--address', required=True, help='The IP address to investigate.')
@click.option('--asn', 'run_asn', is_flag=True, help='Perform an ASN lookup.')
@click.option('--geo', 'run_geo', is_flag=True, help='Perform a geolocation lookup.')
@click.option('--ports', 'port_range', help="Scan a port range (e.g., '20-1024').")
def ip_cmd(address, run_asn, run_geo, port_range):
    """Investigates an IP address."""
    if not validate_ip(address):
        logger.error(f"'{address}' is not a valid IP address.")
        sys.exit(1)

    logger.info(f"Starting investigation for IP: {address}")

    if not any([run_asn, run_geo, port_range]):
        run_asn = True
        run_geo = True

    if run_asn or run_geo:
        get_ip_info(address, run_asn, run_geo)

    if port_range:
        scan_ports(address, port_range)
