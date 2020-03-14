import json
import requests

from api.exceptions import *

base_url = "https://vega.ii.uam.es:8080/api"
token = open("../token.txt").readline()
header = {"Authorization": f"Bearer {token}"}


def user_register(username: str, email: str, public_key: str) -> None:
    url = base_url + "/users/register"
    body = {
        "nombre": username,
        "email": email,
        "publicKey": public_key
    }

    response = requests.post(url, headers=header, json=body)
    parsed_response = json.loads(response.text)

    if response.status_code != 200:
        raise api_exceptions[parsed_response["error_code"]]


def user_search(query: str) -> list:
    url = base_url + "/users/search"
    body = {"data_search": query}

    response = requests.post(url, headers=header, json=body)
    parsed_response = json.loads(response.text)

    if response.status_code != 200:
        raise api_exceptions[parsed_response["error_code"]]

    return parsed_response


def user_get_public_key(user_id: str) -> str:
    url = base_url + "/users/getPublicKey"
    body = {"userID": user_id}

    response = requests.post(url, headers=header, json=body)
    parsed_response = json.loads(response.text)

    if response.status_code != 200:
        raise api_exceptions[parsed_response["error_code"]]

    return parsed_response["publicKey"]


def user_delete(user_id: str) -> str:
    url = base_url + "/users/delete"
    body = {"userID": user_id}

    response = requests.post(url, headers=header, json=body)
    parsed_response = json.loads(response.text)

    if response.status_code != 200:
        raise api_exceptions[parsed_response["error_code"]]

    return parsed_response["userID"]


def file_list() -> list:
    url = base_url + "/files/list"

    response = requests.get(url, headers=header)
    parsed_response = json.loads(response.text)

    if response.status_code != 200:
        raise api_exceptions[parsed_response["error_code"]]

    return parsed_response["files_list"]


def file_upload(filename: str) -> str:
    url = base_url + "/files/upload"
    with open(filename, "rb") as f:
        body = {"ufile": f}

        # Note that this is the only function of the API which receives an ordinary POST form instead of a JSON one
        response = requests.post(url, headers=header, files=body)
        parsed_response = json.loads(response.text)

        if response.status_code != 200:
            raise api_exceptions[parsed_response["error_code"]]

        return parsed_response["file_id"]


def file_download(file_id: str) -> str:
    url = base_url + "/files/download"
    body = {"file_id": file_id}

    response = requests.post(url, headers=header, json=body)

    if response.status_code != 200:
        parsed_response = json.loads(response.text)
        raise api_exceptions(parsed_response["error_code"])

    return response.text


def file_delete(file_id: str) -> str:
    url = base_url + "/files/delete"
    body = {"file_id": file_id}

    response = requests.post(url, headers=header, json=body)
    parsed_response = json.loads(response.text)

    if response.status_code != 200:
        raise api_exceptions[parsed_response["error_code"]]

    return parsed_response["file_id"]
