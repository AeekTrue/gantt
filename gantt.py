from typing import Dict, List, Any, Callable
import datetime as dt
import colorama
import pydantic
import json

from pydantic.types import Tag

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

class Task(pydantic.BaseModel):
    start: dt.datetime
    end: dt.datetime
    title: str
    done: bool = False
    tags: set[str] = pydantic.Field(default_factory=set)

    def __str__(self):
        return f"{self.title}: {self.start.strftime(DATE_FORMAT)} - {self.end.strftime(DATE_FORMAT)}, {'DONE' if self.done else 'NOT DONE'}\n[{' '.join(self.tags)}]"

    def process(self, args: list[str]):
        match args:
            case []:
                print(self)
            case a, b if a.isdigit() and b.isdigit():
                a, b = int(a), int(b)
                today = dt.datetime.now()
                new_start = today.replace(day=a)
                if new_start.date() < dt.date.today():
                    new_start = new_start.replace(month=self.start.month+1)
                self.start = new_start
                new_end = today.replace(day=b)
                if new_end.date() < dt.date.today():
                    new_end = new_end.replace(month=self.end.month+1)
                self.end = new_end
            case _:
                print('Unknown args')
                # raise ShellException()



def random_task(title="Random Task"):
    # Get current month's first and last day
    now = dt.datetime.now()
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day = now.replace(day=lom(now), hour=23, minute=59, second=59, microsecond=999999)

    # Generate random start time within the current month
    import random
    start_timestamp = random.uniform(first_day.timestamp(), last_day.timestamp())
    start_time = dt.datetime.fromtimestamp(start_timestamp)

    # Generate random end time after start time but within the current month
    end_timestamp = random.uniform(start_time.timestamp(), last_day.timestamp())
    end_time = dt.datetime.fromtimestamp(end_timestamp)

    return Task(start=start_time, end=end_time, title=title + ' ' +str(random.randint(10000, 99999)))


class TaskStorage(pydantic.BaseModel):
    tasks: list[Task]


def save_storage(storage: TaskStorage):
    with open('tasks.json', 'w') as f:
        f.write(storage.model_dump_json())
        print('Saved')

def backup_storage(storage: TaskStorage):
    with open('tasks.json.bak', 'w') as f:
        f.write(storage.model_dump_json())
        print('Backed up')


def display_timeline(lshift=0, start_date: dt.datetime=None, end_date: dt.datetime=None):
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
            style += colorama.Back.LIGHTRED_EX if (date.weekday()) % 2 else colorama.Back.RED
        else:
            style += colorama.Back.WHITE if (date.weekday()) % 2 else colorama.Back.LIGHTBLACK_EX
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


class CommandManager(TaskStorageAware, TaskViewAware):
    commands: Dict[str, Callable] = dict()


class CommandDecorator:
    def __init__(self) -> None:
        pass

    def __call__(self, func: Callable):
        # print(func.__name__, 'added as command')
        CommandManager.commands[func.__name__] = func
        return func

    def alias(self, alt_name:str):
        def inner(func: Callable):
            CommandManager.commands[alt_name] = func

            return func
        return inner

def parser(cmd:str):
    command, *args = cmd.split(' ')
    if command not in CommandManager.commands:
        print('Unknown command')
        return
    function = CommandManager.commands[command]
    function(*args, storage=CommandManager.storage, viewer=CommandManager.viewer)
    save_storage(CommandManager.storage)

command = CommandDecorator()
