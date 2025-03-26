from gantt import command, Task, backup_storage, TaskViewer, TaskStorage, CommandManager
import datetime as dt



@command
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


@command
def ls(*args, storage, viewer: TaskViewer):
    show_all = '-a' in args
    if show_all:
        viewer.display_tasks_on_timeline()
    else:
        viewer.display_tasks_on_timeline(filtering=lambda x: not x.done)


@command
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


@command
def reshedule_task(*args, storage, viewer):
    match args:
        case task_id, *args if task_id.isdigit():
            task_id = int(task_id)
            task = viewer.tasks[task_id]
            task.process(args)

@command
def new_task(*args, storage, viewer):
    title = 'No name'
    today = dt.datetime.now()
    start = today
    end = today
    match args:
        case []:
            while (title := input('Title: ')) != '':
                storage.tasks.insert(0, Task(start=start, end=end, title=title))
        case _:
            title = ' '.join(args)
            storage.tasks.insert(0, Task(start=start, end=end, title=title))



@command
def mark_done(*args, storage, viewer):
    match args:
        case task_id, if task_id.isdigit():
            task_id = int(task_id)
            viewer.tasks[task_id].done = not viewer.tasks[task_id].done


@command
def rename_task(*args, storage, viewer):
    match args:
        case task_id, *text if task_id.isdigit():
            viewer.tasks[int(task_id)].title = ' '.join(text)


@command
def move_task(*args, storage, viewer):
    match args:
        case task_id, new_place if task_id.isdigit() and new_place.isdigit():
            task = storage.tasks.pop(int(task_id))
            print('MOVE:', task)
            storage.tasks.insert(int(new_place), task)


@command
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
                    tag = tag.removeprefix('-')
                    if tag in task.tags:
                        task.tags.remove(tag)
                    else:
                        print(f"Tag {tag} not found in task {task_id}")
                else:
                    tag = tag.removeprefix('+')
                    task.tags.add(tag)


@command
def alias(*args, storage, viewer: TaskViewer):
    match args:
        case []:
            print(CommandManager.aliases)
        case alias, *command:
            CommandManager.set_alias(alias, ' '.join(command))
            print(f"Alias {alias} set to {command}")

@command
def tags(*args, storage, viewer: TaskViewer):
    '''Display all tags and their frequency'''
    tags = dict()
    for task in viewer.tasks:
        for tag in task.tags:
            tags[tag] = tags.get(tag, 0) + 1
    for tag, freq in sorted(tags.items(), key=lambda x: x[1], reverse=True):
        print(f"{tag: <12}:{freq}")
