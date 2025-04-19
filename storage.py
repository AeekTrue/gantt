import pydantic
import datetime as dt

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
