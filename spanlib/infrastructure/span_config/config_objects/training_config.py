from dataclasses import dataclass
from typing import List, Mapping

from spanlib.infrastructure.span_config.config_objects.command import Command
from spanlib.infrastructure.span_config.config_objects.step_config import StepConfig


@dataclass(frozen=True)
class TrainingConfig:
    image: str
    install: List[str]
    script_commands: List[Command]
    parameters: Mapping[str, str]
    secret_names: List[str]
    steps: List[StepConfig]
    resources: Mapping[str, str]
