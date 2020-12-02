import importlib
from typing import Mapping, Optional

import hcl

from spanlib.common.exceptions import ConfigInvalidError
from spanlib.infrastructure.span_config.config_objects.batch_score_config import BatchScoreConfig
from spanlib.infrastructure.span_config.config_objects.serve_config import ServeConfig
from spanlib.infrastructure.span_config.config_objects.training_config import TrainingConfig


class SpanConfig:
    """Configuration object for different running entities"""

    def __init__(
        self,
        train_config: Optional[TrainingConfig],
        serve_config: Optional[ServeConfig],
        batch_score_config: Optional[BatchScoreConfig],
    ):
        self.train_config = train_config
        self.serve_config = serve_config
        self.batch_score_config = batch_score_config

    @staticmethod
    def create_from_dictionary(config_dict: Mapping) -> "SpanConfig":
        """Create a validated subclass object based on "version" key in config_dict

        Dynamically load mapper based on config file version
        """
        try:
            version = config_dict["version"]
        except KeyError:
            raise ConfigInvalidError(resp_details="'version' is required in config file.")

        mapper_mod_name = f"...v{version.replace('.', '_')}.mapper"
        mapper_mod = importlib.import_module(mapper_mod_name, package=__name__)
        mapper_subclass = getattr(mapper_mod, "ConfigMapper")
        return mapper_subclass.validate_and_create_config_object(config_dict)

    @staticmethod
    def create_from_str(config_str: str) -> "SpanConfig":
        return SpanConfig.create_from_dictionary(hcl.loads(config_str))
