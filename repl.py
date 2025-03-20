import code
from types import ModuleType
from typing import Optional
from gantt import parser
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

REPL_HISTFILE = 'dev-history' # os.path.expanduser(f".{APPNAME}-history")  # arbitrary name
REPL_HISTFILE_SIZE = 1000
if readline and os.path.exists(REPL_HISTFILE):
    readline.read_history_file(REPL_HISTFILE)

repl = Repl()
repl.interact(banner='Welcome to gantt chart by Aeek True!', exitmsg='')

if readline:
    readline.set_history_length(REPL_HISTFILE_SIZE)
    readline.write_history_file(REPL_HISTFILE)
