# src/osint/cli.py
import click
import os
import logging

from osint.core.config import settings
from osint.core.logger import configure_logger, logger
from osint.ui.banner import print_banner
from osint.core import exporters

# Import module commands
from osint.modules.domain_dns import domain_cmd
from osint.modules.ip_network import ip_cmd
from osint.modules.web_scrape import web_cmd
from osint.modules.email_osint import email_cmd
from osint.modules.shodan_ext import shodan_cmd
from osint.modules.social_media import social_cmd
from osint.modules.files_meta import files_cmd

@click.group()
@click.option('--log-level', default=None, help=f'Set logging level (e.g., DEBUG, INFO).', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], case_sensitive=False))
@click.option('--log-file', default=None, help='Log output to a file.')
@click.option('--timeout', default=None, type=int, help=f'HTTP request timeout.')
@click.option('--retries', default=None, type=int, help=f'Number of HTTP request retries.')
@click.option('--proxy', default=None, help='Proxy to use for HTTP requests.')
@click.option('--tor', is_flag=True, default=False, help='Use Tor proxy for requests.')
@click.option('--threads', default=None, type=int, help=f'Number of threads for concurrent tasks.')
@click.option('--no-color', is_flag=True, default=False, help='Disable color output.')
@click.option('--output-dir', default=None, help=f'Directory to save output files.')
@click.option('--export', 'export_formats', multiple=True, type=click.Choice(['json', 'csv', 'txt', 'pdf'], case_sensitive=False), help="Export results to one or more formats.")
@click.option('--cache/--no-cache', 'use_cache', default=True, help='Enable/disable HTTP caching.')
@click.pass_context
def cli(ctx, log_level, log_file, timeout, retries, proxy, tor, threads, no_color, output_dir, use_cache, export_formats):
    """
    An extensible OSINT framework for security researchers.
    """
    print_banner()

    # Update settings from CLI options, only if they are provided
    if log_level:
        settings.log_level = log_level
    if log_file:
        settings.log_file = log_file
    if timeout:
        settings.http_timeout = timeout
    if retries:
        settings.http_retries = retries
    if proxy:
        settings.http_proxy = proxy
    if threads:
        settings.threads = threads
    if output_dir:
        settings.output_dir = output_dir

    if no_color:
        os.environ["NO_COLOR"] = "1"

    # Configure the logger with the potentially updated settings
    configure_logger()
    logger = logging.getLogger("osint_framework")

    # Create a context object to pass to subcommands
    # This context will be used to initialize the http_client with the right options
    ctx.obj = {
        'use_tor': tor,
        'use_cache': use_cache,
    }

    logger.info("OSINT Framework initialized.")
    logger.debug(f"Settings loaded: {settings.dict()}")
    logger.debug(f"CLI Context: {ctx.obj}")

    # Register the exporters to run at the end of the command
    ctx.call_on_close(lambda: run_exporters(export_formats))


def run_exporters(formats):
    """Callback function to run selected exporters."""
    if not formats:
        return

    logger.info(f"Exporting results to: {', '.join(formats)}")
    if 'json' in formats:
        exporters.export_json()
    if 'csv' in formats:
        exporters.export_csv()
    if 'txt' in formats:
        exporters.export_txt()
    if 'pdf' in formats:
        exporters.export_pdf()


# Register module commands
cli.add_command(domain_cmd)
cli.add_command(ip_cmd)
cli.add_command(web_cmd)
cli.add_command(email_cmd)
cli.add_command(shodan_cmd)
cli.add_command(social_cmd)
cli.add_command(files_cmd)


def main():
    cli(obj={}) # obj={} is required by click

if __name__ == "__main__":
    main()
