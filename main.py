from typing import List
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
    tags: List[str] = pydantic.Field(default_factory=list)

    def __str__(self):
        return f"{self.title}: {self.start.strftime(DATE_FORMAT)} - {self.end.strftime(DATE_FORMAT)}, {'DONE' if self.done else 'NOT DONE'}\n[{' '.join(self.tags)}]"

    def process(self, args: list[str]):
        match args:
            case []:
                print(self)
            case a, b if a.isdigit() and b.isdigit():
                a, b = int(a), int(b)
                self.start = self.start.replace(day=a)
                self.end = self.end.replace(day=b)
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

    def make_up(x, style):
        return style + digits.get(x, ' ') + ' ' + colorama.Fore.RESET + colorama.Back.RESET

    row0 = " "*lshift
    row1 = " "*lshift
    row2 = " "*lshift

    for i in date_range(start_date, end_date):
        style = colorama.Back.GREEN + colorama.Fore.BLACK if int(i.day) % 2 else colorama.Back.BLACK
        style += colorama.Fore.RED if i.weekday() >=5 else ''
        x = f"{i.day: >2}"
        row1 += make_up(x[0], style)
        row2 += make_up(x[1], style)
    print(row1)
    print(row2)
    # print(, end='')


class TaskViewer:
    def __init__(self, storage: TaskStorage) -> None:
        self.storage = storage
        self.tasks = storage.tasks

    def hide_done(self):
        self.tasks = list(filter(lambda x: not x.done, self.tasks))

    def reset_filter(self):
        self.tasks = self.storage.tasks


    def display_tasks_on_timeline(self):
        task_size = 20
        timeline_start = dt.datetime.today()
        timeline_end = timeline_start + dt.timedelta(days=30)
        display_timeline(lshift=task_size, start_date=timeline_start, end_date=timeline_end)
        for i, task in enumerate(self.tasks):
            # if i % 2 == 0:
            #     print(colorama.Fore.GREEN, end="")
            # else:
            #     print(colorama.Fore.WHITE, end="")

            s, e = task.start.date(), task.end.date()
            if task.done:
                print(colorama.Style.DIM, end="")
            task_id_and_title = str(i).rjust(2) + ' ' + task.title
            print(task_id_and_title[:task_size].ljust(task_size)+\
                "".join(["╶╴" if day.date() < s or day.date() > e else "▇▇" for day in date_range(timeline_start, timeline_end)])\
                + colorama.Style.RESET_ALL)
        print(colorama.Fore.RESET, end="")


with open('tasks.json', 'r') as f:
    storage = TaskStorage.model_validate_json(f.read())

# storage.tasks = [random_task() for _ in range(11)]
viewer = TaskViewer(storage)

viewer.display_tasks_on_timeline()
while True:
    cmd = input('>>>').split(' ')
    match cmd:
        case task_id, *args if task_id.isdigit():
            task_id = int(task_id)
            task = viewer.tasks[task_id]
            task.process(args)
        case 'new' | 'нов', *title:
            today = dt.datetime.now()
            start = today
            end = today
            storage.tasks.insert(0, Task(start=start, end=end, title=' '.join(title)))
        case 'done', task_id if task_id.isdigit():
            task_id = int(task_id)
            viewer.tasks[task_id].done = not viewer.tasks[task_id].done
        case 'rename', task_id, *text if task_id.isdigit():
            viewer.tasks[int(task_id)].title = ' '.join(text)
        case 'mv', task_id, new_place if task_id.isdigit() and new_place.isdigit():
            task = storage.tasks.pop(int(task_id))
            print('MOVE:', task)
            storage.tasks.insert(int(new_place), task)
        case 'rm', task_id if task_id.isdigit():
            task_id = int(task_id)
            option = input('REMOVE: ' + str(storage.tasks[task_id]) + '?')
            if option in ['y', 'yes', 'Y', 'YES']:
                storage.tasks.pop(task_id)
        case 'backup',:
            backup_storage(storage)

        case 'hidedone',:
            viewer.hide_done()
        case 'viewall',:
            viewer.reset_filter()
        case 'ls', :
            viewer.display_tasks_on_timeline()
        case 'exit',:
            break
        case _:
            print('Unknown command')
            # raise ShellException('Unknown command')
    save_storage(storage)


with open('tasks.json', 'w') as f:
    f.write(storage.model_dump_json())
