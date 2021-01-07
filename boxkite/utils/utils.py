import os
from typing import Any


def check_param(param_var: Any, env_name: str, param_name: str = "") -> str:
    """Some parameter uses the environment var as a default value.
    This function is to get the value from either params or env_var,
    and to check if there is conflict data.

    Args:
        param_var (Any): given paramter
        env_name (str): target environment variable
        param_name (str): name of of params, for logging purpose only
    """
    env_var = os.environ.get(env_name)
    if param_var is None and env_var is None:
        raise ValueError(f"param.{param_name} or env.{env_name} must be present")
    if param_var and env_var and param_var != env_var:
        raise ValueError(
            f"Mismatching data: param.{param_name}={param_var}, env.{env_name}={env_var}"
        )
    return str(param_var or env_var)
