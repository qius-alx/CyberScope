# src/osint/ui/banner.py
from rich.console import Console
from rich.text import Text

console = Console()

def print_banner():
    """
    Prints the application banner using ASCII art.
    """
    banner_text = r"""
 ██████╗ ███████╗██╗███╗   ██╗████████╗   ███████╗██╗    ██╗
██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝   ██╔════╝██║    ██║
██║   ██║███████╗██║██╔██╗ ██║   ██║      █████╗  ██║    ██║
██║   ██║╚════██║██║██║╚██╗██║   ██║      ██╔══╝  ██║    ██║
╚██████╔╝███████║██║██║ ╚████║   ██║      ███████╗██████╗██║
 ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝      ╚══════╝╚═════╝╚═╝
    """
    text = Text(banner_text, style="bold cyan")
    console.print(text)
    console.print(" " * 15 + "[italic]An extensible OSINT framework for security researchers.[/italic]")
    console.print()
