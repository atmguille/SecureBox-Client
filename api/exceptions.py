class SignatureNotAuthentic(Exception):
    def __init__(self):
        message = "The signature is not authentic"
        super().__init__(message)


class PrivateKeyNotFound(Exception):
    def __init__(self):
        message = "RSA private key was not found"
        super().__init__(message)


class WrongTokenException(Exception):
    def __init__(self):
        message = "The token is not valid"
        super().__init__(message)


class ExpiredTokenException(Exception):
    def __init__(self):
        message = "The token has expired. You have to request a new one"
        super().__init__(message)


class WrongHeaderException(Exception):
    def __init__(self):
        message = "The header's format is incorrect"
        super().__init__(message)


class FileTooLargeException(Exception):
    def __init__(self):
        message = "The file size is bigger than 50 Kb"
        super().__init__(message)


class IncorrectFileIDException(Exception):
    def __init__(self):
        message = "The provided ID is not correct or you don't have enough permission to see it"
        super().__init__(message)


class TooManyFilesException(Exception):
    def __init__(self):
        message = "You cannot store more than 20 files"
        super().__init__(message)


class UserNotFoundException(Exception):
    def __init__(self):
        message = "No user has the provided ID"
        super().__init__(message)


# TODO: WTF
class WTFException(Exception):
    def __init__(self):
        message = "No clue about what this error is (something about the function search?"
        super().__init__(message)


class IncorrectArgsException(Exception):
    def __init__(self):
        message = "The HTTP arguments are not correct"
        super().__init__(message)


api_exceptions = {
    "TOK1": WrongTokenException,
    "TOK2": ExpiredTokenException,
    "TOK3": WrongHeaderException,
    "FILE1": FileTooLargeException,
    "FILE2": IncorrectFileIDException,
    "FILE3": TooManyFilesException,
    "USER_ID1": UserNotFoundException,
    "USER_ID2": WTFException,
    "ARGS1": IncorrectArgsException
}