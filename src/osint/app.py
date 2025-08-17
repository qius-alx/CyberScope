# src/osint/app.py
import sys
from osint.cli import main as cli_main
from osint.core.logger import logger

def main():
    """Application entry point."""
    try:
        cli_main()
    except Exception as e:
        # This is a fallback for unhandled exceptions.
        # It's particularly useful for errors that might occur outside of the
        # main click command group, although click handles most things gracefully.
        logger.critical(f"An unexpected critical error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
