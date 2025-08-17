# src/osint/core/exporters.py
import json
import csv
import os
from pathlib import Path
from datetime import datetime

from osint.core.config import settings
from osint.core.report import report_manager
from osint.core.logger import logger
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader

def get_output_path(filename: str) -> Path:
    """Constructs the full path for an output file, ensuring the directory exists."""
    # Create a timestamped subdirectory for this run to keep reports organized
    run_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = Path(settings.output_dir) / run_timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / filename

def export_json():
    """Exports all collected data to a single JSON file."""
    logger.info("Exporting results to JSON...")
    data = report_manager.get_tables()
    if not data:
        logger.warning("No data to export.")
        return

    filepath = get_output_path("report.json")
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"Successfully exported JSON report to {filepath}")
    except Exception as e:
        logger.error(f"Failed to export JSON report: {e}")

def export_csv():
    """Exports each table of collected data to a separate CSV file."""
    logger.info("Exporting results to CSV...")
    tables = report_manager.get_tables()
    if not tables:
        logger.warning("No data to export.")
        return

    for table in tables:
        # Sanitize title for a valid filename
        sanitized_title = "".join(c for c in table['title'] if c.isalnum() or c in (' ', '_')).rstrip()
        filename = sanitized_title.replace(' ', '_').lower() + ".csv"
        filepath = get_output_path(filename)

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(table['headers'])
                writer.writerows(table['rows'])
            logger.info(f"Successfully exported CSV file to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export CSV file for table '{table['title']}': {e}")

def export_txt():
    """Exports all collected data to a single plain text file."""
    logger.info("Exporting results to TXT...")
    tables = report_manager.get_tables()
    if not tables:
        logger.warning("No data to export.")
        return

    filepath = get_output_path("report.txt")
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            for table in tables:
                f.write(f"--- {table['title']} ---\n\n")
                # Simple text representation
                f.write("\t".join(table['headers']) + "\n")
                f.write("-" * (8 * len(table['headers'])) + "\n")
                for row in table['rows']:
                    # Ensure all items are strings before joining
                    str_row = [str(item) for item in row]
                    f.write("\t".join(str_row) + "\n")
                f.write("\n\n")
        logger.info(f"Successfully exported TXT report to {filepath}")
    except Exception as e:
        logger.error(f"Failed to export TXT report: {e}")

def export_pdf():
    """Renders collected data into an HTML template and saves it as a PDF."""
    logger.info("Exporting results to PDF...")
    tables = report_manager.get_tables()
    if not tables:
        logger.warning("No data to export.")
        return

    try:
        # Set up Jinja2 environment
        template_dir = Path(__file__).parent.parent / "data"
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("report_template.html")

        # Prepare data for the template
        template_data = {
            "tables": tables,
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Render the HTML
        html_out = template.render(template_data)

        # Generate PDF
        filepath = get_output_path("report.pdf")
        HTML(string=html_out).write_pdf(filepath)

        logger.info(f"Successfully exported PDF report to {filepath}")

    except Exception as e:
        logger.error(f"Failed to export PDF report: {e}")
