# src/osint/modules/email_osint.py
import click
import sys
import dns.resolver

from osint.core.logger import logger
from osint.ui.tables import print_table
from osint.core.http import http_client
from osint.core.validators import validate_email
from osint.core.config import settings

def check_email_dns(email_address: str):
    """Looks up MX and SPF records for the email's domain."""
    domain = email_address.split('@')[1]
    logger.info(f"Querying DNS records for domain: {domain}")

    results = []
    # MX Records
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        for record in sorted(mx_records, key=lambda r: r.preference):
            results.append(["MX", f"Preference: {record.preference}, Mail Server: {record.exchange.to_text()}"])
    except Exception as e:
        logger.warning(f"Could not retrieve MX records for {domain}: {e}")

    # SPF (in TXT records)
    try:
        txt_records = dns.resolver.resolve(domain, 'TXT')
        spf_found = False
        for record in txt_records:
            record_text = record.to_text().strip('"')
            if 'v=spf1' in record_text.lower():
                results.append(["SPF", record_text])
                spf_found = True
        if not spf_found:
            logger.debug(f"No SPF record found for {domain}.")
    except Exception as e:
        logger.warning(f"Could not retrieve TXT/SPF records for {domain}: {e}")

    if results:
        print_table(f"DNS Mail Records for {domain}", ["Record Type", "Value"], results)

def check_hibp(email_address: str):
    """Checks the email address against the Have I Been Pwned database."""
    if not settings.hibp_api_key:
        logger.warning("HIBP check requires an API key. Set HIBP_API_KEY in your .env file.")
        return

    logger.info(f"Checking {email_address} against HIBP database...")
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email_address}"
    headers = {
        "hibp-api-key": settings.hibp_api_key,
        "User-Agent": http_client.session.headers.get("User-Agent", "osint-framework")
    }

    try:
        # We don't want to use the global cache for this, as results can change
        response = http_client.session.get(url, headers=headers, timeout=settings.http_timeout)
        response.raise_for_status()
        breaches = response.json()
        headers = ["Breach Name", "Domain", "Breach Date", "Description"]
        rows = [[b.get('Name'), b.get('Domain'), b.get('BreachDate'), b.get('Description')] for b in breaches]
        print_table(f"Breaches Found for {email_address}", headers, rows)
    except Exception as e:
        if hasattr(e, 'response') and e.response.status_code == 404:
             logger.info(f"Good news! No breaches found for {email_address} in HIBP database.")
        else:
            logger.error(f"Failed to check HIBP for {email_address}: {e}")


@click.command('email')
@click.option('--address', required=True, help='The email address to investigate.')
@click.option('--dns', 'run_dns', is_flag=True, help='Check mail-related DNS records (MX, SPF).')
@click.option('--hibp', 'run_hibp', is_flag=True, help='Check for breaches in Have I Been Pwned.')
def email_cmd(address, run_dns, run_hibp):
    """Investigates an email address."""
    if not validate_email(address):
        logger.error(f"'{address}' is not a valid email address.")
        sys.exit(1)

    logger.info(f"Starting investigation for email: {address}")

    if not any([run_dns, run_hibp]):
        run_dns = True
        run_hibp = True

    if run_dns:
        check_email_dns(address)

    if run_hibp:
        check_hibp(address)
