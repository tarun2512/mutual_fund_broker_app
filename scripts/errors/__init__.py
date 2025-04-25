class ErrorMessages:
    ERR002 = "Data Not Found"
    ERR003 = "User Record Not Found"


class JobCreationError(Exception):
    """
    Raised when a Job Creation throws an exception.

    Job Creation happens by adding a record to Mongo.
    """


class UnknownError(Exception):
    pass


class DuplicateSpaceNameError(Exception):
    pass


class KairosDBError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class ImageValidation(Exception):
    pass


class ILensError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

    """
    Base Error Class
    """


class NameExists(Exception):
    pass


class InputRequestError(ILensError):
    pass


class IllegalTimeSelectionError(ILensError):
    pass


class DataNotFound(Exception):
    pass


class AuthenticationError(ILensError):
    """
    JWT Authentication Error
    """


class CustomError(ILensError):
    pass


class TooManyRequestsError(Exception):
    pass


class InvalidPasswordError(ILensError):
    pass


class VariableDelayError(ILensError):
    pass


class FixedDelayError(ILensError):
    pass


class LicenceValidationError(Exception):
    pass


class UserNotFound(ILensError):
    pass


class JWTDecodingError(Exception):
    pass


class DuplicateReportNameError(Exception):
    pass


class PathNotExistsException(Exception):
    pass


class ImplementationError(Exception):
    pass


class UserRoleNotFoundException(Exception):
    pass


class CustomAppError:
    FAILED_TO_SAVE = "Failed to save app"
