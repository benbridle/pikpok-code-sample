class BaseError(Exception):
    """Never call this directly, instead use an exception more
    specific to the situation."""

    def __init__(self, message=None):
        """Allows overwriting the default error message with a more specific message."""
        self.message = message or self.message


# ----------------------------------------------------------------
# Base user and server errors


class ServerError(BaseError):
    """Base error for when the server runs into an issue."""

    status_code = 500
    message = "Generic internal server error."


class UserError(BaseError):
    """Base error for when the user uses the API incorrectly."""

    status_code = 400
    message = "Generic API usage error."


# ----------------------------------------------------------------
# Bad requests


class BadRequestError(UserError):
    status_code = 400
    message = "Bad request"


class MissingBodyError(BadRequestError):
    message = "No request body was sent with the request."


class MissingFieldError(BadRequestError):
    def __init__(self, field_name):
        self.message = f"The field '{field_name}' was missing from the request body."


class MalformedFieldError(BadRequestError):
    message = "The value of a field in the request body is malformed."

    pass


# ----------------------------------------------------------------
# Other user errors


class ResourceAlreadyExistsError(UserError):
    status_code = 409
    message = "The resource being created already exists."


class ResourceNotFoundError(UserError):
    status_code = 404
    message = "The specified resource was not found."


class UnauthorizedAccessError(UserError):
    status_code = 403
    message = "You are not authorized to complete the current action."
