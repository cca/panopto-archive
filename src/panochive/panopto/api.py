#!python3
import time
import urllib.parse
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

    def __inspect_response_is_retry_needed(self, response):
        """
        Inspect the response of a requets' call.
        True indicates the retry needed, False indicates success. Othrwise an exception is thrown.
        Reference: https://stackoverflow.com/a/24519419

        This method detects 401 (Unauthorized), refresh the access token, and returns as "is retry needed".
        This method also detects 429 (Too many request) which means API throttling by the server. Wait a sec and return as "is retry needed".
        Prodcution code should handle other failure cases and errors as appropriate.
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
                resp = self.requests_session.put(url=url, json=payload, headers=headers)
                if self.__inspect_response_is_retry_needed(resp):
                    continue
                return True
        except Exception as e:
            print(f"Rename failed. {e}")
            return False

    def delete_folder(self, folder_id):
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

    def search_folders(self, query):
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
