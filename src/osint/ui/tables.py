# src/osint/ui/tables.py
from typing import List, Optional

from rich.console import Console
from rich.table import Table
from osint.core.report import report_manager

console = Console()

def print_table(title: str, headers: List[str], rows: List[List[str]], show_header: bool = True):
    """
    Prints a formatted table to the console using rich and stores the data for exporting.

    Args:
        title (str): The title of the table.
        headers (List[str]): A list of strings for the table headers.
        rows (List[List[str]]): A list of lists, where each inner list is a row.
        show_header (bool): Whether to display the table header.
    """
    if not rows:
        console.print(f"[yellow]No data to display for '{title}'.[/yellow]")
        return

    table = Table(
        title=f"[bold green]{title}[/bold green]",
        show_header=show_header,
        header_style="bold magenta"
    )

    for header in headers:
        table.add_column(header)

    for row in rows:
        # Ensure all items in row are strings to avoid rich errors
        str_row = [str(item) for item in row]
        table.add_row(*str_row)

    console.print(table)

    # Store the data for potential export
    report_manager.add_table(title=title, headers=headers, rows=rows)
