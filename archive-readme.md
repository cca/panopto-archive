# Panopto Archive Data Layout

This folder mirrors CCA's Panopto folder hierarchy and stores media plus raw API metadata for each folder and session.

This is merely an overview of the structure and contents of the archive. See "data-dictionary.xlsx" spreadsheet for a complete list of metadata fields and enumerated values.

## Folder Structure

```text
<folder>/
├── folder_metadata.json
├── access.json
├── permissions.json
└── _sessions/
    └── <session name>/
        ├── session_metadata.json
        ├── access.json
        ├── permissions.json
        ├── <session>_default.mp4
        └── <session>_Captions_<language>.txt
```

## Saved File Types

- Media files: `*_default.mp4` (session video), plus occasional image assets (for example slide or thumbnail JPG/PNG files).
- Captions/transcripts: `*_Captions_<language>.txt` when available.
- JSON API responses: `folder_metadata.json`, `session_metadata.json`, `access.json`, and `permissions.json`.

## Permissions And Access Notes

- `permissions.json` stores per-principal role assignments under `Results[]`.
- `Role.Name` indicates the role (common values seen here: `Creator`, `Viewer`).
- `Principal.Type` distinguishes user vs group assignments.
- `IsInherited` shows whether a permission comes from a parent folder.
- `access.json` stores overall visibility (for example `Level: "Restricted"`) and whether that visibility is inherited.

## Important JSON Fields

- Session metadata (`session_metadata.json`):
  - `Name`, `Description`, `Id`, `Duration`, `CreatedBy.Username`, `FolderDetails.Name`
  - `Urls.ViewerUrl`, `Urls.DownloadUrl`, `Urls.CaptionDownloadUrl`, `Urls.EditorUrl`
- Folder metadata (`folder_metadata.json`):
  - `Name`, `Description`, `Id`, `ParentFolder`, `Urls.FolderUrl`
