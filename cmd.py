from cli import cli
from storage import TaskStorage


@cli.command
def ls(storage: TaskStorage, *args):
    '''
    Usage: ls [FILTER]
    List tasks that match the filter.
    '''
    default_filter = 'not task.done'
    filter = ' '.join(args) or default_filter
    result = '\n'.join(str(task) for task in storage.tasks if eval(filter, {'task': task}))
    print(result)
