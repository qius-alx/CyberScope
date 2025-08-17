# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.2.0] - 2023-10-28

### Added
- **IP & Network Module**: `ip` command for ASN, geolocation, and port scanning.
- **Web & Scraping Module**: `web` command for scraping pages and checking Wayback Machine.
- **Email OSINT Module**: `email` command for DNS checks and HIBP breach lookups.
- **Shodan Module**: `shodan` command to query the Shodan API.
- **Files & Metadata Module**: `files` command for hash calculation and EXIF data extraction.
- **Exporters**: Functionality to export results to JSON, CSV, TXT, and PDF.
- **Concurrency**: Implemented a concurrent execution helper for faster checks (used in Social Media module).
- **Social Media Module**: `social` command to check for usernames across multiple platforms.
- **Testing**: Added comprehensive unit tests for all new modules and core components.

## [0.1.0] - 2023-10-27

### Added
- Initial release of the OSINT Framework.
- Core components: config, logger, http client.
- CLI foundation with global options.
- UI elements: banner and tables.
- Initial module: Domain & DNS investigation (WHOIS, DNS).
- Project tooling: Makefile, pre-commit, pyproject.toml.
