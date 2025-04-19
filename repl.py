# Command line interface for managing tasks
import os
import code
from types import ModuleType
from typing import Optional

from storage import TaskStorageAware

readline: Optional[ModuleType]
try:
    import readline
except ImportError:
    logger.warning('Can not import "readline". History and autocomplete may not work.')
    readline = None


class Repl(TaskStorageAware, code.InteractiveConsole):
    def runsource(self, source, filename='<console>', symbol='single'):
        try:
            result = eval(source, {}, {'storage': self.storage})
            print(result)
        except Exception as e:
            print(f"Error: {e}")
