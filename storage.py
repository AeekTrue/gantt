import pydantic
import datetime as dt
from loguru import logger
from config import DATE_FORMAT

def lom(date):
    # last date of month
    date = date.replace(day=1)
    date = date.replace(month=date.month+1)
    date = date - dt.timedelta(days=1)
    return date.day

def date_range(start: dt.date,  stop: dt.date, step: dt.timedelta=dt.timedelta(days=1)):
    cur = start
    while cur <= stop:
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

    def save_storage(self):
        with open('tasks.json', 'w') as f:
            f.write(self.model_dump_json())
            logger.info('Saved')


    def backup_storage(self):
        with open('tasks.json.bak', 'w') as f:
            f.write(self.model_dump_json())
            print('Backed up')


class TaskStorageAware:
    with open('tasks.json', 'r') as f:
        storage = TaskStorage.model_validate_json(f.read())
