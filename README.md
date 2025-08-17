# OSINT Framework

An extensible OSINT framework for security researchers, built in Python.

![Banner](https://placeholder.com/wp-content/uploads/2018/10/placeholder.com-logo1.png) <!-- Placeholder for a screenshot -->

## Features

- **Modular Architecture**: Easily extend the framework with new modules.
- **CLI Interface**: A user-friendly command-line interface powered by Click.
- **Rich Output**: Beautiful and clear output in the console using Rich.
- **Multiple Export Formats**: Export results to JSON, CSV, and PDF.
- **And much more...**

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/user/osint-framework.git
    cd osint-framework
    ```

2.  Install dependencies:
    ```bash
    make install
    ```

## Usage

The base command is `osint`. You can see all available commands by running `osint --help`.
Each module is available as a subcommand.

### Domain Investigation
Investigate a domain for WHOIS and DNS information.
```bash
# Run all domain checks
osint domain --name example.com

# Run only WHOIS lookup
osint domain --name example.com --whois

# Run only DNS lookup and export to JSON
osint domain --name example.com --dns --export json
```

### IP Investigation
Investigate an IP address for ASN, geolocation, and open ports.
```bash
# Run ASN and Geolocation lookups
osint ip --address 8.8.8.8

# Scan a range of ports
osint ip --address 8.8.8.8 --ports 80-1024
```

### Web Scraping
Scrape a URL for information and check for historical archives.
```bash
# Scrape a page for emails, phones, links, etc.
osint web --url https://example.com --scrape

# Check for Wayback Machine archives
osint web --url https://example.com --wayback
```

### Email Investigation
Investigate an email address for associated DNS records and data breaches.
```bash
# Check DNS and HIBP (requires HIBP_API_KEY in .env)
osint email --address test@example.com
```

### Shodan Search
Search Shodan for devices and services (requires SHODAN_API_KEY in .env).
```bash
osint shodan --query "apache country:US" --limit 50
```

### File Analysis
Analyze local files for metadata and hashes.
```bash
# Analyze a single file
osint files --path ./my_image.jpg --exif --hash

# Analyze all files in a directory
osint files --path ./my_documents/
```

## Configuration

Configuration is handled via a `.env` file. Copy the `.env.example` to `.env` and fill in your API keys and custom settings.

```bash
cp .env.example .env
```

See `CONFIG.md` for more details on configuration options.

## Contributing

Contributions are welcome! Please read `CONTRIBUTING.md` for details on how to submit pull requests.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
