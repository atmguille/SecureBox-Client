import logging

from Crypto.PublicKey.RSA import RsaKey

from api.api import API
from bundle import Bundle
from crypto import rsa_generate_key, sign_message, encrypt_message


class SecureBox:
    def __init__(self, token):
        self.api = API(token)

    def create_id(self, bundle: Bundle, username: str, email: str):
        logging.info(f"Creating a new identity")
        key = rsa_generate_key()
        public_key = key.publickey()

        user = self.api.user_register(username, email, public_key)
        # The API does not return our user id, so we will have to look it by ourselves
        # The strategy is to get a list of users with our email, and get the one with the ts closest to ours
        logging.info("Looking for our user ID")
        ts = user["ts"]
        users = self.api.user_search(email)
        user_at_server = min(users, key=lambda u: abs(float(u["ts"]) - ts))
        user_id = user_at_server["userID"]

        logging.info(f"Saving data to configuration file")
        # Save key and user_id to config
        bundle.set_key(key)
        bundle.set_user_id(user_id)
        # Save data to disk TODO: más tarde?
        bundle.write()

    def search_id(self, query: str):
        logging.info(f"Searching query {query}")
        users = self.api.user_search(query)

        for user in users:
            logging.info(user)

    def delete_id(self, user_id: str):
        logging.info(f"Deleting {user_id}...")
        self.api.user_delete(user_id)

    def upload(self, filename: str, destination_id: str, private_key: RsaKey):
        with open(filename, "rb") as file:
            logging.info(f"Reading file {filename}")
            message = file.read()

            # Sign message using our private key
            logging.info(f"Signing file {filename}")
            signature = sign_message(message, private_key)

            logging.info(f"Encrypting file {filename}")
            # Encrypt signed message using the remote public key
            remote_key = self.api.user_get_public_key(destination_id)
            encrypted_message = encrypt_message(signature + message, remote_key)

            logging.info(f"Sending file {filename}")
            file_id = self.api.file_upload(filename, encrypted_message)
            logging.info(f"Successfully sent {filename} which got ID {file_id}")