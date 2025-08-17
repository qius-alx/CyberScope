# Configuration

The OSINT Framework is configured through environment variables or a `.env` file in the root of the project.

## Core Settings

- `LOG_LEVEL`: The logging level (e.g., `DEBUG`, `INFO`). Default: `INFO`.
- `LOG_FILE`: Path to a file to write logs to. Default: `None`.
- `OUTPUT_DIR`: Directory to save exported results. Default: `results`.

## HTTP Settings

- `HTTP_TIMEOUT`: Request timeout in seconds. Default: `30`.
- `HTTP_RETRIES`: Number of retries for failed requests. Default: `3`.
- `HTTP_PROXY`: URL of an HTTP proxy to use.
- `TOR_PROXY`: URL of a SOCKS5 proxy for Tor. Default: `socks5h://localhost:9050`.

## API Keys

- `SHODAN_API_KEY`: Your API key for Shodan.
- `HIBP_API_KEY`: Your API key for Have I Been Pwned.
