import logging
import os
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread

from api.api import API
from bundle import Bundle
from cryptography.cryptography import *

logging.basicConfig(level=logging.INFO)


class SecureBoxClient:
    received_folder = "received"

    def __init__(self, token):
        self.api = API(token)

    def create_id(self, bundle: Bundle, username: str, email: str):
        logging.info(f"Creating a new identity")
        key = rsa_generate_key()
        public_key = key.publickey()

        user = self.api.user_register(username, email, public_key)
        user_id = user["userID"]

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
        encrypted_message = self.local_crypto(filename, private_key=private_key, receiver_id=destination_id)
        logging.info(f"Sending file {filename}")
        file_id = self.api.file_upload(filename, encrypted_message)["fileID"]
        logging.info(f"Successfully sent {filename} which got ID {file_id}")

    def list_files(self):
        logging.info("Listing uploaded files...")
        for file in self.api.file_list():
            logging.info(file)

    def download(self, file_id: str, source_id: str, private_key: RsaKey):
        logging.info(f"Retrieving file with ID {file_id}...")

        # Download the public key of the sender in parallel with the encrypted file for maximum performance
        public_key = []
        thread = Thread(target=lambda: public_key.append(self.api.user_get_public_key(source_id)))
        thread.start()

        encrypted_message, filename = self.api.file_download(file_id)
        logging.info(f"Successfully downloaded {filename}, decrypting it now...")
        signed_message = decrypt_message(encrypted_message, private_key)

        logging.info(f"Successfully decrypted {filename}, checking signature...")
        # Wait until the public key has been retrieved
        thread.join()
        public_key = public_key[0]
        message = verify_signature(signed_message, public_key)

        if not os.path.exists(SecureBoxClient.received_folder):
            os.mkdir(SecureBoxClient.received_folder)
        logging.info(f"Signature checked, writing file to {SecureBoxClient.received_folder}/{filename}...")
        with open(SecureBoxClient.received_folder + '/' + filename, "wb") as file:
            file.write(message)

    def delete_files(self, *files_id: str):
        if "all" in files_id:
            files_id = [file["fileID"] for file in self.api.file_list()]
        with ThreadPoolExecutor(max_workers=len(files_id)) as pool:
            for file_id in files_id:
                logging.info(f"Deleting file {file_id}...")
                pool.submit(self.api.file_delete, file_id)

    def local_crypto(self, filename: str, private_key: RsaKey = None, receiver_id: str = None, to_disk: bool = False) -> bytes:
        """
        This method performs several actions to a file
        :param filename: name of the file to be read
        :param private_key: if provided, the file will be signed digitally
        :param receiver_id: if provided, the file will be encrypted
        :param to_disk: if true, the resulting message (signed and/or encrypted) will be saved to a file
        :return: the resulting message, which will be signed and/or encrypted
        """
        with open(filename, "rb") as f:
            logging.info(f"Opening file {filename}...")
            message = f.read()

            # Sign the message using our private key if provided
            if private_key:
                logging.info("Signing file...")
                signature = sign_message(message, private_key)
                message = signature + message

            # Encrypt the message using the remote public key if provided
            if receiver_id:
                logging.info(f"Retrieving {receiver_id}'s public key...")
                public_key = self.api.user_get_public_key(receiver_id)
                logging.info("Encrypting file...")
                message = encrypt_message(message, public_key)

            # Save the file to disk if requested
            if to_disk:
                output_filename = filename
                if private_key:
                    output_filename += ".signed"
                if receiver_id:
                    output_filename += ".crypt"

                logging.info(f"Saving file {output_filename} to disk")
                with open(output_filename, "wb") as output_file:
                    output_file.write(message)

            return message
