import os
from pathlib import Path

from .utils import sanitize_path


def create_folder(parent: Path, name: str) -> Path:
    # Resolve path first so length check is accurate (e.g. "." -> CWD)
    folder: Path = (parent / sanitize_path(name)).resolve()
    # Windows has a MAX_PATH limit of 260 chars
    if os.name == "nt" and len(str(folder)) > 260:
        folder = Path(f"\\\\?\\{folder}")
    folder.mkdir(exist_ok=True, parents=True)
    return folder
