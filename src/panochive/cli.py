from datetime import datetime
from os import environ
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.table import Table

from .panopto.api import PanoptoAPICLient
from .panopto.oauth2 import PanoptoOAuth2


def sessions_table(sessions: list[dict[str, Any]]) -> Table:
    table = Table(title="Panopto Sessions")
    # table.add_column("Id", style="cyan", no_wrap=True)
    table.add_column("Name", style="cyan")
    table.add_column("Created", justify="right", style="magenta")
    # CreatedBy data empty in the API?
    # table.add_column("Creator", justify="right", style="cyan")
    table.add_column("Duration (m)", justify="right", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("URL", style="blue")
    for session in sessions:
        date_created: datetime = datetime.fromisoformat(
            session["StartTime"].rstrip("Z")
        )
        table.add_row(
            session["Name"],
            date_created.strftime("%Y-%m-%d"),
            # session.get("CreatedBy", {}).get("Username") or "[unknown]",
            str(round(session.get("Duration", 0.0) / 60.0, 2)),
            session["Description"],
            session["Urls"]["ViewerUrl"],
        )
    return table


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
    type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True),
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

    # merely testing auth, retrieve a folder and exit
    if test:
        # TODO models for Folder and Session objects
        folder: dict[str, Any] = api_client.get_folder(folder_id)
        console.print(f"=== FOLDER: {folder['Name']} ===")
        console.print_json(data=folder)
        sessions: list[dict[str, Any]] = api_client.get_sessions_in_folder(folder_id)
        if len(sessions):
            console.print(sessions_table(sessions))
        else:
            console.print("No sessions in this folder.")
        exit(0)
    else:
        console.print("Non-test mode not implemented yet. Exiting.")
        exit(1)


if __name__ == "__main__":
    main()
