import colorama
import datetime as dt

from storage import TaskStorageAware, Task, date_range


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


def draw_timeline(lshift: int, start_date: dt.date, end_date: dt.date):
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

def display_tasks(tasks: list[Task], filter_func):
    id_column_width = 3
    title_column_width = 20

    timeline_start = dt.date.today()
    timeline_end = timeline_start + dt.timedelta(days=30)
    draw_timeline(lshift=id_column_width + title_column_width, start_date=timeline_start, end_date=timeline_end)
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
