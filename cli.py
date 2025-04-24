from storage import TaskStorageAware


class CLI(TaskStorageAware):
    def __init__(self):
        super().__init__()
        self.commands = dict()

    def execute_command(self, command, args):
        if command in self.commands:
            self.commands[command](self.storage, *args)
        else:
            raise ValueError(f"Unknown command: {command}")

    def command(self, func):
        self.commands[func.__name__] = func
        return func

cli = CLI()
