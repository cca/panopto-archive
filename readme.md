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
# might need to start with folder ID otherwise we need to folders/search first
uv run panochive "CCA Departments" --dest data/
```

## License

ECL-2.0
