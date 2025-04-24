from cli import cli, display_tasks
from storage import TaskStorage


@cli.command
def ls(storage: TaskStorage, *args):
    '''
    Usage: ls [FILTER]
    List tasks that match the filter.
    '''
    default_filter = 'not task.done'
    filter = ' '.join(args) or default_filter
    display_tasks(storage.tasks, lambda task: eval(filter, {'task': task}))
