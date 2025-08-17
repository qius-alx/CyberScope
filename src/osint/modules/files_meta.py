# src/osint/modules/files_meta.py
import click
import os
import hashlib
import magic
import exifread
from pathlib import Path

from osint.core.logger import logger
from osint.ui.tables import print_table

def analyze_file(file_path: Path, run_hash: bool, run_exif: bool):
    """Analyzes a single file for hashes and EXIF data."""
    logger.info(f"Analyzing file: {file_path}")

    if run_hash:
        calculate_hashes(file_path)

    if run_exif:
        get_exif_data(file_path)

def calculate_hashes(file_path: Path):
    """Calculates and prints MD5, SHA1, and SHA256 hashes for a file."""
    try:
        hasher_md5 = hashlib.md5()
        hasher_sha1 = hashlib.sha1()
        hasher_sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher_md5.update(chunk)
                hasher_sha1.update(chunk)
                hasher_sha256.update(chunk)

        headers = ["Hash Type", "Value"]
        rows = [
            ["MD5", hasher_md5.hexdigest()],
            ["SHA1", hasher_sha1.hexdigest()],
            ["SHA256", hasher_sha256.hexdigest()],
        ]
        print_table(f"Hashes for {file_path.name}", headers, rows)

    except Exception as e:
        logger.error(f"Failed to calculate hashes for {file_path}: {e}")

def get_exif_data(file_path: Path):
    """Extracts and prints EXIF data from an image file."""
    try:
        # Check if the file is an image using python-magic
        mime = magic.from_file(str(file_path), mime=True)
        if not mime.startswith('image'):
            logger.debug(f"Skipping EXIF scan for non-image file: {file_path.name} (MIME: {mime})")
            return

        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f, details=False) # details=False is faster

            if not tags:
                logger.info(f"No EXIF information found in {file_path.name}")
                return

            headers = ["Tag", "Value"]
            # Exclude thumbnail data from the output for brevity
            rows = [[key, str(value)] for key, value in tags.items() if 'thumbnail' not in key.lower()]

            if rows:
                print_table(f"EXIF Data for {file_path.name}", headers, rows)

    except Exception as e:
        logger.error(f"Failed to extract EXIF data from {file_path}: {e}")


@click.command('files')
@click.option('--path', 'input_path', required=True, type=click.Path(exists=True, readable=True, resolve_path=True), help="Path to a file or directory to analyze.")
@click.option('--hash', 'run_hash', is_flag=True, help="Calculate file hashes (MD5, SHA1, SHA256).")
@click.option('--exif', 'run_exif', is_flag=True, help="Extract EXIF data from image files.")
def files_cmd(input_path, run_hash, run_exif):
    """Analyzes local files for metadata and hashes."""
    path = Path(input_path)

    if not any([run_hash, run_exif]):
        run_hash = True
        run_exif = True

    if path.is_file():
        analyze_file(path, run_hash, run_exif)
    elif path.is_dir():
        logger.info(f"Analyzing all files in directory: {path}")
        for root, _, files in os.walk(path):
            for name in files:
                file_path = Path(root) / name
                try:
                    if file_path.is_file():
                        analyze_file(file_path, run_hash, run_exif)
                except Exception as e:
                    logger.error(f"Could not analyze file {file_path}: {e}")
    else:
        logger.error(f"The provided path is neither a file nor a directory: {path}")
