from datetime import datetime
from os import environ
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.table import Table

from .download import download_panopto_folder
from .panopto.api import PanoptoAPICLient
from .panopto.models import Folder, Session
from .panopto.oauth2 import PanoptoOAuth2
from .utils import format_duration

DEBUG: bool = environ.get("DEBUG", "").lower() in ("true", "1", "t")


def folder_table(folder: Folder) -> Table:
    # table alignment but no border lines
    table = Table(box=None, highlight=True, pad_edge=False)
    table.add_row("Id:", folder.Id)
    table.add_row("Description:", folder.Description or "")
    parent_name = (
        folder.ParentFolder.Name if folder.ParentFolder else "NULL (possibly root?)"
    )
    table.add_row("Parent:", parent_name)
    table.add_row("URL:", str(folder.Urls.FolderUrl))
    return table


def sessions_table(sessions: list[Session]) -> Table:
    table = Table(title="Sessions")
    # table.add_column("Id", style="cyan", no_wrap=True)
    table.add_column("Name", style="cyan")
    table.add_column("Created", justify="right", style="magenta")
    table.add_column("Duration", justify="right", style="cyan")
    table.add_column("Description", style="green")
    for session in sessions:
        date_created: datetime = session.StartTime
        table.add_row(
            session.Name,
            date_created.strftime("%Y-%m-%d"),
            format_duration(session.Duration),
            session.Description or "",
        )
    return table


def print_folder_and_sessions(
    api_client: PanoptoAPICLient,
    folder_id: str,
    console: Console,
    recursive: bool,
):
    # get folder
    folder_dict: dict[str, Any] = api_client.get_folder(folder_id)
    if DEBUG:
        console.print_json(data=folder_dict)
    folder = Folder(**folder_dict)
    console.print(f"=== FOLDER: {folder.Name} ===", highlight=False)
    console.print(folder_table(folder))

    # get child sessions
    session_dicts: list[dict[str, Any]] = api_client.get_sessions_in_folder(folder_id)
    if DEBUG:
        console.print_json(data=session_dicts)
    sessions: list[Session] = [
        Session(**session_dict) for session_dict in session_dicts
    ]
    if len(sessions):
        console.print(sessions_table(sessions))
    else:
        console.print("No sessions in this folder.")

    # recursively print subfolders
    if recursive:
        subfolders: list[dict[str, Any]] = api_client.get_children(folder_id)
        for subfolder in subfolders:
            print_folder_and_sessions(
                api_client,
                subfolder["Id"],
                console,
                recursive,
            )


@click.command()
@click.help_option("--help", "-h")
@click.argument(
    "folder_id",
    type=str,
    metavar="FOLDER",
)
@click.option(
    "--dest",
    "-d",
    default="data",
    help="Destination for archived sessions",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path),
)
@click.option(
    "--recursive", "-r", is_flag=True, help="Recursively archive sessions in subfolders"
)
@click.option("--skip-verify", is_flag=True, help="Skip SSL certificate verification")
@click.option("--test", is_flag=True, help="Print folder/session info, do not download")
def main(folder_id: str, dest: Path, recursive: bool, skip_verify: bool, test: bool):
    """Archive Panopto sessions from a folder. Requires SERVER, CLIENT_ID, and CLIENT_SECRET environment variables."""
    server: str = environ.get("SERVER", "")
    client_id: str = environ.get("CLIENT_ID", "")
    client_secret: str = environ.get("CLIENT_SECRET", "")
    ssl_verify: bool = not skip_verify
    console: Console = Console()

    if not server or not client_id or not client_secret:
        console.print(
            "ERROR: requires SERVER, CLIENT_ID, and CLIENT_SECRET environment variables. See readme for details."
        )
        exit(1)

    oauth2: PanoptoOAuth2 = PanoptoOAuth2(server, client_id, client_secret, ssl_verify)
    api_client: PanoptoAPICLient = PanoptoAPICLient(server, ssl_verify, oauth2)

    # merely print folders when testing
    if test:
        return print_folder_and_sessions(api_client, folder_id, console, recursive)
    return download_panopto_folder(api_client, folder_id, dest, console, recursive)


if __name__ == "__main__":
    main()
