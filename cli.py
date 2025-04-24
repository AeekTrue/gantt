from storage import TaskStorageAware, Task

def display_tasks(tasks: list[Task], filter_func):
    id_column_width = 3
    title_column_width = 20
    for i, task in enumerate(tasks):
        if filter_func(task):
            print(f"{i+1:>{id_column_width-1}} {task.title:<{title_column_width}}")

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
