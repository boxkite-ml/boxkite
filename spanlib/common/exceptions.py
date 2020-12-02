import logging
import re
from asyncio import AbstractEventLoop
from logging import Logger, getLogger
from typing import Callable, Dict, List, Mapping, Optional, Union

_underscorer1 = re.compile(r"([A-Z]+)([A-Z][a-z])")
_underscorer2 = re.compile(r"([a-z\d])([A-Z])")


def camel_to_snake(s: str) -> str:
    return _underscorer2.sub(r"\1_\2", _underscorer1.sub(r"\1_\2", s)).lower()


class SpanError(Exception):
    """Span exception.

    NOTE:
    - `status_code`, `resp_message`, and `resp_details` will be used to populate the response that
      the end user receives.
    - `code`, `status_code` and `resp_message` are completely determined by the error type.
    - `resp_details` is an optional custom message that is shown to the end user together
      with `resp_message`. It is a keyword-only argument to make it explicit that we are passing
      info to the end user.
    - `parameter_message` is an optional key-value mapping for indicating parameter-specific errors
      . A common use case for this is annotating form fields with error messages. It is a
      keyword-only argument to make it explicit that we are passing info to the end user.
    - `debug_message` will be used to initialise the base Exception class. We deliberately
      restrict the `SpanError` interface to allow up to one positional argument (v.s. using
      `*args`) in order to align with suggested practice. (c.f.
      https://www.python.org/dev/peps/pep-0352/, especially section on "retracted-ideas")
      At the same time, we do not require this argument to be keyword-only, so that usage can
      remain consistent with built-in exceptions.

    Example usage:
    ```
    raise SpanError(debug_message="My message")  # OK
    raise SpanError("My message")                # OK - equivalent to above

    raise SpanError("My message", resp_details="Details")  # OK
    raise SpanError("My message", "Details")               # Not OK - resp_details is keyword-only
    ```

    :param str debug_message: Debug message, defaults to "".
    :param str resp_details: Response additional details, defaults to "".
    :param parameter_messages: Parameter-specific error messages, defaults to `None`/`{}`.

    :cvar int log_level: Log level.
    :cvar str status_code: Response status code.
    :cvar str code: Error code used to coordinate error types between client and server.
    :cvar str message: Response message.
    :ivar str resp_details: Response additional details.
    """

    def __init__(
        self,
        debug_message: str = "",
        *,
        resp_details: str = "",
        parameter_messages: Optional[Union[List[str], Mapping[str, List[str]]]] = None,
    ):
        super().__init__(debug_message)
        self.debug_message = debug_message

        self.parameter_messages: Mapping[str, List[str]]
        if isinstance(parameter_messages, List):
            self.parameter_messages = {"error": parameter_messages}
        else:
            self.parameter_messages = parameter_messages or {}

        self.resp_details = resp_details
        logging.getLogger("aiohttp-exceptions").debug(self)

    def __str__(self):
        return f"{self.resp_message} details={self.resp_details}, debug={self.debug_message}"

    resp_message = "Error encountered."
    status_code = 500
    log_level = logging.DEBUG

    @property
    def code(self) -> str:
        return camel_to_snake(self.__class__.__name__)

    def to_dict(self) -> Dict:
        return {
            k: v
            for k, v in {
                "object": "error",
                "code": self.code,
                "message": self.resp_message,
                "details": self.resp_details if self.resp_details else None,
                "parameter_messages": self.parameter_messages if self.parameter_messages else None,
            }.items()
            if v is not None
        }


class ConfigInvalidError(SpanError):
    resp_message = "Config invalid."
    status_code = 422


class SchemaNotFoundError(SpanError):
    resp_message = "Bedrock hcl schema file not found."
    status_code = 500
    log_level = logging.ERROR


class DataClassConversionError(SpanError):
    log_level = logging.ERROR


class IOError(SpanError):
    resp_message = "IO error."
    status_code = 500
    log_level = logging.ERROR


class FatalError(Exception):
    pass


class LeaderElectionError(SpanError):
    resp_message = "Failed to acquire leader."
    status_code = 500
    log_level = logging.ERROR


def fatal_error_handler(
    func: Callable[[], None], logger: Optional[Logger] = None
) -> Callable[[AbstractEventLoop, Dict], None]:
    """Returns asyncio event loop exception handler that logs the exception context
    and calls func if exception represents a FatalError.

    :param Callable[[], None] func: Function to call on FatalError.
    :param Logger, optional logger: Exception logger, defaults to root logger.
    :return Callable[[AbstractEventLoop, Dict], None]: Asyncio event loop exception handler.
    """
    _logger = logger or getLogger()

    def handler(loop: AbstractEventLoop, context: Dict):
        message = context.get("message")
        exc: Optional[Exception] = context.get("exception")

        is_fatal_error = isinstance(exc, FatalError)

        error_type = "FATAL ERROR" if is_fatal_error else "Error"
        _logger.error(
            f"{error_type} in event loop: message={message}, exc={exc}",
            exc_info=exc,
            extra={"context": context},
        )

        if is_fatal_error:
            func()

    return handler
