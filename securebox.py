import logging

from api.api import API
from bundle import Bundle
from crypto import rsa_generate_key


def create_id(api: API, bundle: Bundle, username: str, email: str):
    logging.info(f"Creating a new identity")
    key = rsa_generate_key()
    public_key = key.publickey()

    user = api.user_register(username, email, public_key)
    # The API does not return our user id, so we will have to look it by ourselves
    # The strategy is to get a list of users with our email, and get the one with the ts closest to ours
    logging.info("Looking for our user ID")
    ts = user["ts"]
    users = api.user_search(email)
    user_at_server = min(users, key=lambda u: abs(float(u["ts"]) - ts))
    user_id = user_at_server["userID"]

    logging.info(f"Saving data to configuration file")
    # Save key and user_id to config
    bundle.set_key(key)
    bundle.set_user_id(user_id)
    # Save data to disk TODO: más tarde?
    bundle.write()
