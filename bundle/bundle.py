import configparser
import json
from getpass import getpass
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import unpad, pad

from bundle.exceptions import IncorrectPassword


class Bundle:
    plain_filename = "bundle.ini"
    cyphered_filename = "bundle.enc"

    def __init__(self):
        self.config = configparser.ConfigParser()

        if Path(Bundle.cyphered_filename).exists():
            with open(Bundle.cyphered_filename, "rb") as f:
                salt = f.read(32)
                iv = f.read(16)
                ciphered_data = f.read()

            self.password = getpass("Enter bundle password: ")
            key = PBKDF2(self.password, salt, dkLen=32)

            try:
                decipher = AES.new(key, AES.MODE_CBC, iv=iv)
                deciphered_data = unpad(decipher.decrypt(ciphered_data), AES.block_size)
                dictionary = json.loads(deciphered_data.decode())

                self.config.read_dict(dictionary)
            except Exception:
                # If the password is not correct, decrypt will produce random garbage, and it is highly unlikely
                # that that garbage could have the correct padding and a JSON format that could be understood
                # by the configparser
                raise IncorrectPassword()

        elif Path(Bundle.plain_filename).exists():
            self.password = ""
            self.config.read(Bundle.plain_filename)
        else:
            self.password = None

    def initialization_needed(self) -> bool:
        # TODO: we could check that all the fields are in the bundle to avoid
        if "SecureBox" in self.config:
            return False
        else:
            self.config["SecureBox"] = {}
            return True

    def write(self):
        if self.password is None:
            self.password = getpass("Enter bundle password (empty = no password): ")

        if self.password:
            salt = get_random_bytes(32)
            key = PBKDF2(self.password, salt, dkLen=32)

            cipher = AES.new(key, AES.MODE_CBC)
            data = json.dumps(self.config._sections).encode()
            ciphered_data = cipher.encrypt(pad(data, AES.block_size))

            with open(Bundle.cyphered_filename, "wb") as f:
                f.write(salt)
                f.write(cipher.iv)
                f.write(ciphered_data)
        else:
            with open(Bundle.plain_filename, "w") as f:
                self.config.write(f)

    def get_token(self) -> str:
        return self.config["SecureBox"]["token"]

    def set_token(self, token: str):
        self.config["SecureBox"]["token"] = token

    def get_user_id(self) -> str:
        return self.config["SecureBox"]["user_id"]

    def set_user_id(self, user_id: str):
        self.config["SecureBox"]["user_id"] = user_id

    def get_key(self) -> RsaKey:
        return RSA.import_key(self.config["SecureBox"]["key"])

    def set_key(self, key: RsaKey):
        self.config["SecureBox"]["key"] = key.export_key("PEM").decode()
