# src/osint/modules/shodan_ext.py
import click
import shodan
import sys

from osint.core.logger import logger
from osint.ui.tables import print_table
from osint.core.config import settings

def search_shodan(query: str, limit: int):
    """Searches Shodan for the given query."""
    # The settings object is now loaded with the .env file content
    if not settings.shodan_api_key:
        logger.warning("Shodan search requires an API key. Set SHODAN_API_KEY in your .env file.")
        return

    logger.info(f"Querying Shodan for: '{query}' (limit: {limit})")

    try:
        api = shodan.Shodan(settings.shodan_api_key)
        results = api.search(query, limit=limit)

        if not results.get('matches'):
            logger.info("No results found on Shodan for this query.")
            return

        logger.info(f"Total results found: {results.get('total')}")

        headers = ["IP Address", "Port", "Hostnames", "Organization", "Location"]
        rows = []
        for match in results['matches']:
            location_info = match.get('location', {})
            city = location_info.get('city', 'N/A')
            country = location_info.get('country_name', 'N/A')

            rows.append([
                match.get('ip_str', 'N/A'),
                str(match.get('port', 'N/A')),
                ", ".join(match.get('hostnames', []) if match.get('hostnames') else ['N/A']),
                match.get('org', 'N/A'),
                f"{city}, {country}"
            ])

        print_table(f"Shodan Results for '{query}'", headers, rows)

    except shodan.APIError as e:
        logger.error(f"Shodan API error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during Shodan search: {e}")


@click.command('shodan')
@click.option('--query', required=True, help="The search query for Shodan (e.g., 'apache country:US').")
@click.option('--limit', default=100, type=click.IntRange(1, 1000), help="The number of results to return (default: 100).")
def shodan_cmd(query, limit):
    """Search Shodan for devices and services."""
    search_shodan(query, limit)
