from gantt import command, Task, backup_storage


@command
def list_tasks(*args, storage, viewer):
    viewer.display_tasks_on_timeline()


@command
def reshedule_task(*args, storage, viewer):
    match args:
        case task_id, *args if task_id.isdigit():
            task_id = int(task_id)
            task = viewer.tasks[task_id]
            task.process(args)

@command
def new_task(*args, storage, viewer):
    match args:
        case title:
            import datetime as dt
            today = dt.datetime.now()
            start = today
            end = today
            storage.tasks.insert(0, Task(start=start, end=end, title=' '.join(title)))


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
def hide_done(*args, storage, viewer):
    match args:
        case []:
            viewer.hide_done()


@command
def view_all(*args, storage, viewer):
    match args:
        case []:
            viewer.reset_filter()
