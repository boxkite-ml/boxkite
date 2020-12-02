from typing import List, Mapping, Set

from spanlib.common.exceptions import ConfigInvalidError
from spanlib.infrastructure.span_config.base_mapper.base_mapper import BaseMapper
from spanlib.infrastructure.span_config.config_objects import StepConfig, TrainingConfig
from spanlib.infrastructure.span_config.config_objects.command import Command, ShellCommand
from spanlib.infrastructure.span_config.v1_0.step_mapper import V1StepConfigMapper
from spanlib.utils.common import as_dataclass


class V1TrainConfigMapper(BaseMapper):
    @staticmethod
    def create_config_object(config_dict) -> TrainingConfig:
        mapper = V1TrainConfigMapper(config_dict)
        return as_dataclass(mapper, TrainingConfig, install=mapper.install_commands.content)

    @property
    def image(self) -> str:
        if len(self.steps) == 0:
            raise ConfigInvalidError
        return self.steps[0].image

    @property
    def install_commands(self) -> ShellCommand:
        if len(self.steps) == 0:
            raise ConfigInvalidError
        return ShellCommand(content=self.steps[0].install)

    @property
    def script_commands(self) -> List[Command]:
        if len(self.steps) == 0:
            raise ConfigInvalidError
        return self.steps[0].script_commands

    @property
    def parameters(self) -> Mapping[str, str]:
        return self.config_dict.get("parameters", {})

    @property
    def secret_names(self) -> List[str]:
        return self.config_dict.get("secrets", [])

    @property
    def resources(self) -> Mapping[str, str]:
        # To get the resources of the first step as the resources of a pipeline run
        if len(self.steps) == 0:
            raise ConfigInvalidError
        return self.steps[0].resources

    @property
    def steps(self) -> List[StepConfig]:
        # TODO: [BDRK-1802]
        # The behaviour of HCL v1 is that when there are multiple steps defined, it will map
        # all steps to a list of dictionaries, but if there's only one step, it maps it to a
        # single dictionary. This behaviour is changed in v2 but we're not using it yet.
        if self.config_dict.get("step") and type(self.config_dict["step"]) is dict:
            return [V1StepConfigMapper.create_config_object(self.config_dict["step"])]

        step_names: Set[str] = set()
        step_objects: List[StepConfig] = []
        for step in self.config_dict.get("step", []):
            step_object = V1StepConfigMapper.create_config_object(step)
            if step_object.name in step_names:
                raise ConfigInvalidError(resp_details=f"Duplicate step name: {step_object.name}")
            step_objects.append(step_object)
            step_names.add(step_object.name)
        return step_objects
