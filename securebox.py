import os
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread

from api.api import API
from bundle.bundle import Bundle
from cryptography.cryptography import *


class SecureBoxClient:
    received_folder = "received"

    def __init__(self, token):
        self.api = API(token)

    def create_id(self, bundle: Bundle, username: str, email: str):
        print(f"Creating a new identity")
        key = rsa_generate_key()
        public_key = key.publickey()

        user = self.api.user_register(username, email, public_key)
        user_id = user["userID"]

        print(f"Saving data to configuration file")
        # Save key and user_id to config
        bundle.set_key(key)
        bundle.set_user_id(user_id)
        # Save data to disk
        bundle.write()

    def search_id(self, query: str):
        print(f"Searching query {query}")
        users = self.api.user_search(query)
        if users:
            for user in users:
                print(f"User ID: {user['userID']}. Name: {user['nombre']}. Email: {user['email']}. TS: {user['ts']}\n"
                             f"Public Key: {user['publicKey']}")
        else:
            print("No users found with the specified query")

    def delete_id(self, user_id: str):
        print(f"Deleting {user_id}...")
        self.api.user_delete(user_id)

    def upload(self, filename: str, receiver_id: str, private_key: RsaKey):
        encrypted_message = self.encrypt_helper(filename, private_key=private_key, receiver_id=receiver_id)
        print(f"Sending file {filename}")
        file_id = self.api.file_upload(filename, encrypted_message)["file_id"]
        print(f"Successfully sent {filename} which got ID {file_id}")

    def list_files(self):
        print("Listing uploaded files...")
        files = self.api.file_list()
        if files:
            for file in files:
                print(f"File ID: {file['fileID']}. File name: {file['fileName']}")
        else:
            print("No files found")

    def download(self, file_id: str, sender_id: str, private_key: RsaKey):
        self.decrypt_helper(file_id=file_id, sender_id=sender_id, private_key=private_key)

    def delete_files(self, *files_id: str):
        if "all" in files_id:
            files_id = [file["fileID"] for file in self.api.file_list()]
        with ThreadPoolExecutor(max_workers=len(files_id)) as pool:
            for file_id in files_id:
                print(f"Deleting file {file_id}...")
                pool.submit(self.api.file_delete, file_id)

    def encrypt_helper(self, filename: str, private_key: RsaKey = None, receiver_id: str = None,
                       to_disk: bool = False) -> bytes:
        """
        This method performs several actions to a file
        :param filename: name of the file to be read
        :param private_key: if provided, the file will be signed digitally
        :param receiver_id: if provided, the file will be encrypted
        :param to_disk: if true, the resulting message (signed and/or encrypted) will be saved to a file
        :return: the resulting message, which will be signed and/or encrypted
        """
        with open(filename, "rb") as f:
            print(f"Opening file {filename}...")
            message = f.read()

            # Sign the message using our private key if provided
            if private_key:
                print("Signing file...")
                signature = sign_message(message, private_key)
                message = signature + message

            # Encrypt the message using the remote public key if provided
            if receiver_id:
                print(f"Retrieving {receiver_id}'s public key...")
                public_key = self.api.user_get_public_key(receiver_id)
                print("Encrypting file...")
                message = encrypt_message(message, public_key)

            # Save the file to disk if requested
            if to_disk:
                output_filename = filename
                if private_key:
                    output_filename += ".signed"
                if receiver_id:
                    output_filename += ".crypt"

                print(f"Saving file {output_filename} to disk")
                with open(output_filename, "wb") as output_file:
                    output_file.write(message)

            return message

    def decrypt_helper(self, filename: str = None, file_id: str = None, sender_id: str = None,
                       private_key: RsaKey = None) -> None:
        # Avoid "referenced before assignment" warnings
        message = bytes()
        output_filename = ""
        public_key = []
        thread = None

        # Get mode
        if filename:
            # Local mode (the file could be encrypted and/or signed)
            with open(filename, "rb") as file:
                message = file.read()

            output_filename = filename.replace(".crypt", "")
            output_filename = output_filename.replace(".signed", "")

            encrypted = ".crypt" in filename
            signed = ".signed" in filename
        elif file_id:
            # SecureBox mode (the file is encrypted and signed)
            encrypted = True
            signed = True
        else:
            print("Not enough arguments when decrypting")
            return

        if signed:
            # Fetch the public key in parallel for maximum performance
            thread = Thread(target=lambda: public_key.append(self.api.user_get_public_key(sender_id)))
            thread.start()

        if file_id:
            # Fetch the file from the SecureBox server
            message, output_filename = self.api.file_download(file_id)
            print(f"File {output_filename} downloaded")

        if encrypted:
            message = decrypt_message(message, private_key)
            print(f"File {output_filename} decrypted")

        if signed:
            thread.join()
            public_key = public_key[0]
            message = verify_signature(message, public_key)
            print(f"File {output_filename} successfully verified")

        if not os.path.exists(SecureBoxClient.received_folder):
            os.mkdir(SecureBoxClient.received_folder)
        print(f"Writing file to {SecureBoxClient.received_folder}/{output_filename}...")
        with open(SecureBoxClient.received_folder + '/' + output_filename, "wb") as file:
            file.write(message)

