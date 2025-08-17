# src/osint/modules/domain_dns.py
import click
import whois
import dns.resolver
import sys
from typing import List

from osint.core.logger import logger
from osint.ui.tables import print_table
from osint.core.validators import validate_domain

def get_whois_info(domain_name: str):
    """Performs a WHOIS lookup for the given domain."""
    logger.info(f"Performing WHOIS lookup for {domain_name}...")
    try:
        w = whois.whois(domain_name)
        if w and w.get('domain_name'):
            headers = ["Field", "Value"]
            rows = []
            # Use a sorted list of keys for consistent output
            for key in sorted(w.keys()):
                value = w[key]
                if value:
                    # Format lists and datetimes for clean printing
                    if isinstance(value, list):
                        display_value = "\n".join(str(v) for v in value)
                    else:
                        display_value = str(value)
                    rows.append([key.replace('_', ' ').title(), display_value])
            print_table(f"WHOIS Information for {domain_name}", headers, rows)
        else:
            logger.warning(f"No WHOIS data found for {domain_name}.")
    except Exception as e:
        logger.error(f"WHOIS lookup failed for {domain_name}: {e}")

def get_dns_records(domain_name: str):
    """Performs DNS lookups for common record types."""
    logger.info(f"Querying DNS records for {domain_name}...")
    record_types = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'CNAME', 'SOA']
    results = []
    for record_type in record_types:
        try:
            answers = dns.resolver.resolve(domain_name, record_type)
            for rdata in answers:
                results.append([record_type, rdata.to_text()])
        except dns.resolver.NoAnswer:
            logger.debug(f"No {record_type} records found for {domain_name}.")
        except dns.resolver.NXDOMAIN:
            logger.error(f"Domain {domain_name} does not exist (NXDOMAIN).")
            return
        except Exception as e:
            logger.warning(f"Could not retrieve {record_type} records for {domain_name}: {e}")

    if results:
        headers = ["Record Type", "Value"]
        print_table(f"DNS Records for {domain_name}", headers, results)
    else:
        logger.warning(f"No DNS records found for {domain_name}")

@click.command('domain')
@click.option('--name', required=True, help='The domain to investigate.')
@click.option('--whois', 'run_whois', is_flag=True, help='Perform a WHOIS lookup.')
@click.option('--dns', 'run_dns', is_flag=True, help='Perform a DNS lookup.')
def domain_cmd(name, run_whois, run_dns):
    """Investigates a domain for WHOIS and DNS information."""
    if not validate_domain(name):
        logger.error(f"'{name}' is not a valid domain name.")
        sys.exit(1)

    logger.info(f"Starting domain investigation for: {name}")

    if not any([run_whois, run_dns]):
        # If no flags are specified, run all checks by default
        run_whois = True
        run_dns = True

    if run_whois:
        get_whois_info(name)

    if run_dns:
        get_dns_records(name)
