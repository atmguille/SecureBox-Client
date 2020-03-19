class SignatureNotAuthentic(Exception):  # TODO: este fichero solo para una excepcion? Es por seguir el modelo de api, pero...
    def __init__(self):
        message = "The signature is not authentic"
        super().__init__(message)
