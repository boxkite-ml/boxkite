from typing import Any, Dict, List, Mapping, Optional

from spanlib.common.exceptions import ConfigInvalidError
from spanlib.infrastructure.span_config.base_mapper.base_mapper import BaseMapper
from spanlib.infrastructure.span_config.config_objects import StepConfig
from spanlib.infrastructure.span_config.config_objects.command import (
    Command,
    CommandType,
    ShellCommand,
    SparkSubmitCommand,
)
from spanlib.utils.common import as_dataclass


class V1StepConfigMapper(BaseMapper):
    @staticmethod
    def create_config_object(config_dict) -> StepConfig:
        mapper = V1StepConfigMapper(config_dict)
        return as_dataclass(mapper, StepConfig, install=mapper.install_commands.content)

    @property
    def name(self) -> str:
        keys = self.config_dict.keys()
        if len(keys) != 1:
            raise ConfigInvalidError(resp_details=f"Step name is ambiguous: {', '.join(keys)}")
        return list(keys)[0]

    @property
    def image(self) -> str:
        # reraise didn't work with property, let's check directly
        img = self.config_dict[self.name].get("image", None)
        if not img:
            raise ConfigInvalidError(resp_details=f"Image is not specified for step {self.name}")
        return img

    @property
    def install_commands(self) -> ShellCommand:
        return ShellCommand(content=self.config_dict[self.name].get("install", []))

    @property
    def script_commands(self) -> List[Command]:
        script_stanza = self._script_stanza
        commands = []
        for command_dict in script_stanza:
            for command_type, command_value in command_dict.items():
                command: Command
                if command_type == CommandType.SHELL:
                    command = ShellCommand(content=command_value)
                elif command_type == CommandType.SPARK_SUBMIT:
                    command = SparkSubmitCommand(
                        script=command_value.get("script"),
                        conf=command_value.get("conf", {}),
                        settings=command_value.get("settings", {}),
                    )
                else:
                    raise ConfigInvalidError("Unrecognized command")
                commands.append(command)
        return commands

    @property
    def _script_stanza(self) -> List[Dict[str, Any]]:
        script = self.config_dict[self.name]["script"]
        if len(script) == 0 or isinstance(script[0], str):
            return []
        return script

    @property
    def _spark_stanza(self) -> Optional[Dict[str, Any]]:
        return self.config_dict[self.name].get("spark", None)

    @property
    def parameters(self) -> Mapping[str, str]:
        return self.config_dict[self.name].get("parameters", {})

    @property
    def secret_names(self) -> List[str]:
        return self.config_dict[self.name].get("secrets", [])

    @property
    def resources(self) -> List[str]:
        return self.config_dict[self.name].get("resources", {})

    @property
    def depends_on(self) -> List[str]:
        return self.config_dict[self.name].get("depends_on", [])
