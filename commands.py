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
