import os
import re
from math import floor
from typing import Any

from panochive.panopto.models import Folder


def format_duration(seconds: float) -> str:
    minutes: float = seconds / 60.0
    if minutes < 1.0:
        return f"{seconds:.2f}s"
    elif minutes < 60.0:
        return f"{minutes:.2f}m"
    else:
        hours: int = floor(minutes / 60.0)
        remainder_minutes: float = minutes % 60.0
        return f"{hours}h {remainder_minutes:.2f}m"


def sanitize_path(filename: str, replacement: str = "_") -> str:
    if not filename:
        return "untitled"  # ? Might want to revisit this

    # Remove control characters (ASCII 0-31 and 127)
    filename = re.sub(r"[\x00-\x1f\x7f]", "", filename)

    # Replace illegal characters: < > : " / \ | ? *
    # This covers Windows constraints and Mac's '/' constraint
    illegal_chars = r'[<>:"/\\|?*]'
    filename = re.sub(illegal_chars, replacement, filename)

    # Windows forbids filenames ending in a space or a period
    filename = filename.strip(" .")

    # Check for Windows reserved filenames (CON, PRN, NUL, COM1, etc.)
    # We check the "stem" of the filename (before the extension)
    root: str
    ext: str
    root, ext = os.path.splitext(filename)
    reserved_names: set[str] = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }
    if root.upper() in reserved_names:
        filename = f"{replacement}{filename}"

    # Fallback if the string becomes empty (e.g. " ." -> "")
    return filename if filename else "untitled"


def should_skip(folder_arg: dict[str, Any] | Folder, skip_list: set[str]) -> bool:
    # cast folder dicts to Folder model for consistency
    folder: Folder = (
        Folder(**folder_arg) if isinstance(folder_arg, dict) else folder_arg
    )
    uuid_regex: re.Pattern[str] = re.compile(
        r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    )
    for entry in skip_list:
        if uuid_regex.match(entry) and folder.Id == entry:
            return True
        if folder.Name == entry:
            return True
    return False
