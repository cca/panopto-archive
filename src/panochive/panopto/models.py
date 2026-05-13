from datetime import datetime
from typing import List, Optional

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
