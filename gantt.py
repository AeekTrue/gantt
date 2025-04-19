from typing import Dict, List, Any, Callable
import datetime as dt
import colorama
import pydantic
import json

from storage import Task, TaskStorage


DATE_FORMAT = "%d.%m.%y"
digits = {
    '0':'🯰',
    '1':'🯱',
    '2':'🯲',
    '3':'🯳',
    '4':'🯴',
    '5':'🯵',
    '6':'🯶',
    '7':'🯷',
    '8':'🯸',
    '9':'🯹',
}
week_days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']

class ShellException(Exception):
    pass


def lom(date):
    # last date of month
    date = date.replace(day=1)
    date = date.replace(month=date.month+1)
    date = date - dt.timedelta(days=1)
    return date.day

def date_range(start: dt.datetime,  stop: dt.datetime, step: dt.timedelta=dt.timedelta(days=1)):
    cur = start
    while cur.date() <= stop.date():
        yield cur
        cur += step




def save_storage(storage: TaskStorage):
    with open('tasks.json', 'w') as f:
        f.write(storage.model_dump_json())
        print('Saved')

def backup_storage(storage: TaskStorage):
    with open('tasks.json.bak', 'w') as f:
        f.write(storage.model_dump_json())
        print('Backed up')


def display_timeline(lshift=0, start_date: dt.datetime | None =None, end_date: dt.datetime | None =None):
    today = dt.datetime.now()
    if start_date is None:
        start_date = today.replace(day=1)
    if end_date is None:
        end_date = today.replace(day=lom(today))

    def make_up(x, style, offset=1):
        return style + digits.get(x, x) + ' '*offset + colorama.Fore.RESET + colorama.Back.RESET
    row0 = " "*lshift
    row1 = " "*lshift
    row2 = " "*lshift

    for i, date in enumerate(date_range(start_date, end_date)):
        weekend = date.weekday() >= 5
        style = colorama.Fore.RED if weekend else ''
        x = f"{date.day: >2}"
        weekday = week_days[date.weekday()]
        row1 += make_up(x[0], style)
        row2 += make_up(x[1], style)

        style = colorama.Fore.BLACK
        if weekend:
            style += colorama.Back.LIGHTRED_EX if (i+1) % 2 else colorama.Back.RED
        else:
            style += colorama.Back.WHITE if (i+1) % 2 else colorama.Back.LIGHTBLACK_EX
        row0 += make_up(weekday, style, offset=0)


    print(row1)
    print(row2)
    print(row0)


class TaskViewer:
    def __init__(self, storage: TaskStorage) -> None:
        self.storage = storage
        self.tasks = storage.tasks


    def display_tasks_on_timeline(self, filtering: Callable[[Task], bool] = lambda x: True):
        task_size = 20
        timeline_start = dt.datetime.today()
        timeline_end = timeline_start + dt.timedelta(days=30)
        display_timeline(lshift=task_size, start_date=timeline_start, end_date=timeline_end)
        for i, task in enumerate(self.tasks):
            if not filtering(task):
                continue
            s, e = task.start.date(), task.end.date()
            if task.done:
                print(colorama.Style.DIM, end="")
            task_id_and_title = str(i).rjust(2) + ' ' + task.title
            print(task_id_and_title[:task_size].ljust(task_size)+\
                "".join(["╶╴" if day.date() < s or day.date() > e else "▇▇" for day in date_range(timeline_start, timeline_end)])\
                + colorama.Style.RESET_ALL)
        print(colorama.Fore.RESET, end="")


class TaskStorageAware:
    with open('tasks.json', 'r') as f:
        storage = TaskStorage.model_validate_json(f.read())


class TaskViewAware:
    viewer = TaskViewer(TaskStorageAware.storage)


class ContextManager:
    """
    Contains environment variables for commands.
    """
    filter = None
    tag = None

class CommandManager(TaskStorageAware, TaskViewAware):
    commands: Dict[str, Callable] = dict()
    aliases: Dict[str, str] = dict()

    @classmethod
    def set_alias(cls, alias: str, command: str):
        cls.aliases[alias] = command

class CommandDecorator:
    def __init__(self) -> None:
        pass

    def __call__(self, func: Callable):
        # print(func.__name__, 'added as command')
        CommandManager.commands[func.__name__] = func
        return func

    def alias(self, alias: str):
        def decorator(func: Callable):
            CommandManager.aliases[alias] = func.__name__
            return func
        return decorator

def tokentize(cmd: str):
    return cmd.split(' ')

def parser(cmd:str):
    command, *args = tokentize(cmd)
    if command in CommandManager.aliases:
        alias = CommandManager.aliases[command]
        command, *args = tokentize(alias) + args

    function = CommandManager.commands.get(command)
    if function is None:
        print(f"Command {command} not found")
        return

    function(*args, storage=CommandManager.storage, viewer=CommandManager.viewer)
    save_storage(CommandManager.storage)

command = CommandDecorator()
