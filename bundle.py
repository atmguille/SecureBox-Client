import configparser

from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey


class Bundle:
    filename = "bundle.ini"

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(Bundle.filename)

    def initialization_needed(self) -> bool:
        # TODO: comprobar que estén todos los datos?
        if "SecureBox" in self.config:
            return False
        else:
            self.config["SecureBox"] = {}
            return True

    def write(self):
        with open(Bundle.filename, "w") as f:
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
