import json
import os
from pathlib import Path
from typing import Any

from rich.console import Console

from .panopto.api import PanoptoAPICLient
from .panopto.models import Folder, Session
from .utils import sanitize_path


def create_folder(parent: Path, name: str) -> Path:
    # Resolve path first so length check is accurate (e.g. "." -> CWD)
    folder: Path = (parent / sanitize_path(name)).resolve()
    # Windows has a MAX_PATH limit of 260 chars
    if os.name == "nt" and len(str(folder)) > 260:
        folder = Path(f"\\\\?\\{folder}")
    folder.mkdir(exist_ok=True, parents=True)
    return folder


def download_session_files(
    api_client: PanoptoAPICLient, session_id: str, dest: Path, console: Console
) -> None:
    console.print("Downloading session files not implemented yet. Skipping...")
    session_dict: dict[str, Any] = api_client.get_session(session_id)
    write_json(session_dict, dest / "session_metadata.json")


def write_json(data: Any, dest: Path) -> None:
    with dest.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def download_panopto_folder(
    api_client: PanoptoAPICLient,
    folder_id: str,
    dest: Path,  # will be --dest for root & parent folder for recursive calls
    console: Console,
    recursive: bool,
) -> None:
    folder_dict: dict[str, Any] = api_client.get_folder(folder_id)
    folder: Folder = Folder(**folder_dict)
    console.print(f"Processing folder: [bold]{folder.Name}[/bold]", highlight=False)
    folder_path: Path = create_folder(dest, folder.Name)
    write_json(folder_dict, folder_path / "folder_metadata.json")

    session_dicts: list[dict[str, Any]] = api_client.get_sessions_in_folder(folder_id)
    sessions: list[Session] = [Session(**data) for data in session_dicts]
    console.print(f"{len(sessions)} sessions in folder")
    sessions_path: Path = create_folder(folder_path, "_sessions")
    for session in sessions:
        # TODO rich progress bar
        console.print(f'Processing session: "[bold]{session.Name}[/bold]"')
        session_path: Path = create_folder(
            sessions_path, sanitize_path(session.Name, replacement=" ")
        )
        download_session_files(api_client, session.Id, session_path, console)

    if recursive:
        subfolders: list[dict[str, Any]] = api_client.get_children(folder_id)
        for subfolder in subfolders:
            download_panopto_folder(
                api_client,
                subfolder["Id"],
                folder_path,
                console,
                recursive,
            )
