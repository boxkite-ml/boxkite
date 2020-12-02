from typing import Any, Dict, List, Mapping

from spanlib.common.exceptions import ConfigInvalidError
from spanlib.infrastructure.span_config.base_mapper.base_mapper import BaseMapper
from spanlib.infrastructure.span_config.config_objects import ServeConfig
from spanlib.infrastructure.span_config.config_objects.command import CommandType, ShellCommand
from spanlib.utils.common import as_dataclass


class V1ServeConfigMapper(BaseMapper):
    @staticmethod
    def create_config_object(config_dict) -> ServeConfig:
        mapper = V1ServeConfigMapper(config_dict)
        return as_dataclass(mapper, ServeConfig, install=mapper.install_commands)

    @property
    def install_commands(self) -> ShellCommand:
        return self.config_dict.get("install", [])

    @property
    def script_commands(self) -> List[ShellCommand]:
        script_stanza = self._script_stanza
        commands = []
        for command_dict in script_stanza:
            command: ShellCommand
            for command_type, command_value in command_dict.items():
                if command_type == CommandType.SHELL:
                    command = ShellCommand(content=command_value)
                else:
                    raise ConfigInvalidError("Unrecognized command")
                commands.append(command)
        return commands

    @property
    def _script_stanza(self) -> List[Dict[str, Any]]:
        script = self.config_dict["script"]
        if len(script) == 0 or isinstance(script[0], str):
            return []
        return script

    @property
    def image(self) -> str:
        return self.config_dict.get("image", "scratch")

    @property
    def parameters(self) -> Mapping[str, str]:
        return self.config_dict.get("parameters", {})

    @property
    def secret_names(self) -> List[str]:
        return self.config_dict.get("secrets", [])
