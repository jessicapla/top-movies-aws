import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_env_var(variable_name: str) -> str:
    """
    Retrieves the value of an environment variable.

    Parameters:
        variable_name (str): The name of the environment variable to retrieve.

    Returns:
        str: The value of the environment variable.

    Raises:
        KeyError: If the environment variable is not set.
    """
    var = os.environ.get(variable_name)
    if not var:
        message = f"Environment variable '{variable_name}' is not set or is empty."
        logger.error(message)
        raise ValueError(message)
    
    return var