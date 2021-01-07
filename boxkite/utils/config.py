from typing import Dict

import hcl

from spanlib.common.exceptions import ConfigInvalidError
from spanlib.infrastructure.span_config.config_objects.span_config import (
    SpanConfig as BedrockConfig,
)


def get_bedrock_config(path: str) -> BedrockConfig:
    try:
        with open(path) as f:
            span_config: Dict = hcl.loads(f.read())
    except ValueError as exc:
        raise ConfigInvalidError(resp_details="Malformed .hcl file.") from exc
    return BedrockConfig.create_from_dictionary(span_config)
