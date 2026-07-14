"""
Custom exceptions, caught centrally by a handler in main.py so every
error in the API - whether it's a built-in HTTPException or one of
these - comes back to the client in the same consistent JSON shape.
"""


class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


class DuplicateUsernameError(AppException):
    def __init__(self, username: str):
        super().__init__(status_code=409, detail=f"Username '{username}' is already taken")


class DuplicateEmailError(AppException):
    def __init__(self, email: str):
        super().__init__(status_code=409, detail=f"Email '{email}' is already registered")
