from dataclasses import dataclass
from typing import List, Mapping

from spanlib.infrastructure.span_config.config_objects.command import Command


@dataclass(frozen=True)
class StepConfig:
    name: str
    image: str
    install: List[str]
    script_commands: List[Command]
    depends_on: List[str]
    resources: Mapping[str, str]
