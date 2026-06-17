class AppException(Exception):
    """Base exception for all application errors."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class NetworkException(AppException):
    """Exception raised for network-related errors."""
    pass

class APIException(AppException):
    """Exception raised when the API returns an error response."""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code
