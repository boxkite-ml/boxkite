# isort:skip_file
import pkg_resources

for entry_point in pkg_resources.iter_entry_points("console_scripts", "bedrock"):  # noqa
    entry_point.require()  # noqa

import logging
import os
import sys
from pathlib import Path
from typing import List, Mapping, Optional

import click

import docker
from docker.types import Mount
from spanlib.common.exceptions import ConfigInvalidError
from spanlib.infrastructure.span_config.config_objects.command import (
    ShellCommand,
    SparkSubmitCommand,
)
from spanlib.utils.command import generate_command, make_spark_run_steps
from spanlib.utils.paths import training

from .config import BedrockConfig, get_bedrock_config
from .labrun.lab import LabRunner

CONTAINER_AUTH_FILE = "/credentials/application_default_credentials.json"
HADOOP_NAMESPACE_PREFIX = "spark.hadoop.google.cloud.auth.service.account"


@click.group()
def main():
    pass


def get_logger(verbose: bool):
    formatter = logging.Formatter(
        fmt="[%(asctime)s %(levelname)s] %(message)s", datefmt="%H:%M:%S"
    )
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger = logging.getLogger("LabRunner")
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.addHandler(stdout_handler)
    return logger


def get_gcloud_keyfile_path() -> str:
    """Getting gcloud keyfile path

    Reading from a bunch of environment variables to find a keyfile path
    Precedence is taken from
    https://www.terraform.io/docs/providers/google/provider_reference.html

    :return: path to auth_file
    :rtype: str
    """

    env_vars = [
        "GOOGLE_CREDENTIALS",
        "GOOGLE_CLOUD_KEYFILE_JSON",
        "GCLOUD_KEYFILE_JSON",
        "GOOGLE_APPLICATION_CREDENTIALS",
    ]
    for var in env_vars:
        auth_file_path = os.getenv(var, None)
        if auth_file_path:
            break
    if not auth_file_path:
        logging.warning(
            "No env var found specifying credentials, "
            "fallback to user's Google Application Default Credential."
        )
        auth_file_path = str(
            Path.joinpath(Path.home(), ".config/gcloud/application_default_credentials.json")
        )

    assert os.path.isfile(
        auth_file_path
    ), f"Google credential file at {auth_file_path} does not exist"
    return auth_file_path


@main.command()
@click.argument("target_dir")
def train(target_dir: str):
    logging.basicConfig(level=logging.INFO)

    gcloud_keyfile = get_gcloud_keyfile_path()
    docker_client = docker.from_env()
    config = get_bedrock_config(os.path.join(target_dir, "bedrock.hcl"))
    if config.train_config is None:
        raise ConfigInvalidError(resp_details="Train stanza is missing from config file")
    command = make_training_command_from_config(config)
    container = docker_client.containers.run(
        image=config.train_config.image,
        mounts=[
            Mount(source=target_dir, target=training.APP_VOL_MOUNT_PATH, type="bind"),
            Mount(source=target_dir, target=training.ARTEFACT_VOL_MOUNT_PATH, type="bind"),
            Mount(source=gcloud_keyfile, target=CONTAINER_AUTH_FILE, type="bind"),
        ],
        environment=[f"GOOGLE_APPLICATION_CREDENTIALS={CONTAINER_AUTH_FILE}"],
        entrypoint=["/bin/bash", "-x", "-c"],
        command=[command],
        working_dir=training.APP_VOL_MOUNT_PATH,
        detach=True,
        remove=True,
    )
    for line in container.logs(stream=True):
        logging.info(line.strip().decode("utf-8"))


def make_training_command_from_config(config: BedrockConfig):
    if config.train_config is None:
        raise ConfigInvalidError(resp_details="Train stanza is missing from config file")
    config_command = config.train_config.script_commands[0]
    if isinstance(config_command, ShellCommand):
        command = generate_command([config.train_config.install, config_command.content])
    elif isinstance(config_command, SparkSubmitCommand):
        command = generate_command(
            make_spark_run_steps(
                spark_system_config={
                    HADOOP_NAMESPACE_PREFIX + ".enable": "true",
                    HADOOP_NAMESPACE_PREFIX + ".json.keyfile": CONTAINER_AUTH_FILE,
                },
                spark_system_settings={},
                install_script=config.train_config.install,
                command=config_command,
            )
        )
    else:
        raise ConfigInvalidError
    return command


@main.command()
@click.argument("target_dir")
def deploy(target_dir: str):
    logging.basicConfig(level=logging.INFO)

    gcloud_keyfile = get_gcloud_keyfile_path()
    docker_client = docker.from_env()
    config = get_bedrock_config(os.path.join(target_dir, "bedrock.hcl"))
    if config.serve_config is None:
        raise ConfigInvalidError(resp_details="Serve stanza is missing from config file")
    config_command = config.serve_config.script_commands
    command = generate_command([config.serve_config.install, config_command[0].content])
    container = docker_client.containers.run(
        image=config.serve_config.image,
        mounts=[
            Mount(source=target_dir, target=training.APP_VOL_MOUNT_PATH, type="bind"),
            Mount(source=target_dir, target=training.ARTEFACT_VOL_MOUNT_PATH, type="bind"),
            Mount(source=gcloud_keyfile, target=CONTAINER_AUTH_FILE, type="bind"),
        ],
        environment=[
            f"GOOGLE_APPLICATION_CREDENTIALS={CONTAINER_AUTH_FILE}",
            "GRPC_VERBOSITY=INFO",
        ],
        entrypoint=["/bin/bash", "-x", "-c"],
        command=[command],
        working_dir=training.APP_VOL_MOUNT_PATH,
        detach=True,
        remove=True,
    )
    for line in container.logs(stream=True):
        logging.info(line.strip().decode("utf-8"))


# help for click.argument is unsupported: https://github.com/pallets/click/issues/587
# See function doc for more details about params
@main.group()
@click.option("--domain", default=None, help="Domain for Bedrock backend")
@click.option("--token", default=None, help="Personal API token that does not expire easily")
@click.option("-v", "--verbose", is_flag=True, default=False, help="Verbose")
@click.pass_context
def labrun(ctx, domain: Optional[str], token: Optional[str], verbose: bool):
    """
    :param Optional[str] domain: Reference to span backend
    :param Optional[str] token: Personal access token
    :param Optional[bool] verbose: Verbose mode
    """
    logger = get_logger(verbose)
    lab_runner = LabRunner(logger=logger, api_domain=domain, api_token=token)
    ctx.obj = (logger, lab_runner)


def _get_map_from_list_args(params: List[str]) -> Mapping[str, str]:
    output_map = {}
    for param in params:
        kv = param.split("=", 1)
        output_map[kv[0]] = kv[1]
    return output_map


@labrun.command()
@click.argument("target_dir")
@click.argument("config-file-path")
@click.argument("environment")
@click.option(
    "--script-parameters", "-p", multiple=True, help="Script parameters overrides as JSON string"
)
@click.option("--secrets", "-s", multiple=True, help="Secret values")
@click.pass_obj
def submit(
    obj,
    target_dir: str,
    config_file_path: str,
    environment: str,
    script_parameters: List[str],
    secrets: List[str],
) -> None:
    """Run a local directory on Bedrock

    NOTE: Lab runs currently only support training run.
    Lab runs are not stored in database and hence not visible from the UI.

    \b
    Expected environment variables:
    BEDROCK_API_TOKEN=<your personal API token>

    To override script parameters, consider
    -p ALPHA=0.3 -p BETA=0.5

    To specify secret values, consider
    -s DUMMY_SECRET_A=HELLO -s DUMMY_SECRET_B=WORLD

    \b
    :param str target_dir: Where the training files and data reside
    :param str config_file_path: Path to config file, relative to target directory
    :param str environment: Environment for the run
    :param List[str] script_parameters: Script parameter overrides, e.g., ALPHA=4, BETA=5
    :param List[str] secrets: Secret values, e.g., DUMMY_SECRET_A=3
    :return None
    """
    logger, lab_runner = obj
    script_parameters_map = _get_map_from_list_args(script_parameters)
    secrets_map = _get_map_from_list_args(secrets)
    lab_runner.run(
        target_dir=target_dir,
        config_file_path=config_file_path,
        environment_id=environment,
        script_parameters=script_parameters_map,
        secrets=secrets_map,
    )


@labrun.command()
@click.argument("run_id")
@click.argument("step_id")
@click.argument("run_token")
@click.pass_obj
def logs(obj, run_id: str, step_id: str, run_token: str) -> None:
    logger, lab_runner = obj
    lab_runner.stream_logs(run_id, step_id, run_token)


@labrun.command()
@click.argument("run_id")
@click.argument("run_token")
@click.pass_obj
def artefact(obj, run_id: str, run_token: str) -> None:
    logger, lab_runner = obj
    url = lab_runner.get_artefact_url(run_id, run_token)
    print(url)
