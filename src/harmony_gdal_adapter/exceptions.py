"""Contains custom exceptions specific to the Harmony GDAL Adapter service.

These exceptions are intended to allow for clearer messages to the
end-user and easier debugging of expected errors that arise during an
invocation of the service.

"""

from harmony_service_lib.exceptions import HarmonyException, NoRetryException


class HGANoRetryException(NoRetryException):
    """Base class for exceptions in the Harmony GDAL Adapter.

    This exception is inherited by errors that should not cause Harmony to
    retry the HGA step in a workflow chain, because it is known they will fail
    upon that retry.

    """

    def __init__(self, message: str | None = None) -> None:
        """Initialize a new HGANoRetryException instance.

        Args:
            message (str, optional): The message associated with the exception.
        """
        super().__init__(message)


class DownloadError(HarmonyException):
    """Raised when the Harmony GDAL Adapter cannot retrieve input data.

    This does not inherit from NoRetryException, as it may be due to intermittent
    network issues.

    """

    def __init__(self, url: str, message: str) -> None:
        """Initialize a new DownloadError instance.

        Args:
            url (str): The URL associated with the exception.
            message (str): The message associated with the exception.
        """
        super().__init__(f'Could not download resource: {url}, {message}')


class UnsupportedFileFormatError(HGANoRetryException):
    """Raised when the input file format is cannot processed by the HGA."""

    def __init__(self, file_format: str) -> None:
        """Initialize a new UnsupportedFileFormatError instance.

        Args:
            file_format (str): The file format associated with the exception.
        """
        super().__init__(f'Cannot process unsupported file format: "{file_format}"')


class IncompatibleVariablesError(HGANoRetryException):
    """Raised when the dataset variables requested are not compatible.

    i.e. they have different projections, geotransforms, sizes or data types.

    """

    def __init__(self, message: str) -> None:
        """Initialize a new IncompatibleVariablesError instance.

        Args:
            message (str): The message associated with the exception.
        """
        super().__init__(f'Incompatible variables: {message}')


class MissingVariableError(HGANoRetryException):
    """Raised when a requested variable is absent from the input GeoTIFF."""

    def __init__(self, variable_name: str) -> None:
        """Initialize a new MissingVariableError instance.

        Args:
            variable_name (str): The missing variable name associated with the exception.
        """
        super().__init__(f'Missing variable in input file: {variable_name}')


class InvalidProjectionError(HGANoRetryException):
    """Raised when the requested output projection is invalid"""

    def __init__(self, requested_projection: str) -> None:
        """Initialize a new InvalidProjectionError instance.

        Args:
            requested_projection (str): The requested projection as a string.
        """
        super().__init__(f'Requested projection is invalid: {requested_projection}')


class InputValidationError(HGANoRetryException):
    """Raised when the KCL recipe fails"""

    def __init__(self, error: str) -> None:
        """Initialize a new InputValidationError

        Args:
            error (str): The JSON data given by the error.
        """
        super().__init__(f'{error}')
