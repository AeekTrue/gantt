from typing import List
import datetime as dt
import colorama
import pydantic
import json

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


class Task(pydantic.BaseModel):
    start: dt.datetime
    end: dt.datetime
    title: str

    def __str__(self):
        return f"{self.title}: {self.start.strftime(DATE_FORMAT)} - {self.end.strftime(DATE_FORMAT)}"

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


class Storage(pydantic.BaseModel):
    tasks: list[Task]


def display_timeline(lshift=0):
    def make_up(x, style):
        return style + digits.get(x, ' ') + ' ' + colorama.Fore.RESET + colorama.Back.RESET

    row1 = " "*lshift
    row2 = " "*lshift

    for i in range(1, lom(dt.datetime.now())+1):
        style = colorama.Back.GREEN + colorama.Fore.BLACK if int(i) % 2 else colorama.Back.BLACK
        x = f"{i: >2}"
        row1 += make_up(x[0], style)
        row2 += make_up(x[1], style)
    print(row1)
    print(row2)
    # print(, end='')


def display_tasks_on_timeline(tasks):
    task_size = 20
    display_timeline(lshift=task_size)
    i = 0
    for task in tasks:
        if i % 2 == 0:
            print(colorama.Fore.GREEN, end="")
        else:
            print(colorama.Fore.WHITE, end="")

        start_day = task.start.day
        end_day = task.end.day
        task_id_and_title = str(i).rjust(2) + ' ' + task.title
        print(task_id_and_title[:task_size].ljust(task_size)+"".join(["╶╴" if i < start_day or i > end_day else "▇▇" for i in range(1, lom(dt.datetime.now())+1)]))
        i += 1
    print(colorama.Fore.RESET, end="")


with open('tasks.json', 'r') as f:
    storage = Storage.model_validate_json(f.read())

# storage.tasks = [random_task() for _ in range(11)]
tasks = storage.tasks

display_tasks_on_timeline(tasks)
while True:
    cmd = input('>>>').split(' ')
    match cmd:
        case task_id, *args if task_id.isdigit():
            task_id = int(task_id)
            task = tasks[task_id]
            task.process(args)
        case 'new', title, start, end if start.isdigit() and end.isdigit():
            today = dt.datetime.now()
            start = today.replace(day=int(start))
            end = today.replace(day=int(end))
            tasks.append(Task(start=start, end=end, title=title))
        case 'rename', task_id, *text if task_id.isdigit():
            tasks[int(task_id)].title = ' '.join(text)
        case 'move', task_id, new_place if task_id.isdigit() and new_place.isdigit():
            tasks.insert(int(new_place), tasks.pop(int(task_id)))
        case 'show', :
            display_tasks_on_timeline(tasks)
        case 'save',:
            with open('tasks.json', 'w') as f:
                f.write(storage.model_dump_json())
            print('Saved')
        case 'exit',:
            break
        case _:
            print('Unknown command')
            # raise ShellException('Unknown command')

with open('tasks.json', 'w') as f:
    f.write(storage.model_dump_json())
