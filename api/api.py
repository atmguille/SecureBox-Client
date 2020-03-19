import json
from io import BytesIO
from typing import Tuple

import requests
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey

from api.exceptions import *


class API:
    base_url = "https://vega.ii.uam.es:8080/api"

    def __init__(self, token):
        self.header = {"Authorization": f"Bearer {token}"}

    def user_register(self, username: str, email: str, public_key: RsaKey):
        url = API.base_url + "/users/register"
        body = {
            "nombre": username,
            "email": email,
            "publicKey": public_key.export_key("PEM").decode()
        }

        response = requests.post(url, headers=self.header, json=body)
        parsed_response = json.loads(response.text)

        if response.status_code != 200:
            raise api_exceptions[parsed_response["error_code"]]

        return parsed_response

    def user_search(self, query: str) -> list:
        url = API.base_url + "/users/search"
        body = {"data_search": query}

        response = requests.post(url, headers=self.header, json=body)
        parsed_response = json.loads(response.text)

        if response.status_code != 200:
            raise api_exceptions[parsed_response["error_code"]]

        return parsed_response

    def user_get_public_key(self, user_id: str) -> RsaKey:
        url = API.base_url + "/users/getPublicKey"
        body = {"userID": user_id}

        response = requests.post(url, headers=self.header, json=body)
        parsed_response = json.loads(response.text)

        if response.status_code != 200:
            raise api_exceptions[parsed_response["error_code"]]

        return RSA.import_key(parsed_response["publicKey"])

    def user_delete(self, user_id: str) -> str:
        url = API.base_url + "/users/delete"
        body = {"userID": user_id}

        response = requests.post(url, headers=self.header, json=body)
        parsed_response = json.loads(response.text)

        if response.status_code != 200:
            raise api_exceptions[parsed_response["error_code"]]

        return parsed_response["userID"]

    def file_list(self) -> list:
        url = API.base_url + "/files/list"

        response = requests.get(url, headers=self.header)
        parsed_response = json.loads(response.text)

        if response.status_code != 200:
            raise api_exceptions[parsed_response["error_code"]]

        return parsed_response["files_list"]

    def file_upload(self, filename: str, data: bytes = None) -> str:
        url = API.base_url + "/files/upload"

        if data:
            file = BytesIO(data)
            file.name = filename
        else:
            file = open(filename, "rb")

        body = {"ufile": file}

        # Note that this is the only function of the API which receives an ordinary POST form instead of a JSON one
        response = requests.post(url, headers=self.header, files=body)
        file.close()
        parsed_response = json.loads(response.text)

        if response.status_code != 200:
            raise api_exceptions[parsed_response["error_code"]]

        return parsed_response["file_id"]

    def file_download(self, file_id: str) -> Tuple[bytes, str]:
        url = API.base_url + "/files/download"
        body = {"file_id": file_id}

        response = requests.post(url, headers=self.header, json=body)

        if response.status_code != 200:
            parsed_response = json.loads(response.text)
            raise api_exceptions[parsed_response["error_code"]]

        # Filename has the following format: Content-Disposition: attachment; filename="<FILENAME>"
        filename = response.headers["Content-Disposition"]
        filename = filename[filename.find("filename=\"") + len("filename=\""):]
        filename = filename[:filename.find('"')]

        return response.content, filename

    def file_delete(self, file_id: str) -> str:
        url = API.base_url + "/files/delete"
        body = {"file_id": file_id}

        response = requests.post(url, headers=self.header, json=body)
        parsed_response = json.loads(response.text)

        if response.status_code != 200:
            raise api_exceptions[parsed_response["error_code"]]

        return parsed_response["file_id"]
