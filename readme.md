# Archive Panopto Sessions

Panopto provides no way to bulk download sessions. This is a simple command-line tool for downloading sessions and their corresponding metadata. We want to:

- ✅ Traverse the Panopto folder hierarchy starting at a given point
- (TODO) Filter through sessions according to criteria (e.g. an option to not download private sessions)
- ✅ Download video & caption files
- ❌ Confirm videos transferred successfully using content hashes
- ❓ Push the video files to cloud storage
- ✅ Retain the video metadata alongside the sessions
- ✅ Mirror the Panopto folder hierarchy in cloud storage

## Setup

### Create an OAuth2 Client

- Panopto admin goes to System > [OAuth2 Clients](https://ccarts.hosted.panopto.com/Panopto/Pages/Admin/OauthClients/List.aspx#)
- **New** > make it a  server-side client\*
- CORS URL: `http://localhost` & Redirect URL: `http://localhost:9127/redirect`
- Copy the client ID and secret into the `.env` file (see example.env)

\* This fake server-side weirdness is how the Panopto OAuth2 example was designed and could be avoided by rewriting it.

###

```sh
uv sync
# test (no downloads) with "CCA Departments" folder ID
uv run panochive --test c117dc01-bc96-4eca-a53a-ace50173fb6e
```

`mise` is also used to autoload the `.env` file and manage the python version, but these could be done manually, e.g. `export SERVER=ccarts.hosted.panopto.com` etc...

## Usage

```sh
# download Panopto folder to local "dest" folder (data by default)
uv run panochive de58c934-a306-4aea-95c8-b45601224869 --dest path/to/dest
# recursively download everything in a portion of the folder hierarchy
uv run panochive -r de58c934-a306-4aea-95c8-b45601224869
```

### Skip Folders

While recursing through the folder hierarchy, the `--skip-list` option or `SKIP_LIST` env var takes a JSON file containing an array of folder names or UUIDs to skip. We can skip specific folders we know we do not want to dwownload, e.g. due to privacy ("Faculty Affairs & Records") or copyright concerns ("Catalog Media").

### Copy to S3

There is light wrapper around `aws s3 sync`, see `uv run sync --help` for details. In general, prefer using this tool rather than running aws commands manually to have some assurance and a consistent storage class. Set the name of the AWS bucket as an `AWS_ARCHIVE_BUCKET` env var. Examples:

```sh
uv run sync ./data Libraries --dry-run # see s3 paths before uploading
uv run sync ./data "CCA Departments" # sync to s3://BUCKET/CCA Departments/...
uv run sync ./data --quiet # no awscli output
```

### Copy to GCP

Generally, prefer using the archive S3 bucket above, but if for some reason we want to use GCP.

Once downloaded, we can copy the files from their "dest" (data) folder to GCP using `gcloud storage cp`. Make sure to preserve the Panopto folder hierarchy, e.g. if you download ROOT/Libraries/CAPL Archive then the folder locally will be data/CAPL Archive. If you copy that to GCP, put it where it belongs under "Libraries", not in the bucket's root.

```sh
uv run panochive FOLDER_ID
gcloud storage cp --recursive "data/CAPL Archive" "gs://panopto_archive/Libraries"
```

## Development

```sh
uv run pytest src/panochive/tests # test
uv run ruff format src/panochive # formatting
uv run ruff check src/panochive # type checking and linting
```

## License

ECL-2.0
