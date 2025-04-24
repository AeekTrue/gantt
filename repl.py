# Command line interface for managing tasks
import os
import code
import datetime
import shlex
from types import ModuleType
from typing import Optional
from loguru import logger

from storage import TaskStorageAware

readline: Optional[ModuleType]
try:
    import readline
except ImportError:
    logger.warning('Can not import "readline". History and autocomplete may not work.')
    readline = None


def parse_command(command_str):
    """
    Parse a Bash-like command string into a list of arguments.

    Args:
    command_str (str): The command string to parse.

    Returns:
    list: A list of parsed command components.
    """
    try:
        # Use shlex to split the command string
        parsed_components = shlex.split(command_str)
        return parsed_components
    except ValueError as e:
        # Handle any parsing errors (e.g., unmatched quotes)
        print(f"Error parsing command string: {e}")
        return []


class Namespace:
    def __getitem__(self, key: str):
        return len(key)


ns = Namespace()
class Repl(TaskStorageAware, code.InteractiveConsole):
    def runsource(self, source, filename='<console>', symbol='single'):
        try:
            parsed_command = parse_command(source)
            if parsed_command == []:
                return False
            command, *args = parsed_command
            logger.debug(f"Command: {command}, Args: {args}")
        except Exception as e:
            print(f"Error: {e}")
