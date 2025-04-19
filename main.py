#!python
import os
os.environ['LOGURU_AUTOINIT'] = 'False'
os.environ['LOGURU_LEVEL'] = 'TRACE'

from loguru import logger
from repl import Repl


def main():
    app_dir = os.path.dirname(os.path.realpath(__file__))
    log_file = os.path.join(app_dir, 'log.txt')
    storage_file = os.path.join(app_dir, 'tasks.json')
    backup_file = os.path.join(app_dir, 'tasks.json.bak')

    logger.add(log_file)
    logger.info(f"Log file: {log_file}")
    repl = Repl()
    repl.interact()

if __name__ == "__main__":
    main()
