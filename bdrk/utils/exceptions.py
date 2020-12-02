"""
Client library exceptions.
"""

from spanlib.common.exceptions import SpanError


class BedrockClientNotFound(SpanError):
    resp_message = "BedrockClient has not been initialized."


class MultipleRunContextError(SpanError):
    resp_message = "You can only start 1 pipeline run at 1 time."


class NoRunContextError(SpanError):
    resp_message = "Action must be wrapped inside a run context."


class DataMismatchError(SpanError):
    resp_message = "Data mismatch error."
