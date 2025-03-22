from gantt import command, Task, backup_storage, TaskViewer
import datetime as dt


@command.alias('show')
def show_task(*args, storage, viewer):
    match args:
        case task_id, if task_id.isdigit():
            task_id = int(task_id)
            if 0 <= task_id < len(viewer.tasks):
                print(viewer.tasks[task_id])
            else:
                print(f"Task with ID {task_id} not found.")
        case _:
            print("Usage: show <task_id>")


@command.alias('ls')
def list_tasks(*args, storage, viewer: TaskViewer):
    show_all = '-a' in args
    if show_all:
        viewer.display_tasks_on_timeline()
    else:
        viewer.display_tasks_on_timeline(filtering=lambda x: not x.done)


@command.alias('filter')
def filter_tasks(*args, storage, viewer):
    if not args:
        print("Usage: filter <filter_expression>")
        return

    filter_expr = ' '.join(args)
    try:
        environment = {
            'td': lambda x: dt.datetime.today() + dt.timedelta(days=x),
            'today': dt.date.today().day,
        }

        filter_wrapper = lambda task, tags, start, end, done: eval(f"{filter_expr}",
            environment, {'task': task, 'tags': tags, 'start': start, 'end': end, 'done': done})
        filter_func = lambda task: filter_wrapper(task, task.tags, task.start.day, task.end.day, task.done)

        # Apply the filter and display filtered tasks
        viewer.display_tasks_on_timeline(filtering=filter_func)
    except Exception as e:
        print(f"Error in filter expression: {e}")
        print("Example: 'filter not task.done' or 'filter \"project\" in task.title'")


@command.alias('edit')
def reshedule_task(*args, storage, viewer):
    match args:
        case task_id, *args if task_id.isdigit():
            task_id = int(task_id)
            task = viewer.tasks[task_id]
            task.process(args)

@command.alias('new')
def new_task(*args, storage, viewer):
    title = 'No name'
    match args:
        case []:
            title = input('Title: ')
        case _:
            title = ' '.join(args)

    today = dt.datetime.now()
    start = today
    end = today
    storage.tasks.insert(0, Task(start=start, end=end, title=title))


@command.alias('done')
def mark_done(*args, storage, viewer):
    match args:
        case task_id, if task_id.isdigit():
            task_id = int(task_id)
            viewer.tasks[task_id].done = not viewer.tasks[task_id].done


@command.alias('rename')
def rename_task(*args, storage, viewer):
    match args:
        case task_id, *text if task_id.isdigit():
            viewer.tasks[int(task_id)].title = ' '.join(text)


@command.alias('mv')
def move_task(*args, storage, viewer):
    match args:
        case task_id, new_place if task_id.isdigit() and new_place.isdigit():
            task = storage.tasks.pop(int(task_id))
            print('MOVE:', task)
            storage.tasks.insert(int(new_place), task)


@command.alias('rm')
def remove_task(*args, storage, viewer):
    match args:
        case task_id, if task_id.isdigit():
            task_id = int(task_id)
            option = input('REMOVE: ' + str(storage.tasks[task_id]) + '?')
            if option in ['y', 'yes', 'Y', 'YES']:
                storage.tasks.pop(task_id)


@command
def backup(*args, storage, viewer):
    match args:
        case []:
            backup_storage(storage)

@command
def mark(*args: str, storage, viewer: TaskViewer):
    match args:
        case task_id, *tags if task_id.isdigit():
            task_id = int(task_id)
            task = viewer.tasks[task_id]
            for tag in tags:
                if tag.startswith('-'):
                    tags.remove(tag)
                else:
                    tag = tag.removeprefix('+')
                    task.tags.add(tag)
