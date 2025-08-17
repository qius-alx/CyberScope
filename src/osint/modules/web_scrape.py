# src/osint/modules/web_scrape.py
import click
import re
import sys
from bs4 import BeautifulSoup
import waybackpy
from urllib.parse import urlparse

from osint.core.logger import logger
from osint.ui.tables import print_table
from osint.core.http import http_client # Using our custom http client

# Regex for finding emails
EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
# Regex for finding phone numbers (very basic, can be improved)
PHONE_REGEX = r"(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"

def scrape_page(url: str):
    """Scrapes a webpage for title, meta tags, links, emails, and phones."""
    logger.info(f"Scraping {url}...")
    try:
        response = http_client.get(url)
        soup = BeautifulSoup(response.content, 'lxml')

        # --- Basic Info ---
        title = soup.title.string.strip() if soup.title and soup.title.string else "No title found"
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'].strip() if meta_desc and meta_desc.get('content') else "No description found"

        info_headers = ["Key", "Value"]
        info_rows = [["Title", title], ["Meta Description", description]]
        print_table(f"Basic Info for {url}", info_headers, info_rows)

        # --- Find Emails and Phones ---
        text = soup.get_text()
        emails = re.findall(EMAIL_REGEX, text)
        phones = re.findall(PHONE_REGEX, text)

        if emails:
            print_table("Emails Found", ["Email"], [[email] for email in sorted(list(set(emails)))])
        if phones:
            print_table("Phone Numbers Found", ["Phone"], [[phone] for phone in sorted(list(set(phones)))])

        # --- Find Links ---
        links = []
        parsed_url = urlparse(url)
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http'):
                link_domain = urlparse(href).netloc
                if link_domain != parsed_url.netloc:
                    links.append(["External", href])
            elif not href.startswith(('#', 'mailto:', 'tel:')):
                links.append(["Internal", href])

        if links:
            print_table("Links Found", ["Type", "URL"], links[:20]) # Limit to first 20 links
            if len(links) > 20:
                logger.info(f"Found {len(links)} links in total. Displaying first 20.")

    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")

def check_wayback(url: str):
    """Checks the Wayback Machine for archives of the given URL."""
    logger.info(f"Checking Wayback Machine for {url}...")
    try:
        user_agent = http_client.session.headers.get("User-Agent", "osint-framework")
        cdx = waybackpy.Cdx(url, user_agent=user_agent)
        oldest = cdx.oldest()
        newest = cdx.newest()

        if oldest and oldest.archive_url:
            headers = ["Archive Type", "Timestamp", "URL"]
            rows = [
                ["Oldest", oldest.timestamp, oldest.archive_url],
                ["Newest", newest.timestamp, newest.archive_url],
            ]
            print_table(f"Wayback Machine Archives for {url}", headers, rows)
        else:
            logger.warning(f"No archives found for {url} on the Wayback Machine.")

    except Exception as e:
        logger.error(f"Wayback Machine lookup failed for {url}: {e}")


@click.command('web')
@click.option('--url', required=True, help='The URL to investigate.')
@click.option('--scrape', 'run_scrape', is_flag=True, help='Scrape the page for info, emails, phones, and links.')
@click.option('--wayback', 'run_wayback', is_flag=True, help='Check for Wayback Machine archives.')
def web_cmd(url, run_scrape, run_wayback):
    """Investigates a web URL."""
    if not (url.startswith('http://') or url.startswith('https://')):
        logger.error("Invalid URL format. Please provide a full URL (e.g., 'https://example.com').")
        sys.exit(1)

    logger.info(f"Starting web investigation for: {url}")

    if not any([run_scrape, run_wayback]):
        run_scrape = True
        run_wayback = True

    if run_scrape:
        scrape_page(url)

    if run_wayback:
        check_wayback(url)
