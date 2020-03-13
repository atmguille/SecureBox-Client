import requests

base_url = "https://vega.ii.uam.es:8080/api"

token = open("token.txt").readline()



def register_user(username: str, email: str):
    url = base_url + "/users/register"
    body = {
        "nombre": username,
        "email": email,
        "publicKey":
    }
    requests.post(url)