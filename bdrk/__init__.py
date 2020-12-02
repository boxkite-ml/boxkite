import sys

from bdrk.backend import v1  # noqa: F401 F403
from bdrk.backend.utils import v1 as v1_util  # noqa: F401 F403

# Creating alias for backward compatible calls
sys.modules['bdrk.v1'] = v1
sys.modules['bdrk.v1_util'] = v1_util

import logging
from typing import Optional

from bdrk.tracking.client import BedrockClient
from bdrk.utils.utils import check_param
from bdrk.utils.vars import Constants
from spanlib.infrastructure.kubernetes.env_var import API_TOKEN, BEDROCK_PROJECT_ID

# For convenient calls
from .tracking.training_pipeline import *  # noqa: F401 F403

# The only global instance to store general-purpose global variables
# From other modules, do not access this directly as it will actually copy the None value
# Always access this global var using bdrk.bedrock_client
bedrock_client = None

# Logger
_logger = logging.getLogger(Constants.MAIN_LOG)

__schema_version__ = "1"


def init(
    access_token: Optional[str] = None, project_id: Optional[str] = None,
):
    """Initialise Bedrock library and project

    Args:
        access_token (Optional[str], optional): personal access token. Defaults to None.
        project_id (Optional[str], optional): root project. Defaults to None.
    """
    access_token = check_param(
        param_name="access_token", param_var=access_token, env_name=API_TOKEN,
    )
    project_id = check_param(
        param_name="project_id", param_var=project_id, env_name=BEDROCK_PROJECT_ID,
    )

    # Initialize BedrockClient
    global bedrock_client
    bedrock_client = BedrockClient(access_token=access_token, project_id=project_id)

    # Create project if it does not exist
    bedrock_client.create_project_if_not_exist(project_id)

    _logger.info(f"BedrockClient initialized on project={project_id}")
