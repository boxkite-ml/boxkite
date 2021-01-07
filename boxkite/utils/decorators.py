import logging
import os
from functools import wraps

from spanlib.infrastructure.kubernetes.env_var import BEDROCK_RUN_TRIGGER

from .vars import Constants, RunTriggerEnv

_logger = logging.getLogger(Constants.MAIN_LOG)


def bedrock_env_skipped(func):
    """Some functions are no-op in the Bedrock orchestrated environment.
    This decorator will read the env var to check.
    """

    @wraps(func)
    def decorated(*args, **kwargs):
        if os.environ.get(BEDROCK_RUN_TRIGGER) == RunTriggerEnv.BEDROCK:
            _logger.warning(f"{func.__name__} is skipped on Bedrock orchestrated environment")
            return None
        return func(*args, **kwargs)

    return decorated
