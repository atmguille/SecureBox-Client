import json
import logging

import requests

base_url = "https://vega.ii.uam.es:8080/api"
token = open("token.txt").readline()
header = {"Authorization": f"Bearer {token}"}


def user_register(username: str, email: str, public_key: str) -> None:
    url = base_url + "/users/register"
    body = {
        "nombre": username,
        "email": email,
        "publicKey": public_key
    }

    response = requests.post(url, headers=header, json=body)
    if response.status_code != 200:
        # We probably have a wrong token (status code 401)
        logging.warning(response.text)


def user_search(query: str) -> list:
    url = base_url + "/users/search"
    body = {"data_search": query}

    response = requests.post(url, headers=header, json=body)
    if response.status_code != 200:
        # We probably have a wrong token (status code 401)
        logging.warning(response.text)
        return []
    parsed_response = json.loads(response.text)
    return parsed_response


def user_get_public_key(user_id: str) -> str:
    url = base_url + "/users/getPublicKey"
    body = {"userID": user_id}

    response = requests.post(url, headers=header, json=body)
    if response.status_code != 200:
        logging.warning(response.text)
        return None

    parsed_response = json.loads(response.text)
    return parsed_response["publicKey"]


def user_delete(user_id: str) -> str:
    url = base_url + "/users/delete"
    body = {"userID": user_id}

    response = requests.post(url, headers=header, json=body)
    if response.status_code != 200:
        logging.warning(response.text)
        return None
    parsed_response = json.loads(response.text)
    return parsed_response["userID"]

#print(user_get_public_key("0378540"))
print(user_get_public_key("0374543fg85400"))