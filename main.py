from ast import LShift
import datetime as dt
import colorama


def lom(date):
    # last date of month
    date = date.replace(day=1)
    date = date.replace(month=date.month+1)
    date = date - dt.timedelta(days=1)
    return date.day

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


class Task:
    start: dt.datetime
    end: dt.datetime
    title: str

    def __init__(self, start, end, title):
        self.start = start
        self.end = end
        self.title = title

    def __str__(self):
        return f"Task({self.start}, {self.end}, {self.title})"

    @classmethod
    def random_task(cls, title="Random Task"):
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

        return cls(start_time, end_time, title + ' ' +str(random.randint(10000, 99999)))


tasks = [Task.random_task() for _ in range(11)]


def display_timeline(lshift=0):
    columns = [f"{i: >2}" for i in range(1, lom(dt.datetime.now())+1)]
    print(" "*lshift + " ".join(map(lambda x: digits.get(x[0], ' '), columns)))
    print(" "*lshift +" ".join(map(lambda x: digits.get(x[1], ' '), columns)))



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
        print(task.title[:task_size].ljust(task_size)+"".join(["╶╴" if i < start_day or i > end_day else "▇▇" for i in range(1, lom(dt.datetime.now())+1)]))
        i += 1

display_tasks_on_timeline(tasks)
