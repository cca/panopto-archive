from pathlib import Path
from typing import Any

import pytest
from pydantic import HttpUrl

from panochive.download import create_folder
from panochive.panopto.models import Folder, FolderUrls
from panochive.utils import format_duration, sanitize_path, should_skip


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


def mk_folder_dict(folder_id: str, name: str) -> dict[str, Any]:
    """Folders have a required structure and should_skip(Folder) passes them to the
    model so we write helpers to create them
    """
    return {
        "Id": folder_id,
        "Name": name,
        "Description": None,
        "ParentFolder": None,
        "Urls": {
            "FolderUrl": "http://a.co",
            "EmbedUrl": None,
            "ShareSettingsUrl": None,
        },
    }


def mk_folder_obj(folder_id: str, name: str) -> Folder:
    urls = FolderUrls(
        FolderUrl=HttpUrl("http://a.co"), EmbedUrl=None, ShareSettingsUrl=None
    )
    return Folder(
        Id=folder_id,
        Name=name,
        Description=None,
        ParentFolder=None,
        Urls=urls,
    )


@pytest.mark.parametrize(
    "folder_arg, skip_list, expected",
    [
        # match & not matched UUIDs
        (
            mk_folder_dict("41c73e26-234b-4e5b-b62e-ad200071da8c", "Folder 1"),
            {"41c73e26-234b-4e5b-b62e-ad200071da8c"},
            True,
        ),
        (
            mk_folder_dict("41c73e26-234b-4e5b-b62e-ad200071da8c", "Folder 2"),
            {"12345678-234b-4e5b-b62e-ad200071da8c"},
            False,
        ),
        (
            mk_folder_dict("12345678-234b-4e5b-b62e-ad200071da8c", "Matching Name"),
            {"Matching Name"},
            True,
        ),
        (
            mk_folder_dict("12345678-234b-4e5b-b62e-ad200071da8c", "Folder"),
            {"Not matching name"},
            False,
        ),
        # Matching & not matching UUIDs with Folder objects instead of dicts
        (
            mk_folder_obj("12345678-234b-4e5b-b62e-ad200071da8c", "Folder 4"),
            {"12345678-234b-4e5b-b62e-ad200071da8c"},
            True,
        ),
        (
            mk_folder_obj("12345678-234b-4e5b-b62e-ad200071da8c", "Folder 5"),
            {"87654321-234b-4e5b-b62e-ad200071da8c"},
            False,
        ),
        (
            mk_folder_obj("12345678-234b-4e5b-b62e-ad200071da8c", "Matching name"),
            {"Matching name"},
            True,
        ),
        (
            mk_folder_obj("12345678-234b-4e5b-b62e-ad200071da8c", "Folder"),
            {"Not matching name"},
            False,
        ),
    ],
)
def test_should_skip(folder_arg, skip_list, expected):
    assert should_skip(folder_arg, skip_list) == expected
