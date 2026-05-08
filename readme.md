# Archive Panopto Sessions

Panopto provides no way to bulk download sessions. This will be a simple command-line tool for downloading sessions and their corresponding metadata. Ideally we want to:

- Traverse the Panopto folder hierarchy starting at a given point
- Filter through sessions according to criteria (e.g. an option to not download private sessions)
- Download video files and confirm they transferred successfully (do we have content hashes?)
- Push the video files to cloud storage
- Retain the video metadata alongside the sessions
- It might be desirable to save them in a directory structure mirroring the hierarchy in Panopto

I don't know how much of that will be possible, e.g. having content hashes of streams, nor do I know if this can be accomplished through the REST API or if we have to use SOAP.

## Setup

TODO: credentials

```sh
uv sync
cp example.env .env # fill in credentials
```

## Usage

```sh
# might need to start with folder ID otherwise we need to folders/search first
uv run panochive --folder "CCA Departments" --dest data/
```

## License

ECL-2.0
