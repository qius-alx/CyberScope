# src/osint/modules/social_media.py
import click
import json
from pathlib import Path

from osint.core.logger import logger
from osint.ui.tables import print_table
from osint.core.http import http_client
from osint.core.concurrency import run_concurrently

# Path to the data file
SITES_DATA_PATH = Path(__file__).parent.parent / "data" / "sites.json"

def load_sites_data():
    """Loads the site data from the JSON file."""
    try:
        with open(SITES_DATA_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Site data file not found at: {SITES_DATA_PATH}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from: {SITES_DATA_PATH}")
        return {}

def check_username(site_info):
    """
    Checks for a username's existence on a single site.
    This function is designed to be run concurrently.

    Args:
        site_info (tuple): A tuple containing (site_name, site_data, username).

    Returns:
        A list [site_name, url] if the user is found, otherwise None.
    """
    site_name, site_data, username = site_info
    url = site_data['url'].format(username)
    error_type = site_data['error_type']
    error_msg = site_data.get('error_msg')

    try:
        # Use a new session for each thread to avoid issues, or use the global one carefully
        # For this use case, the global client should be thread-safe as requests sessions are.
        response = http_client.get(url, allow_redirects=True)

        if error_type == 'status_code':
            if response.status_code == 200:
                logger.debug(f"Found {username} on {site_name}")
                return [site_name, url]
        elif error_type == 'message':
            if response.status_code == 200 and error_msg not in response.text:
                logger.debug(f"Found {username} on {site_name}")
                return [site_name, url]

    except Exception as e:
        logger.debug(f"Error checking {site_name} for {username}: {e}")

    return None


@click.command('social')
@click.option('--username', required=True, help="The username to check across platforms.")
@click.option('--platforms', help="A comma-separated list of platforms to check (e.g., 'GitHub,Twitter'). If not provided, all platforms are checked.")
def social_cmd(username, platforms):
    """Checks for a username's existence across social media platforms."""
    logger.info(f"Starting social media check for username: {username}")

    sites_data = load_sites_data()
    if not sites_data:
        return

    if platforms:
        platform_list = [p.strip() for p in platforms.split(',')]
        sites_to_check = {p: sites_data[p] for p in platform_list if p in sites_data}
        if not sites_to_check:
            logger.error(f"None of the specified platforms are supported. Supported platforms: {list(sites_data.keys())}")
            return
    else:
        sites_to_check = sites_data

    tasks = [(site, data, username) for site, data in sites_to_check.items()]

    results = run_concurrently(check_username, tasks, task_description=f"Checking {len(tasks)} platforms...")

    if results:
        # Sort results alphabetically by platform name
        sorted_results = sorted(results, key=lambda x: x[0])
        headers = ["Platform", "Profile URL"]
        print_table(f"Accounts Found for '{username}'", headers, sorted_results)
    else:
        logger.info(f"No accounts found for username '{username}' on the checked platforms.")
