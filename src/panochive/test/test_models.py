import pytest
from pydantic import ValidationError

from ..panopto.models import Folder, Session, SessionUrls, User


class TestUser:
    """Test User model."""

    def test_user_with_username(self) -> None:
        """User with a username."""
        user = User(Id="user-123", Username="john.doe")
        assert user.Id == "user-123"
        assert user.Username == "john.doe"

    def test_user_with_null_username(self) -> None:
        """User with null username (as seen in API responses)."""
        user = User(Id="00000000-0000-0000-0000-000000000000", Username=None)
        assert user.Id == "00000000-0000-0000-0000-000000000000"
        assert user.Username is None

    def test_user_without_username_field(self) -> None:
        """User without username field provided (defaults to None)."""
        user = User(Id="user-456")
        assert user.Id == "user-456"
        assert user.Username is None

    def test_user_missing_id_fails(self) -> None:
        """User requires Id field."""
        with pytest.raises(ValidationError):
            User(Username="john.doe")  # type: ignore


class TestSessionUrls:
    """Test SessionUrls model."""

    def test_all_urls_present(self) -> None:
        """All URL fields present."""
        # Pylance complains that these are literal strings & not HttpUrls
        urls = SessionUrls(
            ViewerUrl="https://example.com/viewer",  # type: ignore
            EmbedUrl="https://example.com/embed",  # type: ignore
            ShareSettingsUrl="https://example.com/share",  # type: ignore
            DownloadUrl="https://example.com/download",  # type: ignore
            AudioDescriptionDownloadUrl="https://example.com/audio",  # type: ignore
            CaptionDownloadUrl="https://example.com/captions",  # type: ignore
            EditorUrl="https://example.com/editor",  # type: ignore
            ThumbnailUrl="https://example.com/thumb.jpg",  # type: ignore
        )
        assert str(urls.ViewerUrl) == "https://example.com/viewer"
        assert str(urls.ThumbnailUrl) == "https://example.com/thumb.jpg"

    def test_most_urls_null(self) -> None:
        """Most URLs can be null, as seen in real API responses."""
        urls = SessionUrls(
            ViewerUrl="https://example.com/viewer",  # type: ignore
            CaptionDownloadUrl="https://example.com/captions",  # type: ignore
            ThumbnailUrl="https://example.com/thumb.jpg",  # type: ignore
        )
        assert str(urls.ViewerUrl) == "https://example.com/viewer"
        assert urls.EmbedUrl is None
        assert urls.DownloadUrl is None


class TestSession:
    """Test Session model."""

    def test_session_from_example_data(self) -> None:
        """Parse a session matching example-sessions.json structure."""
        session_data = {
            "Id": "b26f458f-9cd9-4722-a5b8-b2f9017a2304",
            "Name": "2025 118th CCA Commencement - Master Ceremony",
            "Description": "The 118th commencement ceremony for California College of the Arts.",
            "StartTime": "2025-06-11T15:56:46.082Z",
            "Duration": 4590.833,
            "MostRecentViewPosition": 553.8736,
            "CreatedBy": {
                "Id": "00000000-0000-0000-0000-000000000000",
                "Username": None,
            },
            "Urls": {
                "ViewerUrl": "https://ccarts.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=b26f458f-9cd9-4722-a5b8-b2f9017a2304",
                "EmbedUrl": None,
                "ShareSettingsUrl": None,
                "DownloadUrl": None,
                "AudioDescriptionDownloadUrl": None,
                "CaptionDownloadUrl": "https://ccarts.hosted.panopto.com/Panopto/Pages/Transcription/GenerateSRT.ashx?id=b26f458f-9cd9-4722-a5b8-b2f9017a2304",
                "EditorUrl": None,
                "ThumbnailUrl": "https://d2y36twrtb17ty.cloudfront.net/sessions/thumb.jpg",
            },
            "Folder": "dfff45e6-0db7-4fab-aea5-b2fa01163dcf",
            "FolderDetails": {
                "Id": "dfff45e6-0db7-4fab-aea5-b2fa01163dcf",
                "Name": "2025 118th Commencement",
            },
            "PercentCompleted": 4,
        }
        session = Session(**session_data)
        assert session.Id == "b26f458f-9cd9-4722-a5b8-b2f9017a2304"
        assert session.Name == "2025 118th CCA Commencement - Master Ceremony"
        assert session.Duration == 4590.833
        assert session.CreatedBy.Username is None
        assert session.PercentCompleted == 4

    def test_session_with_null_description(self) -> None:
        """Session with null description."""
        session_data = {
            "Id": "session-123",
            "Name": "Session Name",
            "Description": None,
            "StartTime": "2025-06-11T15:56:46.082Z",
            "Duration": 3600.0,
            "MostRecentViewPosition": 100.0,
            "CreatedBy": {"Id": "user-123", "Username": "jane.doe"},
            "Urls": {
                "ViewerUrl": "https://example.com/viewer",
                "EmbedUrl": None,
                "ShareSettingsUrl": None,
                "DownloadUrl": None,
                "AudioDescriptionDownloadUrl": None,
                "CaptionDownloadUrl": None,
                "EditorUrl": None,
                "ThumbnailUrl": None,
            },
            "Folder": "folder-123",
            "FolderDetails": {"Id": "folder-123", "Name": "My Folder"},
            "PercentCompleted": 50,
        }
        session = Session(**session_data)
        assert session.Description is None

    def test_session_datetime_parsing(self) -> None:
        """Datetime fields are parsed correctly."""
        session_data = {
            "Id": "session-123",
            "Name": "Session Name",
            "Description": "Test",
            "StartTime": "2025-06-11T15:56:46.082Z",
            "Duration": 3600.0,
            "MostRecentViewPosition": 100.0,
            "CreatedBy": {"Id": "user-123", "Username": "jane.doe"},
            "Urls": {"ViewerUrl": "https://example.com/viewer"},
            "Folder": "folder-123",
            "FolderDetails": {"Id": "folder-123", "Name": "My Folder"},
            "PercentCompleted": 50,
        }
        session = Session(**session_data)
        assert session.StartTime.year == 2025
        assert session.StartTime.month == 6
        assert session.StartTime.day == 11

    def test_session_missing_required_field_fails(self) -> None:
        """Session requires all mandatory fields."""
        with pytest.raises(ValidationError):
            Session(
                Id="session-123",
                Name="Session Name",
                Description="Test",
                # Missing StartTime (required)
                Duration=3600.0,
                MostRecentViewPosition=100.0,
                CreatedBy={"Id": "user-123"},
                Urls={"ViewerUrl": "https://example.com/viewer"},  # type: ignore
                Folder="folder-123",
                FolderDetails={"Id": "folder-123", "Name": "My Folder"},
                PercentCompleted=50,
            )

    def test_session_with_context(self) -> None:
        """Session with context list."""
        session_data = {
            "Id": "session-123",
            "Name": "Session Name",
            "Description": "Test",
            "StartTime": "2025-06-11T15:56:46.082Z",
            "Duration": 3600.0,
            "MostRecentViewPosition": 100.0,
            "CreatedBy": {"Id": "user-123", "Username": "jane.doe"},
            "Urls": {"ViewerUrl": "https://example.com/viewer"},
            "Folder": "folder-123",
            "FolderDetails": {"Id": "folder-123", "Name": "My Folder"},
            "PercentCompleted": 50,
            "Context": [
                {
                    "Text": "Introduction",
                    "Time": 0,
                    "ThumbnailUrl": "https://example.com/thumb1.jpg",
                },
                {
                    "Text": "Main Content",
                    "Time": 300,
                    "ThumbnailUrl": "https://example.com/thumb2.jpg",
                },
            ],
        }
        session = Session(**session_data)
        assert session.Context is not None
        assert len(session.Context) == 2
        assert session.Context[0].Text == "Introduction"
        assert session.Context[1].Time == 300

    def test_session_without_context(self) -> None:
        """Session without context field."""
        session_data = {
            "Id": "session-123",
            "Name": "Session Name",
            "Description": "Test",
            "StartTime": "2025-06-11T15:56:46.082Z",
            "Duration": 3600.0,
            "MostRecentViewPosition": 100.0,
            "CreatedBy": {"Id": "user-123", "Username": "jane.doe"},
            "Urls": {"ViewerUrl": "https://example.com/viewer"},
            "Folder": "folder-123",
            "FolderDetails": {"Id": "folder-123", "Name": "My Folder"},
            "PercentCompleted": 50,
        }
        session = Session(**session_data)
        assert session.Context is None


class TestFolder:
    """Test Folder model."""

    def test_folder_from_example_data(self) -> None:
        """Parse a folder with complete data."""
        folder_data = {
            "Id": "dfff45e6-0db7-4fab-aea5-b2fa01163dcf",
            "Name": "2025 118th Commencement",
            "Description": "All commencement recordings for 2025",
            "ParentFolder": {
                "Id": "parent-folder-123",
                "Name": "Parent Folder",
            },
            "Urls": {
                "FolderUrl": "https://ccarts.hosted.panopto.com/Panopto/Pages/Sessions/List.aspx#folderID=...",
                "EmbedUrl": "https://example.com/embed",
                "ShareSettingsUrl": "https://example.com/share",
            },
        }
        folder = Folder(**folder_data)
        assert folder.Id == "dfff45e6-0db7-4fab-aea5-b2fa01163dcf"
        assert folder.Name == "2025 118th Commencement"
        assert folder.Description == "All commencement recordings for 2025"
        assert folder.ParentFolder is not None
        assert folder.ParentFolder.Name == "Parent Folder"

    def test_folder_minimal(self) -> None:
        """Folder with only required fields."""
        folder_data = {
            "Id": "folder-123",
            "Name": "My Folder",
            "Urls": {"FolderUrl": "https://example.com/folder"},
        }
        folder = Folder(**folder_data)
        assert folder.Id == "folder-123"
        assert folder.Name == "My Folder"
        assert folder.Description is None
        assert folder.ParentFolder is None

    def test_folder_null_description(self) -> None:
        """Folder with null description."""
        folder_data = {
            "Id": "folder-123",
            "Name": "My Folder",
            "Description": None,
            "Urls": {"FolderUrl": "https://example.com/folder"},
        }
        folder = Folder(**folder_data)
        assert folder.Description is None

    def test_folder_without_parent(self) -> None:
        """Folder without parent folder (root folder)."""
        folder_data = {
            "Id": "root-folder",
            "Name": "Root",
            "Description": "Root folder",
            "Urls": {"FolderUrl": "https://example.com/root"},
        }
        folder = Folder(**folder_data)
        assert folder.ParentFolder is None

    def test_folder_missing_name_fails(self) -> None:
        """Folder requires Name field."""
        with pytest.raises(ValidationError):
            Folder(
                Id="folder-123",
                Urls={"FolderUrl": "https://example.com/folder"},  # type: ignore
            )  # type: ignore

    def test_folder_missing_urls_fails(self) -> None:
        """Folder requires Urls field."""
        with pytest.raises(ValidationError):
            Folder(
                Id="folder-123",
                Name="My Folder",
            )  # type: ignore

    def test_folder_urls_optional_fields(self) -> None:
        """FolderUrls has optional embed and share settings."""
        folder_data = {
            "Id": "folder-123",
            "Name": "My Folder",
            "Urls": {
                "FolderUrl": "https://example.com/folder",
                "EmbedUrl": None,
                "ShareSettingsUrl": None,
            },
        }
        folder = Folder(**folder_data)
        assert str(folder.Urls.FolderUrl) == "https://example.com/folder"
        assert folder.Urls.EmbedUrl is None
        assert folder.Urls.ShareSettingsUrl is None
