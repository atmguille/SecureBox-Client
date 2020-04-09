import json
from io import BytesIO
from typing import Tuple

import requests
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey

from api.exceptions import *


class API:
    # base_url = "https://vega.ii.uam.es:8080/api"
    base_url = "https://tfg.eps.uam.es:8080/api"

    def __init__(self, token):
        """
        Initializes an API object. If the token is not valid, an exception will be thrown when calling a method
        of the API, NOT during initialization.
        :param token: token to be used
        """
        self.header = {"Authorization": f"Bearer {token}"}

    def user_register(self, username: str, email: str, public_key: RsaKey):
        """
        Registers a new user
        :param username:
        :param email:
        :param public_key:
        :return: a dictionary with keys userID and ts
        """
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
        """
        Looks for users in the server whose name or email contains the query
        :param query:
        :return: a list with the users. Each user is represented as a dictionary with fields userID, nombre, email,
        publicKey and ts.
        """
        url = API.base_url + "/users/search"
        body = {"data_search": query}

        response = requests.post(url, headers=self.header, json=body)
        parsed_response = json.loads(response.text)

        if response.status_code != 200:
            raise api_exceptions[parsed_response["error_code"]]

        return parsed_response

    def user_get_public_key(self, user_id: str) -> RsaKey:
        """
        Gets the public key of a user whose user_id is passed as a parameter
        :param user_id:
        :return: public RsaKey of the requested user
        """
        url = API.base_url + "/users/getPublicKey"
        body = {"userID": user_id}

        response = requests.post(url, headers=self.header, json=body)
        parsed_response = json.loads(response.text)

        if response.status_code != 200:
            raise api_exceptions[parsed_response["error_code"]]

        return RSA.import_key(parsed_response["publicKey"])

    def user_delete(self, user_id: str) -> dict:
        """
        Deletes our user
        :param user_id: user_id of the user whose token is being used to do the query
        :return: a dictionary with a field called userID
        """
        url = API.base_url + "/users/delete"
        body = {"userID": user_id}

        response = requests.post(url, headers=self.header, json=body)
        parsed_response = json.loads(response.text)

        if response.status_code != 200:
            print(response.text)
            raise api_exceptions[parsed_response["error_code"]]

        return parsed_response

    def file_list(self) -> list:
        """
        Lists the files uploaded by us (they are linked to our token/ID)
        :return: a list of files. Each file is represented as a dictionary with fields fileID and fileName
        """
        url = API.base_url + "/files/list"

        response = requests.get(url, headers=self.header)
        parsed_response = json.loads(response.text)

        if response.status_code != 200:
            raise api_exceptions[parsed_response["error_code"]]

        return parsed_response["files_list"]

    def file_upload(self, filename: str, data: bytes = None) -> dict:
        """
        Uploads a file to the server
        :param filename: name of the file to be uploaded
        :param data: If specified, it will be the content of the file. If not, the file named filename will be sent.
        :return: a dictionary with fields file_id and file_size
        """
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

        return parsed_response

    def file_download(self, file_id: str) -> Tuple[bytes, str]:
        """
        Downloads a file from the server
        :param file_id: id of the file to be downloaded
        :return: a tuple with the content of the file (in bytes) and the name of it (as an ordinary string)
        """
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

    def file_delete(self, file_id: str) -> dict:
        """
        Deletes a file from the server
        :param file_id: id of the file to be deleted
        :return: a dictionary with a field called file_id
        """
        url = API.base_url + "/files/delete"
        body = {"file_id": file_id}

        response = requests.post(url, headers=self.header, json=body)
        parsed_response = json.loads(response.text)

        if response.status_code != 200:
            raise api_exceptions[parsed_response["error_code"]]

        return parsed_response
