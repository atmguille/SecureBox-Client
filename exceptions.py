class SignatureNotAuthentic(Exception):
    def __init__(self):
        message = "The signature is not authentic"
        super().__init__(message)


class PrivateKeyNotFound(Exception):
    def __init__(self):
        message = "RSA private key was not found"
        super().__init__(message)
