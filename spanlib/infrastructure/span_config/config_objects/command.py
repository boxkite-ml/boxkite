from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class CommandType(str, Enum):
    SHELL = "sh"
    SPARK_SUBMIT = "spark-submit"


@dataclass(frozen=True)
class Command:
    pass


@dataclass(frozen=True)
class SparkSubmitCommand(Command):
    script: str
    conf: Dict[str, str]
    settings: Dict[str, str]


@dataclass(frozen=True)
class ShellCommand(Command):
    content: List[str]
