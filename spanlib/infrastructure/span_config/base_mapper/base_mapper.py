import os
import sys
from abc import ABC
from typing import Dict, List

import hcl
import jsonschema

from spanlib.common.exceptions import ConfigInvalidError, SchemaNotFoundError
from spanlib.infrastructure.span_config.config_objects import SpanConfig


class BaseMapper:
    def __init__(self, config_dict: Dict):
        self.config_dict = config_dict


class SchemaMapper(BaseMapper, ABC):
    """Represent a complete mapper able to parse a config file version

    """

    @classmethod
    def validate_and_create_config_object(cls, config_dict) -> SpanConfig:
        cls._validate(config_dict)
        return cls.create_config_object(config_dict)

    @staticmethod
    def create_config_object(config_dict) -> SpanConfig:
        raise NotImplementedError

    @classmethod
    def _schema_dict(cls):
        subclass_filepath = sys.modules[cls.__module__].__file__
        subclass_dirpath = os.path.dirname(subclass_filepath)
        schema_filepath = os.path.join(subclass_dirpath, "schema.hcl")

        try:
            with open(schema_filepath, "r") as f:
                return hcl.load(f)
        except Exception as exc:
            raise SchemaNotFoundError from exc

    @classmethod
    def _validate(cls, config_dict):
        # At this point the HCL config file has already been deemed to be syntatically correct
        # and parsed into self.config_dict
        validator = jsonschema.Draft7Validator(cls._schema_dict())
        errors: List[jsonschema.ValidationError] = sorted(
            list(validator.iter_errors(config_dict)), key=jsonschema.exceptions.relevance
        )

        # TODO: [BDRK-362] https://basis-ai.atlassian.net/browse/BDRK-362
        # Richer error messages will be great to have, but for now we dump everything
        # in ConfigInvalidError.message
        if errors:
            error_messages = []
            for error in errors:
                config_path = ".".join([str(fragment) for fragment in error.relative_path])
                error_message = f"{config_path}: {error.message}"
                error_messages.append(error_message)

            combined_message = f"Invalid configuration file: {'; '.join(error_messages)}"
            raise ConfigInvalidError(resp_details=combined_message)
