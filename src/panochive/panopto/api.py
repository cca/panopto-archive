#!python3
import re
import time
import urllib.parse
from pathlib import Path
from typing import Any

import requests


# See https://github.com/Panopto/panopto-api-python-examples/tree/master/folders-cli
class PanoptoAPICLient:
    def __init__(self, server, ssl_verify, oauth2):
        """
        Constructor of folders API handler instance.
        This goes through authorization step of the target server.
        """
        self.server = server
        self.ssl_verify = ssl_verify
        self.oauth2 = oauth2

        # Use requests module's Session object in this example.
        # ref. https://2.python-requests.org/en/master/user/advanced/#session-objects
        self.requests_session = requests.Session()
        self.requests_session.verify = self.ssl_verify

        self.__setup_or_refresh_access_token()

    def __setup_or_refresh_access_token(self):
        """
        This method invokes OAuth2 Authorization Code Grant authorization flow.
        It goes through browser UI for the first time.
        It refreshes the access token after that and no user interaction is required.
        This is called at the initialization of the class, as well as when 401 (Unauthorized) is returned.
        """
        access_token = self.oauth2.get_access_token_authorization_code_grant()
        self.requests_session.headers.update(
            {"Authorization": "Bearer " + access_token}
        )

    def __get_download_session(self):
        """
        Create a session with authenticated cookie for downloads.
        Uses the legacy login endpoint to establish a cookie-based session.
        """
        download_session = requests.Session()
        download_session.verify = self.ssl_verify

        try:
            # Get access token for credentials
            access_token = self.oauth2.get_access_token_authorization_code_grant()

            # Call legacy login endpoint with Bearer token to get authenticated cookie
            url = f"https://{self.server}/Panopto/api/v1/auth/legacylogin"
            headers = {"Authorization": "Bearer " + access_token}

            resp = download_session.get(url=url, headers=headers)
            if resp.status_code == 200:
                # The cookie is automatically stored in the session
                return download_session
            else:
                print(f"Failed to get download session cookie: {resp.status_code}")
                return None
        except Exception as e:
            print(f"Error creating download session: {e}")
            return None

    def __inspect_response_is_retry_needed(self, response):
        """
        Inspect the response of a requets' call.
        True indicates the retry needed, False indicates success. Otherwise an exception is thrown.
        Reference: https://stackoverflow.com/a/24519419

        This method detects 401 (Unauthorized), refresh the access token, and returns as "is retry needed".
        This method also detects 429 (Too many request) which means API throttling by the server. Wait a sec and return as "is retry needed".
        Production code should handle other failure cases and errors as appropriate.
        """
        if response.status_code // 100 == 2:
            # Success on 2xx response.
            return False

        if response.status_code == 401:
            print("Unauthorized. Refresh access token.")
            self.__setup_or_refresh_access_token()
            return True

        if response.status_code == 429:
            print("Too many requests. Wait one sec, and retry.")
            time.sleep(1)
            return True

        # Throw unhandled cases.
        response.raise_for_status()

    def get(self, path: str) -> Any:
        """
        Call GET API and return the response data.
        A generic method for GET calls not covered by other methods.
        Exxample: api.get("/Panopto/api/v1/streams/{id}/captions")
        or api.get("/v1/streams/{id}/captions") with autoprefixing
        """
        # Convenience: allow shorthand v1/route type paths without the /Panopto/api prefix
        if not path.startswith("/Panopto/api"):
            path = "/Panopto/api" + path
        while True:
            resp = self.requests_session.get(url=f"https://{self.server}/{path}")
            if self.__inspect_response_is_retry_needed(resp):
                continue
            data = resp.json()
            break
        return data

    def get_children(self, folder_id):
        """
        Call GET /api/v1/folders/{id}/children API and return the list of entries.
        This code has hard coded sort order of Name / Asc.
        """
        result = []
        page_number = 0
        while True:
            url = f"https://{self.server}/Panopto/api/v1/folders/{folder_id}/children?pageNumber={page_number}&sortField=Name&sortOrder=Asc"
            resp = self.requests_session.get(url=url)
            if self.__inspect_response_is_retry_needed(resp):
                continue
            data = resp.json()
            entries = data["Results"]
            if len(entries) == 0:
                break
            for entry in entries:
                result.append(entry)
            page_number += 1
        return result

    def get_groups(self, folder_id):
        """
        Call GET /api/v1/folders/{id}/groups API and return the list of entries.
        This code has hard coded sort order of Name / Asc.
        """
        result = []
        page_number = 0
        while True:
            url = f"https://{self.server}/Panopto/api/v1/folders/{folder_id}/permissions?pageNumber={page_number}"
            resp = self.requests_session.get(url=url)
            if self.__inspect_response_is_retry_needed(resp):
                continue
            data = resp.json()
            entries = data["Results"]
            if len(entries) == 0:
                break
            for entry in entries:
                result.append(entry)
            page_number += 1
        return result

    def get_folder(self, folder_id: str) -> dict[str, Any]:
        """
        Call GET /api/v1/folders/{id} API and return the response
        """
        while True:
            url = f"https://{self.server}/Panopto/api/v1/folders/{folder_id}"
            resp = self.requests_session.get(url=url)
            if self.__inspect_response_is_retry_needed(resp):
                continue
            data = resp.json()
            break
        return data

    def get_folder_access(self, folder_id: str) -> dict[str, Any]:
        """
        Call GET /api/v1/folders/{id}/access API and return the response
        """
        while True:
            url = f"https://{self.server}/Panopto/api/v1/folders/{folder_id}/settings/access"
            resp = self.requests_session.get(url=url)
            if self.__inspect_response_is_retry_needed(resp):
                continue
            data = resp.json()
            break
        return data

    def get_folder_permissions(self, folder_id: str) -> dict[str, Any]:
        """
        Call GET /api/v1/folders/{id}/permissions API and return the response
        """
        while True:
            url = (
                f"https://{self.server}/Panopto/api/v1/folders/{folder_id}/permissions"
            )
            resp = self.requests_session.get(url=url)
            if self.__inspect_response_is_retry_needed(resp):
                continue
            data = resp.json()
            break
        return data

    def update_folder_name(self, folder_id: str, new_name: str) -> bool:
        """
        Call PUT /api/v1/folders/{id} API to update the name
        Return True if it succeeds, False if it fails.
        """
        try:
            while True:
                url = f"https://{self.server}/Panopto/api/v1/folders/{folder_id}"
                payload = {"Name": new_name}
                headers = {"content-type": "application/json"}
                resp = self.requests_session.put(url=url, json=payload, headers=headers)  # type: ignore
                if self.__inspect_response_is_retry_needed(resp):
                    continue
                return True
        except Exception as e:
            print(f"Rename failed. {e}")
            return False

    def delete_folder(self, folder_id: str) -> bool:
        """
        Call DELETE /api/v1/folders/{id} API to delete a folder
        Return True if it succeeds, False if it fails.
        """
        try:
            while True:
                url = f"https://{self.server}/Panopto/api/v1/folders/{folder_id}"
                resp = self.requests_session.delete(url=url)
                if self.__inspect_response_is_retry_needed(resp):
                    continue
                return True
        except Exception as e:
            print(f"Deletion failed. {e}")
            return False

    def search_folders(self, query: str) -> list[dict[str, Any]]:
        """
        Call GET /api/v1/folders/search API and return the list of entries.
        """
        result = []
        page_number = 0
        while True:
            url = f"https://{self.server}/Panopto/api/v1/folders/search?searchQuery={urllib.parse.quote_plus(query)}&pageNumber={page_number}"
            resp = self.requests_session.get(url=url)
            if self.__inspect_response_is_retry_needed(resp):
                continue
            data = resp.json()
            entries = data["Results"]
            if len(entries) == 0:
                break
            for entry in entries:
                result.append(entry)
            page_number += 1
        return result

    def get_sessions_in_folder(
        self, folder_id: str, sort_field: str = "CreatedDate", sort_order: str = "Desc"
    ) -> list[dict[str, Any]]:
        """
        Call GET /api/v1/folders/{id}/sessions API and return the list of entries.
        """
        result: list[dict[str, Any]] = []
        page_number = 0
        while True:
            url = f"https://{self.server}/Panopto/api/v1/folders/{folder_id}/sessions?pageNumber={page_number}&sortField={sort_field}&sortOrder={sort_order}"
            resp = self.requests_session.get(url=url)
            if self.__inspect_response_is_retry_needed(resp):
                continue
            data = resp.json()
            entries = data["Results"]
            if len(entries) == 0:
                break
            result.extend(entries)
            page_number += 1
        return result

    def get_session(self, session_id: str) -> dict[str, Any]:
        """
        Call GET /api/v1/sessions/{id} API and return the response
        """
        while True:
            url = f"https://{self.server}/Panopto/api/v1/sessions/{session_id}"
            resp = self.requests_session.get(url=url)
            if self.__inspect_response_is_retry_needed(resp):
                continue
            data = resp.json()
            break
        return data

    def get_session_access(self, session_id: str) -> dict[str, Any]:
        """
        Call GET /api/v1/sessions/{id}/access API and return the response
        """
        while True:
            url = f"https://{self.server}/Panopto/api/v1/sessions/{session_id}/settings/access"
            resp = self.requests_session.get(url=url)
            if self.__inspect_response_is_retry_needed(resp):
                continue
            data = resp.json()
            break
        return data

    def get_session_permissions(self, session_id: str) -> dict[str, Any]:
        """
        Call GET /api/v1/sessions/{id}/permissions API and return the response
        """
        while True:
            url = f"https://{self.server}/Panopto/api/v1/sessions/{session_id}/permissions"
            resp = self.requests_session.get(url=url)
            if self.__inspect_response_is_retry_needed(resp):
                continue
            data = resp.json()
            break
        return data

    def update_session_name(self, session_id: str, new_name: str) -> bool:
        """
        Call PUT /api/v1/sessions/{id} API to update the name
        Return True if it succeeds, False if it fails.
        """
        try:
            while True:
                url = f"https://{self.server}/Panopto/api/v1/sessions/{session_id}"
                payload = {"Name": new_name}
                headers = {"content-type": "application/json"}
                resp = self.requests_session.put(url=url, json=payload, headers=headers)  # type: ignore
                if self.__inspect_response_is_retry_needed(resp):
                    continue
                return True
        except Exception as e:
            print(f"Rename failed. {e}")
            return False

    def delete_session(self, session_id: str) -> bool:
        """
        Call DELETE /api/v1/sessions/{id} API to delete a session
        Return True if it succeeds, False if it fails.
        """
        try:
            while True:
                url = f"https://{self.server}/Panopto/api/v1/sessions/{session_id}"
                resp = self.requests_session.delete(url=url)
                if self.__inspect_response_is_retry_needed(resp):
                    continue
                return True
        except Exception as e:
            print(f"Deletion failed. {e}")
            return False

    def search_sessions(self, query: str) -> list[dict[str, Any]]:
        """
        Call GET /api/v1/sessions/search API and return the list of entries.
        Pages through all results and returns the complete list.
        """
        result = []
        page_number = 0
        while True:
            url = f"https://{self.server}/Panopto/api/v1/sessions/search?searchQuery={urllib.parse.quote_plus(query)}&pageNumber={page_number}"
            resp = self.requests_session.get(url=url)
            if self.__inspect_response_is_retry_needed(resp):
                continue
            data = resp.json()
            entries = data["Results"]
            if len(entries) == 0:
                break
            for entry in entries:
                result.append(entry)
            page_number += 1
        return result

    def download_session_file(
        self,
        download_url: str,
        parent_folder: Path,
        filename: str | None = None,
        chunk_size: int = 8192,
    ) -> bool:
        """
        Download a session file (video, captions, or thumbnail) using the provided URL.
        Uses cookie-based authentication via legacy login endpoint.

        Args:
            download_url: download URL (see Sessions[Urls])
            parent_folder: Path to folder to save the file in
            filename: Optional. If not provided, extracted from Content-Disposition header or URL.
            chunk_size: Size of chunks for streaming download

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Get authenticated session with cookie
            download_session: requests.Session | None = self.__get_download_session()
            if not download_session:
                print("Failed to establish authenticated download session")
                return False

            while True:
                resp: requests.Response = download_session.get(
                    url=download_url, stream=True, allow_redirects=True
                )
                if resp.status_code == 401 or resp.status_code == 403:
                    download_session = self.__get_download_session()
                    if not download_session:
                        return False
                    continue
                break

            resp.raise_for_status()

            # Extract filename from response if not provided
            if not filename:
                content_disposition: str = resp.headers.get("Content-Disposition", "")
                # Parse filename from Content-Disposition header
                # Format: attachment; filename="example.mp4" or filename=example.mp4
                match = re.search(
                    r'filename=(?:"([^"]+)"|([^\s;]+))', content_disposition
                )
                if match:
                    filename = match.group(1) or match.group(2)
                else:
                    # Fallback: try to extract from URL
                    filename = urllib.parse.urlparse(download_url).path.split("/")[-1]
                    # Some Sessions (maybe only reference copies?) use a FrameRedirect URL that resolves to a PNG
                    # https://ccarts.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=e1f4958a-11e5-4f61-b0a2-ae1c006ac46a
                    # "https://ccarts.hosted.panopto.com/Panopto/Services/FrameGrabber.svc/FrameRedirect?objectId=e1f4958a-11e5-4f61-b0a2-ae1c006ac46a&mode=Delivery&random=0.0948754745046028&usePng=True"
                    if filename == "FrameRedirect":
                        filename = "thumbnail.png"

            if not filename:
                print(f"Could not determine filename. Download failed: {download_url}")
                return False

            output_path: Path = parent_folder / filename
            with open(output_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
            return True

        except Exception as e:
            print(f"Download failed. {e}")
            return False
