class ApplicationException(Exception):
    pass


class InvalidCredentialsException(ApplicationException):
    def __init__(self, message="Invalid password"):
        super().__init__(message)


class InvalidAccessTokenException(ApplicationException):
    def __init__(self, message="Invalid access token"):
        super().__init__(message)


class UserNotFound(ApplicationException):
    def __init__(self, message="User not found"):
        super().__init__(message)


class UserAlreadyExists(ApplicationException):
    def __init__(self, message="User already exists"):
        super().__init__(message)