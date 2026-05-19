from pathlib import Path

import pytest

from panochive.download import create_folder
from panochive.utils import format_duration, sanitize_path


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (0.0, "0.00s"),
        (33.33, "33.33s"),
        (30.0, "30.00s"),
        (60.0, "1.00m"),
        (75.0, "1.25m"),
        (90.0, "1.50m"),
        (3600.0, "1h 0.00m"),
        (3665.0, "1h 1.08m"),
        (5430.0, "1h 30.50m"),
    ],
)
def test_format_duration(seconds, expected):
    assert format_duration(seconds) == expected


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("valid.mp4", "valid.mp4"),
        ("inva|id:fi*le?name.txt", "inva_id_fi_le_name.txt"),
        ("   leading_and_trailing_spaces   ", "leading_and_trailing_spaces"),
        ("trailing_periods...", "trailing_periods"),
        ("CON.txt", "_CON.txt"),
        ("NUL", "_NUL"),
        ("AUX.mp4", "_AUX.mp4"),
        ("", "untitled"),
        ("   ", "untitled"),
        ("\x00\x1f\x7fcontrolchars.txt", "controlchars.txt"),
    ],
)
def test_sanitize_path(filename, expected):
    assert sanitize_path(filename) == expected


def test_create_folder(tmp_path):
    # Test normal folder creation
    folder1: Path = create_folder(tmp_path, "Test Folder")
    assert folder1.is_dir()
    assert folder1.name == "Test Folder"

    # Test subfolder creation
    subfolder_name: str = "Subfolder"
    subfolder: Path = create_folder(folder1, subfolder_name)
    assert subfolder.is_dir()
    assert subfolder.name == subfolder_name

    # Test sanitization of folder name
    # Don't need to be exhaustive here since sanitize_path is tested separately
    folder2_name: str = "Inva|id:Fi*le?Name"
    folder2: Path = create_folder(tmp_path, folder2_name)
    assert folder2.is_dir()
    assert folder2.name == sanitize_path(folder2_name)
