# tests/test_core/test_exporters.py
import pytest
import json
import csv
from pathlib import Path
from osint.core import exporters
from osint.core.report import report_manager
from osint.core.config import settings

@pytest.fixture(autouse=True)
def manage_report_data():
    """Fixture to clear the report manager before each test."""
    report_manager.clear()
    yield
    report_manager.clear()

@pytest.fixture
def mock_data():
    """Fixture to provide mock data for the report manager."""
    return [
        {
            "title": "Test Table 1",
            "headers": ["Col1", "Col2"],
            "rows": [["a", "b"], ["c", "d"]]
        },
        {
            "title": "Test Table 2",
            "headers": ["Info", "Value"],
            "rows": [["Key", "Data"]]
        }
    ]

def test_export_json(tmp_path, mock_data):
    """Test the JSON exporter."""
    settings.output_dir = str(tmp_path)
    for table in mock_data:
        report_manager.add_table(**table)

    exporters.export_json()

    # Find the created json file (it's in a timestamped sub-folder)
    output_dir = next(tmp_path.iterdir())
    json_file = output_dir / "report.json"

    assert json_file.exists()
    with open(json_file, 'r') as f:
        data = json.load(f)
    assert data[0]['title'] == "Test Table 1"
    assert data[1]['rows'][0] == ["Key", "Data"]

def test_export_csv(tmp_path, mock_data):
    """Test the CSV exporter."""
    settings.output_dir = str(tmp_path)
    for table in mock_data:
        report_manager.add_table(**table)

    exporters.export_csv()

    output_dir = next(tmp_path.iterdir())
    csv1 = output_dir / "test_table_1.csv"
    csv2 = output_dir / "test_table_2.csv"

    assert csv1.exists()
    assert csv2.exists()
    with open(csv1, 'r') as f:
        reader = csv.reader(f)
        assert next(reader) == ["Col1", "Col2"]
        assert next(reader) == ["a", "b"]

def test_export_txt(tmp_path, mock_data):
    """Test the TXT exporter."""
    settings.output_dir = str(tmp_path)
    for table in mock_data:
        report_manager.add_table(**table)

    exporters.export_txt()

    output_dir = next(tmp_path.iterdir())
    txt_file = output_dir / "report.txt"

    assert txt_file.exists()
    content = txt_file.read_text()
    assert "--- Test Table 1 ---" in content
    assert "Col1\tCol2" in content
    assert "a\tb" in content

def test_export_pdf(tmp_path, mock_data, mocker):
    """Test the PDF exporter."""
    settings.output_dir = str(tmp_path)
    for table in mock_data:
        report_manager.add_table(**table)

    mock_weasyprint = mocker.patch('osint.core.exporters.HTML')
    mock_weasyprint_instance = mock_weasyprint.return_value

    exporters.export_pdf()

    # Check that WeasyPrint's HTML constructor was called with the rendered template
    mock_weasyprint.assert_called_once()
    html_content = mock_weasyprint.call_args[1]['string']
    assert "<h1>OSINT Framework Report</h1>" in html_content
    assert "Test Table 1" in html_content

    # Check that write_pdf was called on the correct path
    output_dir = next(tmp_path.iterdir())
    pdf_file = output_dir / "report.pdf"
    mock_weasyprint_instance.write_pdf.assert_called_once_with(pdf_file)
