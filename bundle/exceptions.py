class IncorrectPassword(Exception):
    def __init__(self):
        message = "The bundle's password is not correct"
        super().__init__(message)
