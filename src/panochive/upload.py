import re
import subprocess
from pathlib import Path
from typing import Literal

import click

# https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html
type AWS_STORAGE_CLASS = Literal[
    "STANDARD",
    "EXPRESS_ONEZONE",
    "REDUCED_REDUNDANCY",
    "INTELLIGENT_TIERING",
    "STANDARD_IA",
    "ONEZONE_IA",
    "GLACIER_IR",
    "GLACIER",
    "DEEP_ARCHIVE",
]


# https://github.com/pydantic/pydantic/discussions/4271
def validate_s3_path(s3_path: str) -> bool:
    """Validate that the given S3 path is correctly formatted."""
    match: re.Match[str] | None = re.match(r"s3://([^/]+)/?", s3_path)
    if not match:
        raise ValueError(f'Invalid S3 path: {s3_path}. Must begin with "s3://".')
    bucket: str = match.group(1)
    if not bucket:
        raise ValueError(f"Invalid S3 path: {s3_path}. Bucket name cannot be empty.")
    if len(bucket) < 3 or len(bucket) > 64:
        raise ValueError(
            f"Invalid S3 path: {s3_path}. Bucket name must be between 3 and 63 characters."
        )
    if not re.match(r"^[a-z0-9.-]+$", bucket):
        raise ValueError(
            f"Invalid S3 path: {s3_path}. Bucket name can only contain lowercase letters, numbers, dots, and hyphens."
        )
    if len(s3_path) > 1023:
        raise ValueError(
            f"Invalid S3 path: {s3_path}. Path cannot exceed 1024 characters."
        )
    return True


@click.command()
@click.help_option("--help", "-h")
@click.argument(
    "local_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.argument("prefix", type=str, required=False, default="")
@click.option(
    "--bucket",
    type=str,
    envvar="AWS_ARCHIVE_BUCKET",
    help="S3 bucket to upload to (default AWS_ARCHIVE_BUCKET env var)",
)
@click.option(
    "-n",
    "--dry-run",
    is_flag=True,
    help="Perform a trial run with no changes made",
)
@click.option(
    "--storage-class",
    type=click.Choice(
        [
            "STANDARD",
            "EXPRESS_ONEZONE",
            "REDUCED_REDUNDANCY",
            "INTELLIGENT_TIERING",
            "STANDARD_IA",
            "ONEZONE_IA",
            "GLACIER_IR",
            "GLACIER",
            "DEEP_ARCHIVE",
        ]
    ),
    default="GLACIER_IR",
    help="S3 storage class for uploaded objects",
    show_choices=False,
    show_default=True,
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress awscli output",
)
@click.option(
    "--no-overwrite",
    is_flag=True,
    help="Do not overwrite existing files",
)
@click.option(
    "--delete",
    is_flag=True,
    help="Delete cloud files that are not present locally",
)
# --include/--exclude may also be useful but we'll start here
def sync_dir_to_cloud(
    local_dir: Path,
    bucket: str,
    prefix: str,
    dry_run: bool,
    storage_class: AWS_STORAGE_CLASS,
    quiet: bool,
    no_overwrite: bool,
    delete: bool,
) -> None:
    """Sync a local directory to an S3 bucket with a path prefix. Use the prefix to ensure the location is right. I strongly recommend using --dry-run to ensure the paths look correct.

    This command is merely a wrapper around `aws s3 sync` but it provides a few niceties: validates S3 path & storage class, ensures we specify a storage class, ensures the S3 path has a `panopto` prefix, and uses an AWS_ARCHIVE_BUCKET env var for the S3 bucket by default.

    Example: uv run sync ./data "CCA Departments"
    """
    s3_path: str = (
        f"s3://{bucket}/panopto/{prefix}/" if prefix else f"s3://{bucket}/panopto"
    )
    validate_s3_path(s3_path)

    cmd: list[str] = [
        "aws",
        "s3",
        "sync",
        str(local_dir),
        s3_path,
        "--storage-class",
        storage_class,
    ]
    if dry_run:
        cmd.append("--dryrun")
    if quiet:
        cmd.append("--quiet")
    if no_overwrite:
        cmd.append("--no-overwrite")
    if delete:
        cmd.append("--delete")

    subprocess.run(cmd, check=True)  # noqa
