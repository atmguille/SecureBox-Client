class SignatureNotAuthentic(Exception):
    def __init__(self):
        message = "The signature is not authentic"
        super().__init__(message)
