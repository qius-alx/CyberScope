# tests/test_modules/test_files_meta.py
import pytest
from click.testing import CliRunner
from osint.cli import cli
from pathlib import Path

@pytest.fixture
def runner():
    return CliRunner()

def test_files_cmd_single_file(runner, tmp_path):
    """Test the files command on a single file."""
    # Create a dummy file
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello world")

    result = runner.invoke(cli, ['files', '--path', str(file_path), '--hash'])
    assert result.exit_code == 0
    assert "Hashes for test.txt" in result.output
    # MD5 for "hello world"
    assert "5eb63bbbe01eeed093cb22bb8f5acdc3" in result.output

def test_files_cmd_directory(runner, tmp_path):
    """Test the files command on a directory."""
    dir_path = tmp_path / "test_dir"
    dir_path.mkdir()
    (dir_path / "file1.txt").write_text("file1")
    (dir_path / "file2.txt").write_text("file2")

    result = runner.invoke(cli, ['files', '--path', str(dir_path), '--hash'])
    assert result.exit_code == 0
    # Check that both files were analyzed
    assert "Hashes for file1.txt" in result.output
    assert "Hashes for file2.txt" in result.output

def test_files_cmd_exif(runner, mocker, tmp_path):
    """Test the files --exif flag."""
    # We need a real image file for exifread to work, but we can mock the libraries
    # to avoid needing a fixture file.
    mock_magic = mocker.patch('osint.modules.files_meta.magic.from_file')
    mock_magic.return_value = 'image/jpeg' # Pretend it's an image

    mock_exif = mocker.patch('osint.modules.files_meta.exifread.process_file')
    mock_exif.return_value = {'EXIF Tag': 'Test Value'}

    file_path = tmp_path / "fake_image.jpg"
    file_path.touch()

    result = runner.invoke(cli, ['files', '--path', str(file_path), '--exif'])
    assert result.exit_code == 0
    assert "EXIF Data for fake_image.jpg" in result.output
    assert "Test Value" in result.output

def test_files_cmd_path_does_not_exist(runner):
    """Test providing a path that does not exist."""
    result = runner.invoke(cli, ['files', '--path', 'non_existent_dir/'])
    assert result.exit_code == 2 # click error for bad parameter
    assert "Path 'non_existent_dir/' does not exist." in result.output
