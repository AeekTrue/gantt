import code
from types import ModuleType
from typing import Optional, Dict, List
from gantt import parser, CommandManager
import commands
import os

readline: Optional[ModuleType]
try:
    import readline
except ImportError:
    readline = None


class Repl(code.InteractiveConsole):
    def runsource(self, source, filename="<input>", symbol="single"):
        # TODO: Integrate your compiler/interpreter
        parser(source)
        return False

class Completer:
    def __init__(self, env: Dict[str, object]) -> None:
        self.env: Dict[str, object] = env
        self.matches: List[str] = []

    def complete(self, text: str, state: int) -> Optional[str]:
        if state == 0:
            # Some implementations check if text.strip() is empty but I can't
            # figure out how to get text to start or end with whitespace.
            options = (key for key in self.env.keys() if key.startswith(text))
            self.matches = sorted(options)
        try:
            return self.matches[state]
        except IndexError:
            return None


REPL_HISTFILE = 'dev-history' # os.path.expanduser(f".{APPNAME}-history")  # arbitrary name
REPL_HISTFILE_SIZE = 10000
if readline and os.path.exists(REPL_HISTFILE):
    readline.read_history_file(REPL_HISTFILE)

if readline:
    readline.set_completer(Completer(CommandManager.commands).complete)
    readline.parse_and_bind("tab: complete")

repl = Repl()
repl.interact(banner='Welcome to gantt chart by Aeek True!', exitmsg='')

if readline:
    readline.set_history_length(REPL_HISTFILE_SIZE)
    readline.write_history_file(REPL_HISTFILE)
