from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, HttpUrl


class User(BaseModel):
    Id: str
    Username: Optional[str] = None


class SessionUrls(BaseModel):
    ViewerUrl: Optional[HttpUrl] = None
    EmbedUrl: Optional[HttpUrl] = None
    ShareSettingsUrl: Optional[HttpUrl] = None
    DownloadUrl: Optional[HttpUrl] = None
    AudioDescriptionDownloadUrl: Optional[HttpUrl] = None
    CaptionDownloadUrl: Optional[HttpUrl] = None
    EditorUrl: Optional[HttpUrl] = None
    ThumbnailUrl: Optional[HttpUrl] = None


class FolderDetails(BaseModel):
    Id: str
    Name: str


class SessionContext(BaseModel):
    Text: str
    Time: int
    ThumbnailUrl: HttpUrl


class Session(BaseModel):
    Id: str
    Name: str
    Description: Optional[str] = None
    StartTime: datetime
    Duration: float
    MostRecentViewPosition: float
    CreatedBy: User
    Urls: SessionUrls
    Folder: str
    FolderDetails: FolderDetails
    Context: Optional[List[SessionContext]] = None
    PercentCompleted: Optional[int] = None


class FolderUrls(BaseModel):
    FolderUrl: HttpUrl
    EmbedUrl: Optional[HttpUrl] = None
    ShareSettingsUrl: Optional[HttpUrl] = None


class Folder(BaseModel):
    Id: str
    Name: str
    Description: Optional[str] = None
    ParentFolder: Optional[FolderDetails] = None
    Urls: FolderUrls


# Session & Folder access data shares a structure
# https://ccarts.hosted.panopto.com/Panopto/Api/Docs/index.html#/Sessions/Sessions_GetAccessSettings
# https://ccarts.hosted.panopto.com/Panopto/Api/Docs/index.html#/Folders/Folders_GetAccessSettings
class AccessDetails(BaseModel):
    IsInherited: bool
    Level: Literal[
        "Organization", "OrganizationUnlisted", "Public", "PublicUnlisted", "Restricted"
    ]


class Role(BaseModel):
    Id: str
    # Custom roles would add this to list, not surprised if it's incomplete
    Name: Literal[
        "Viewer",
        "ViewerWithLink",
        "Creator",
        "Publisher",
        "CaptionRequester",
        "ContentOrganizer",
        "AnalyticsManager",
    ]


class Principal(BaseModel):
    Id: str
    Type: Literal["User", "Group"]


# https://ccarts.hosted.panopto.com/Panopto/Api/Docs/index.html#/Sessions/Sessions_GetPermissions
# https://ccarts.hosted.panopto.com/Panopto/Api/Docs/index.html#/Folders/Folders_GetPermissions
class Permission(BaseModel):
    IsInherited: bool
    Role: Role
    Principal: Principal


# Folder & Session APIs return a list of Permission objects (see above)
class Permissions(BaseModel):
    Results: List[Permission]
