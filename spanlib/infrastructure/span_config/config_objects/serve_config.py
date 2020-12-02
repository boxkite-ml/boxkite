from dataclasses import dataclass, field
from typing import List, Mapping

from spanlib.infrastructure.span_config.config_objects.command import ShellCommand


@dataclass(frozen=True)
class ServeConfig:
    image: str
    install: List[str]
    script_commands: List[ShellCommand]
    parameters: Mapping[str, str]
    secret_names: List[str]


@dataclass(frozen=True)
class ExpressServeConfig(ServeConfig):
    image: str
    install: List[str] = field(default_factory=list)
    script_commands: List[ShellCommand] = field(default_factory=list)
    parameters: Mapping[str, str] = field(default_factory=dict)
    secret_names: List[str] = field(default_factory=list)
