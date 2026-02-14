"""The common module contains common functions and classes used by the other modules."""

import os


# Default output directory
DEFAULT_OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Downloads")

# Environment variable for configuring output directory
OUTPUT_DIR_ENV_VAR = "SKIBA_OUTPUT_DIR"


def hello_world():
    """Prints "Hello World!" to the console."""
    print("Hello World!")


def get_output_directory(output_dir=None):
    """
    Get the output directory for saving files.

    Priority order:
    1. Explicit output_dir parameter (if provided)
    2. SKIBA_OUTPUT_DIR environment variable (if set)
    3. Default ~/Downloads directory

    Args:
        output_dir: Optional explicit output directory path.

    Returns:
        str: The resolved output directory path.

    Raises:
        ValueError: If the resolved directory doesn't exist and can't be created.
    """
    if output_dir is not None:
        resolved_dir = output_dir
    elif OUTPUT_DIR_ENV_VAR in os.environ:
        resolved_dir = os.environ[OUTPUT_DIR_ENV_VAR]
    else:
        resolved_dir = DEFAULT_OUTPUT_DIR

    # Expand user home directory if needed
    resolved_dir = os.path.expanduser(resolved_dir)

    # Create directory if it doesn't exist
    if not os.path.exists(resolved_dir):
        try:
            os.makedirs(resolved_dir)
        except OSError as e:
            raise ValueError(f"Cannot create output directory '{resolved_dir}': {e}")

    return resolved_dir
