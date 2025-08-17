# src/osint/core/report.py

class ReportManager:
    """
    A singleton-like class to manage and store data tables generated during a run.
    This allows the data to be collected from various modules and then passed to
    exporters at the end of the execution.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ReportManager, cls).__new__(cls)
            # Initialize state
            cls._instance.tables = []
        return cls._instance

    def add_table(self, title: str, headers: list, rows: list):
        """Adds a table's data to the report."""
        if not rows: # Don't add empty tables
            return
        self.tables.append({"title": title, "headers": headers, "rows": rows})

    def get_tables(self):
        """Returns all collected tables."""
        return self.tables

    def clear(self):
        """Clears all stored tables."""
        self.tables = []

# Global instance to be used across the application
report_manager = ReportManager()
