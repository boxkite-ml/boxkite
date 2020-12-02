from spanlib.infrastructure.span_config.base_mapper import SchemaMapper
from spanlib.infrastructure.span_config.config_objects import SpanConfig

from .batch_score_mapper import V1BatchScoreConfigMapper
from .serve_mapper import V1ServeConfigMapper
from .train_mapper import V1TrainConfigMapper


class ConfigMapper(SchemaMapper):
    @classmethod
    def create_config_object(cls, config_dict) -> SpanConfig:
        cls._validate(config_dict)
        train_dict = config_dict.get("train")
        serve_dict = config_dict.get("serve")
        batch_score_dict = config_dict.get("batch_score")
        return SpanConfig(
            train_config=V1TrainConfigMapper.create_config_object(train_dict)
            if train_dict
            else None,
            serve_config=V1ServeConfigMapper.create_config_object(serve_dict)
            if serve_dict
            else None,
            batch_score_config=V1BatchScoreConfigMapper.create_config_object(batch_score_dict)
            if batch_score_dict
            else None,
        )
