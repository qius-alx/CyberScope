# src/osint/cli.py
import click
import os
import logging

from osint.core.config import settings
from osint.core.logger import configure_logger
from osint.ui.banner import print_banner

# Import module commands
from osint.modules.domain_dns import domain_cmd

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
@click.option('--cache/--no-cache', 'use_cache', default=True, help='Enable/disable HTTP caching.')
@click.pass_context
def cli(ctx, log_level, log_file, timeout, retries, proxy, tor, threads, no_color, output_dir, use_cache):
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


# Register module commands
cli.add_command(domain_cmd)


def main():
    cli(obj={}) # obj={} is required by click

if __name__ == "__main__":
    main()
